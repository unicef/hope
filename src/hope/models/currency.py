import logging
from typing import Any

from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CurrencyQuerySet(models.QuerySet):
    def active(self) -> "CurrencyQuerySet":
        return self.filter(active=True)


class CurrencyManager(models.Manager.from_queryset(CurrencyQuerySet)):
    def get_active_by_code(self, code: str) -> "Currency":
        currency = self.get_active_by_code_or_none(code)
        if currency is None:
            raise self.model.DoesNotExist(f"No active currency with code {code!r}.")
        return currency

    def get_active_by_code_or_none(self, code: str) -> "Currency | None":
        """Return the active row whose ``code`` is ``code``, else the active row whose ``vision_code`` is.

        The ``vision_code`` fallback is a transitional alias: after a redenomination moves the new
        row's ``code`` onto the ISO code, clients may still send its former code, which is kept as
        ``vision_code``. ``code`` goes first, so an ISO code never resolves through another row's alias,
        and a deactivated ``code`` stays rejected even when an active row carries it as ``vision_code``.
        """
        currency = self.filter(code=code, active=True).first()
        if currency is not None:
            return currency
        # TODO(<ticket>): everything below is the vision_code alias; when the transition period ends,
        # replace it with `return None`.
        if self.filter(code=code).exists():
            return None
        alias = self.filter(vision_code=code, active=True).first()
        if alias is not None:
            logger.warning("Currency %r resolved through the vision_code alias of %r.", code, alias.code)
        return alias


class Currency(models.Model):
    """A currency, in one denomination.

    ``code`` is unique only among ``active=True`` rows: a redenomination keeps the old row as
    ``active=False`` under the same ``code``, so ``vision_code`` is what identifies a row.
    Resolve user-supplied codes through ``hope.apps.core.currency_resolution``, never a bare
    ``code=`` lookup.
    """

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

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.vision_code:
            self.vision_code = self.code
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if not self.vision_code:
            self.vision_code = self.code
