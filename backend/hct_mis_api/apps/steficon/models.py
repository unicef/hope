from typing import Any, Callable, Dict, List, Tuple, Type

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, CICharField
from django.core.validators import ProhibitNullCharactersValidator
from django.db import models
from django.db.models import JSONField
from django.db.transaction import atomic
from django.forms import model_to_dict
from django.utils.functional import cached_property

from concurrency.fields import AutoIncVersionField

from .config import SAFETY_HIGH, SAFETY_NONE, SAFETY_STANDARD
from .interpreters import Interpreter, interpreters, mapping
from .result import Result
from .validators import DoubleSpaceValidator, StartEndSpaceValidator

MONITORED_FIELDS = ("name", "enabled", "deprecated", "language", "definition")


class RuleManager(models.Manager):
    pass


class Rule(models.Model):
    LANGUAGES = [[a.label.lower(), a.label] for a in interpreters]
    version = AutoIncVersionField()
    name = CICharField(
        max_length=100,
        unique=True,
        validators=[
            ProhibitNullCharactersValidator(),
            StartEndSpaceValidator,
            DoubleSpaceValidator,
        ],
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

    flags = JSONField(default=dict, blank=True)

    objects = RuleManager()

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_security = self.security

    def get_flag(self, name, default=None):
        return self.flags.get(name, default)

    def as_dict(self) -> Dict:
        return model_to_dict(self, MONITORED_FIELDS)

    def clean(self):
        if self.pk:
            self.security = self.__original_security

    def clean_definition(self):
        self.interpreter.validate()

    def delete(self, using=None, keep_parents=False):
        self.enabled = False
        self.save()

    def get_changes(self) -> Tuple[Dict, List]:
        prev = self.latest_commit
        if prev:
            data1 = prev.after
            data2 = self.as_dict()
        else:
            data1 = {}
            data2 = self.as_dict()

        diff = set(data1.items()).symmetric_difference(data2.items())
        return data1, list(dict(diff).keys())

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None) -> None:
        if "individual_data_needed" not in self.flags:
            self.flags["individual_data_needed"] = False
        with atomic():
            super().save(force_insert, force_update, using, update_fields)
            self.commit()

    def commit(self, is_release=False, force=False) -> "RuleCommit":
        stored, changes = self.get_changes()
        release = None
        values = {
            "enabled": self.enabled,
            "definition": self.definition,
            "is_release": is_release,
            "updated_by": self.updated_by,
            "before": stored,
            "after": self.as_dict(),
            "affected_fields": changes,
        }
        if changes:
            release = RuleCommit.objects.create(rule=self, version=self.version, **values)
        elif force:
            release, __ = RuleCommit.objects.update_or_create(rule=self, version=self.version, defaults=values)
        if is_release:
            self.history.exclude(pk=release.pk).update(deprecated=True)
        return release

    def release(self):
        if self.deprecated or not self.enabled:
            raise ValueError("Cannot release disabled/deprecated rules")
        commit = self.history.filter(version=self.version).first()
        if commit and not commit.is_release:
            commit.is_release = True
            commit.save()
            self.history.exclude(pk=commit.pk).update(deprecated=True)
        else:
            commit = self.commit(is_release=True, force=True)
        return commit

    @property
    def latest(self):
        try:
            return self.history.filter(is_release=True).order_by("-version").first()
        except RuleCommit.DoesNotExist:
            pass

    @property
    def latest_commit(self):
        try:
            return self.history.order_by("version").last()
        except RuleCommit.DoesNotExist:
            pass

    @property
    def last_changes(self):
        try:
            return {
                "fields": self.latest_commit.affected_fields,
                "before": self.latest_commit.before,
                "after": self.latest_commit.after,
            }
        except RuleCommit.DoesNotExist:
            pass

    @cached_property
    def interpreter(self):
        func: Type[Interpreter] = mapping[self.language]
        return func(self.definition)

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
    before = JSONField(help_text="The record before change", editable=False, default=dict)
    after = JSONField(help_text="The record after apply changes", editable=False, default=dict)

    class Meta:
        verbose_name = "RuleCommit"
        verbose_name_plural = "Rule Commits"
        unique_together = (
            "rule",
            "version",
        )
        ordering = ("-version",)
        get_latest_by = "-version"

    def __str__(self):
        value = f"{self.rule} #{self.id}"
        if not self.enabled:
            value = f"{value} (Disabled)"
        elif self.deprecated:
            value = f"{value} (Deprecated)"
        elif not self.is_release:
            value = f"{value} (Draft)"
        return value

    @cached_property
    def prev(self):
        return self.rule.history.order_by("-version").filter(id__lt=self.id).first()

    @cached_property
    def next(self):
        return self.rule.history.order_by("version").filter(id__gt=self.id).first()

    @atomic
    def revert(self, fields=MONITORED_FIELDS):
        for field in fields:
            setattr(self.rule, field, self.after[field])
        self.rule.save()

    @cached_property
    def interpreter(self):
        func: Callable = mapping[self.language]
        return func(self.definition)

    def execute(self, context) -> Any:
        return self.interpreter.execute(context)

    def release(self):
        if self.deprecated or not self.enabled:
            raise ValueError("Cannot release disabled/deprecated rules")
        if not self.is_release:
            self.is_release = True
            self.save()
            self.rule.history.exclude(pk=self.pk).update(deprecated=True)
        return self
