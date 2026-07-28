from typing import Any

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _


class CurrencyQuerySet(models.QuerySet):
    def active(self) -> "CurrencyQuerySet":
        return self.filter(active=True)

    def resolve_code(self, code: str) -> "Currency":
        return self.get(code=code, active=True)

    def resolve_code_or_none(self, code: str) -> "Currency | None":
        return self.filter(code=code, active=True).first()


CurrencyManager = models.Manager.from_queryset(CurrencyQuerySet)


class Currency(models.Model):
    code = models.CharField(
        max_length=5,
        db_index=True,
        help_text=_("The currency code following the ISO 4217 standard (e.g. USD, EUR)"),
    )
    name = models.CharField(max_length=255, help_text=_("The full name of the currency"))
    is_crypto = models.BooleanField(default=False, help_text=_("Whether this is a cryptocurrency (e.g. USDC)"))
    vision_code = models.CharField(
        max_length=5,
        blank=True,
        default="",
        help_text=_("The vision system code for this currency"),
    )
    active = models.BooleanField(default=True, help_text=_("Whether this currency is active"))
    number_of_decimals = models.SmallIntegerField(default=2, help_text=_("Number of decimal places for this currency"))

    objects = CurrencyManager()

    class Meta:
        app_label = "core"
        ordering = ["code", "vision_code"]
        verbose_name_plural = "currencies"
        constraints = [
            models.UniqueConstraint(Lower("code"), condition=models.Q(active=True), name="unique_code_active"),
            models.UniqueConstraint(Lower("vision_code"), name="unique_vision_code"),
        ]

    def __str__(self) -> str:
        if self.vision_code and self.vision_code != self.code:
            return f"{self.code} ({self.vision_code}) - {self.name}"
        return f"{self.code} - {self.name}"

    def clean(self) -> None:
        super().clean()
        if not self.vision_code:
            self.vision_code = self.code

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.vision_code:
            self.vision_code = self.code
        super().save(*args, **kwargs)
