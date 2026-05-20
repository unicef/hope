from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    code = models.CharField(max_length=5, unique=True, db_index=True, help_text=_("The currency code (e.g. USD, EUR)"))
    name = models.CharField(max_length=255, help_text=_("The full name of the currency"))
    is_crypto = models.BooleanField(default=False, help_text=_("Whether this is a cryptocurrency (e.g. USDC)"))
    vision_code = models.CharField(
        max_length=5, blank=True, default="", help_text=_("The vision system code for this currency")
    )
    active = models.BooleanField(default=True, help_text=_("Whether this currency is active"))
    number_of_decimals = models.SmallIntegerField(default=2, help_text=_("Number of decimal places for this currency"))

    class Meta:
        app_label = "core"
        ordering = ["code"]
        verbose_name_plural = "currencies"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.vision_code:
            self.vision_code = self.code
        super().save(*args, **kwargs)
