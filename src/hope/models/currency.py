from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    code = models.CharField(max_length=5, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    is_crypto = models.BooleanField(default=False, help_text=_("Whether this is a cryptocurrency (e.g. USDC)"))

    class Meta:
        app_label = "core"
        ordering = ["code"]
        verbose_name_plural = "currencies"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
