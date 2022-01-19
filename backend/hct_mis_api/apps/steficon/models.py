from django.conf import settings
from django.contrib.postgres.fields import ArrayField, CICharField, JSONField
from django.core.validators import ProhibitNullCharactersValidator
from django.db import models
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.forms import model_to_dict
from django.utils.functional import cached_property

from concurrency.fields import AutoIncVersionField

from ..utils.models import TimeStampedUUIDModel
from .config import SAFETY_HIGH, SAFETY_NONE, SAFETY_STANDARD
from .exception import RuleError
from .interpreters import interpreters, mapping
from .result import Result
from .validators import DoubleSpaceValidator, StartEndSpaceValidator

MONITORED_FIELDS = ("name", "enabled", "deprecated", "language", "definition")


class RuleManager(models.Manager):
    pass


class Rule(models.Model):
    LANGUAGES = [[a.label.lower(), a.label] for a in interpreters]
    # code = models.AutoField(primary_key=True, editable=False)
    version = AutoIncVersionField()
    name = CICharField(
        max_length=100,
        unique=True,
        validators=[ProhibitNullCharactersValidator(), StartEndSpaceValidator, DoubleSpaceValidator],
    )
    definition = models.TextField(blank=True, default="result.value=0")
    description = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default=LANGUAGES[0][0], choices=LANGUAGES)
    security = models.IntegerField(
        choices=(
            (SAFETY_NONE, "Low"),
            (SAFETY_STANDARD, "Medium"),
            (SAFETY_HIGH, "High"),
        ),
        default=SAFETY_STANDARD,
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", null=True, on_delete=models.PROTECT)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", null=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = RuleManager()

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_security = self.security

    def as_dict(self):
        return model_to_dict(self, MONITORED_FIELDS)

    def get_changes(self):
        current = Rule.objects.get(pk=self.pk)
        data1 = current.as_dict()
        data2 = self.as_dict()
        diff = set(data1.items()).symmetric_difference(data2.items())
        return data1, list(dict(diff).keys())

    def clean(self):
        if self.pk:
            self.security = self.__original_security

    def clean_definition(self):
        self.interpreter.validate()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        with atomic():
            if self.pk:
                self.commit()
            super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.enabled = False
        self.save()

    def used_by(self):
        raise NotImplementedError

    def commit(self, is_release=False, force=False):
        if self.pk:
            stored, changes = self.get_changes()
        else:
            stored, changes = {}, []
        if force or changes or not self.pk:
            return RuleCommit.objects.create(
                rule=self,
                enabled=self.enabled,
                definition=self.definition,
                version=self.version,
                is_release=is_release,
                updated_by=self.updated_by,
                before=stored,
                after=self.as_dict(),
                affected_fields=changes,
            )

    def release(self):
        if self.deprecated or not self.enabled:
            raise ValueError("Cannot release disabled/deprecated rules")
        self.commit(is_release=True)

    @property
    def latest(self):
        try:
            return self.history.filter(is_release=True).latest()
        except RuleCommit.DoesNotExist:
            pass

    @cached_property
    def interpreter(self):
        return mapping[self.language](self.definition)

    def execute(self, context=None, only_release=True, only_enabled=True) -> Result:
        if self.pk:
            qs = self.history
            if only_release:
                qs = qs.filter(is_release=True)

            if only_enabled:
                qs = qs.filter(enabled=True)
            latest = qs.order_by("-version").first()
        else:
            latest = self
        with atomic():
            if latest:
                return latest.interpreter.execute(context)
            else:
                raise ValueError("No Released Rules found")


class RuleCommit(models.Model):
    timestamp = models.DateTimeField(auto_now=True)

    version = models.IntegerField()
    rule = models.ForeignKey(Rule, null=True, related_name="history", on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", null=True, on_delete=models.PROTECT)
    definition = models.TextField(blank=True, default="result.value=0")
    is_release = models.BooleanField(default=False)
    enabled = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default=Rule.LANGUAGES[0][0], choices=Rule.LANGUAGES)

    affected_fields = ArrayField(models.CharField(max_length=100))
    before = JSONField(help_text="The record before change", editable=False)
    after = JSONField(help_text="The record after apply changes", editable=False)

    class Meta:
        verbose_name = "Rule (History)"
        verbose_name_plural = "Rules (History)"
        ordering = ("-timestamp",)
        get_latest_by = "-timestamp"

    def __str__(self):
        value = f"{self.rule} #{self.id}"
        if not self.is_release:
            return f"{value} (Draft)"
        return value

    @atomic
    def revert(self, fields=MONITORED_FIELDS):
        for field in fields:
            setattr(self.rule, field, self.before[field])
        self.rule.save()

    @cached_property
    def interpreter(self):
        return mapping[self.language](self.definition)

    def execute(self, context):
        return self.interpreter.execute(context)
