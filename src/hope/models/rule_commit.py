from typing import Any, Callable, Optional

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField, QuerySet
from django.db.transaction import atomic
from django.utils.functional import cached_property

from hope.apps.steficon.interpreters import mapping
from hope.models.rule import Rule

MONITORED_FIELDS = ("name", "enabled", "deprecated", "language", "definition")


class RuleCommit(models.Model):
    timestamp = models.DateTimeField(auto_now=True)

    version = models.IntegerField()
    rule = models.ForeignKey(Rule, null=True, related_name="history", on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", null=True, on_delete=models.PROTECT)
    definition = models.TextField(blank=True, default="result.value=0")
    is_release = models.BooleanField(default=False)
    enabled = models.BooleanField(default=False)
    deprecated = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default=Rule.LANGUAGES[0][0], choices=Rule.LANGUAGES)  # type: ignore # FIXME

    affected_fields = ArrayField(models.CharField(max_length=100))
    before = JSONField(help_text="The record before change", editable=False, default=dict)
    after = JSONField(help_text="The record after apply changes", editable=False, default=dict)

    class Meta:
        app_label = "steficon"
        verbose_name = "RuleCommit"
        verbose_name_plural = "Rule Commits"
        unique_together = (
            "rule",
            "version",
        )
        ordering = ("-version",)
        get_latest_by = "-version"

    def __str__(self) -> str:
        value = f"{self.rule} #{self.id}"
        if not self.enabled:
            value = f"{value} (Disabled)"
        elif self.deprecated:
            value = f"{value} (Deprecated)"
        elif not self.is_release:
            value = f"{value} (Draft)"
        return value

    @cached_property
    def prev(self) -> QuerySet | None:
        return self.rule.history.order_by("-version").filter(id__lt=self.id).first()

    @cached_property
    def next(self) -> QuerySet | None:
        return self.rule.history.order_by("version").filter(id__gt=self.id).first()

    @atomic
    def revert(self, fields: tuple[str, str, str, str, str] = MONITORED_FIELDS) -> None:
        for field in fields:
            setattr(self.rule, field, self.after[field])
        self.rule.save()

    @cached_property
    def interpreter(self) -> Any:
        func: Callable = mapping[self.language]
        return func(self.definition)

    def execute(self, context: dict) -> Any:
        return self.interpreter.execute(context)

    def release(self) -> Optional["RuleCommit"]:
        if self.deprecated or not self.enabled:
            raise ValueError("Cannot release disabled/deprecated rules")
        if not self.is_release:
            self.is_release = True
            self.save()
            self.rule.history.exclude(pk=self.pk).update(deprecated=True)
        return self
