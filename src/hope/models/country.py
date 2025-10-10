# - Country
# - AreaType
# - Area
from typing import Any

from django.contrib.postgres.fields import CICharField
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.querysets import TreeQuerySet
from natural_keys import NaturalKeyModel

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


class Country(NaturalKeyModel, MPTTModel, UpgradeModel, TimeStampedUUIDModel):
    name = CICharField(max_length=255, db_index=True)
    short_name = CICharField(max_length=255, db_index=True)
    iso_code2 = models.CharField(max_length=2, unique=True)
    iso_code3 = models.CharField(max_length=3, unique=True)
    iso_num = models.CharField(max_length=4, unique=True)
    parent = TreeForeignKey(
        "self",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = ValidityManager()

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
