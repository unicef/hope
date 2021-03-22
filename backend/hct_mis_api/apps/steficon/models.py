from concurrency.fields import AutoIncVersionField
from django.contrib.postgres.fields import JSONField, ArrayField, CICharField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.transaction import atomic
from django.core.validators import ProhibitNullCharactersValidator

from django.forms import model_to_dict
from django.utils.deconstruct import deconstructible
from django.utils.functional import cached_property
from hct_mis_api.apps.steficon.interpreters import interpreters, mapping
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel
from hct_mis_api.apps.utils.validators import StartEndSpaceValidator, DoubleSpaceValidator

MONITORED_FIELDS = ["name", "enabled", "deprecated", "language", "definition"]


class Rule(TimeStampedUUIDModel):
    LANGUAGES = [[a.label.lower(), a.label] for a in interpreters]
    version = AutoIncVersionField()
    name = CICharField(
        max_length=100,
        unique=True,
        validators=[ProhibitNullCharactersValidator(), StartEndSpaceValidator, DoubleSpaceValidator],
    )
    definition = models.TextField(blank=True, default="score.value=0")
    enabled = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default=LANGUAGES[0][0], choices=LANGUAGES)
    created_by = models.ForeignKey("account.User", related_name="+", null=True, on_delete=models.PROTECT)
    updated_by = models.ForeignKey("account.User", related_name="+", null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def as_dict(self):
        return model_to_dict(self, MONITORED_FIELDS)

    def get_changes(self):
        current = Rule.objects.get(pk=self.pk)
        data1 = current.as_dict()
        data2 = self.as_dict()
        diff = set(data1.items()).symmetric_difference(data2.items())
        return data1, list(dict(diff).keys())

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.created_at:
            stored, changes = self.get_changes()
            if changes and (stored["enabled"] or self.enabled):
                RuleCommit.objects.create(
                    rule=self,
                    version=self.version,
                    before=stored,
                    after=self.as_dict(),
                    affected_fields=changes,
                    updated_by=self.updated_by,
                )
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.enabled = False
        self.save()

    def used_by(self):
        return self.target_populations.all()

    @cached_property
    def interpreter(self):
        return mapping[self.language](self.definition)

    def execute(self, **kwargs):
        return self.interpreter.execute(**kwargs)


class RuleCommit(models.Model):
    timestamp = models.DateTimeField(auto_now=True)

    version = models.IntegerField()
    rule = models.ForeignKey(Rule, null=True, related_name="history", on_delete=models.SET_NULL)
    updated_by = models.ForeignKey("account.User", related_name="+", null=True, on_delete=models.PROTECT)

    affected_fields = ArrayField(models.CharField(max_length=100))
    before = JSONField(help_text="The record before change", editable=False)
    after = JSONField(help_text="The record after apply changes", editable=False)

    class Meta:
        verbose_name = "Rule (History)"
        verbose_name_plural = "Rules (History)"
        ordering = ("-timestamp",)
        get_latest_by = "-timestamp"

    def __str__(self):
        return f"Commit #{self.id} of {self.rule}"

    @atomic
    def revert(self, fields=None):
        if fields is None:
            fields = MONITORED_FIELDS
        for field in fields:
            setattr(self.rule, field, self.before[field])
        self.rule.save()
