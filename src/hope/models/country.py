# - Country
# - AreaType
# - Area
from typing import Any

from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.querysets import TreeQuerySet
from natural_keys import NaturalKeyModel

from hope.models.currency import Currency
from hope.models.utils import TimeStampedUUIDModel


class ValidityQuerySet(TreeQuerySet):
    def active(self, *args: Any, **kwargs: Any) -> "ValidityQuerySet":
        return super().filter(valid_until__isnull=True).filter(*args, **kwargs)


class ValidityManager(TreeManager):
    _queryset_class = ValidityQuerySet


class UpgradeModel(models.Model):
    original_id = models.UUIDField(blank=True, null=True)

    class Meta:
        abstract = True


class CountryManager(ValidityManager):
    def get_by_natural_key(self, iso_code3: str) -> "Country":
        return self.get(iso_code3=iso_code3)


class Country(NaturalKeyModel, MPTTModel, UpgradeModel, TimeStampedUUIDModel):
    name = models.CharField(
        max_length=255, db_index=True, db_collation="und-ci-det", help_text=_("The full name of the country")
    )
    short_name = models.CharField(
        max_length=255, db_index=True, db_collation="und-ci-det", help_text=_("The short name of the country")
    )
    iso_code2 = models.CharField(max_length=2, unique=True, help_text=_("The ISO 3166-1 alpha-2 code"))
    iso_code3 = models.CharField(max_length=3, unique=True, help_text=_("The ISO 3166-1 alpha-3 code"))
    iso_num = models.CharField(max_length=4, unique=True, help_text=_("The ISO 3166-1 numeric code"))
    currency = models.ForeignKey(
        Currency,
        verbose_name=_("Currency"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="countries",
        help_text=_("The currency used in this country"),
    )
    parent = TreeForeignKey(
        "self",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
        help_text=_("The parent area in the hierarchy"),
    )
    valid_from = models.DateTimeField(
        blank=True, null=True, auto_now_add=True, help_text=_("The date from which this record is valid")
    )
    valid_until = models.DateTimeField(blank=True, null=True, help_text=_("The date until which this record is valid"))
    extras = JSONField(default=dict, blank=True, help_text=_("Extra data for this country"))

    objects = CountryManager()

    class Meta:
        app_label = "geo"
        verbose_name_plural = "Countries"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_choices(cls) -> list[dict[str, Any]]:
        queryset = cls.objects.all().order_by("name")
        return [
            {
                "label": {"English(EN)": country.name},
                "value": country.iso_code3,
            }
            for country in queryset
        ]
