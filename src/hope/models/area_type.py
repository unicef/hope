from django.contrib.postgres.fields import CICharField
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from natural_keys import NaturalKeyModel

from hope.models.country import UpgradeModel, Country, ValidityManager
from hope.models.utils import TimeStampedUUIDModel


class AreaType(NaturalKeyModel, MPTTModel, UpgradeModel, TimeStampedUUIDModel):
    name = CICharField(max_length=255, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    area_level = models.PositiveIntegerField(default=1)
    parent = TreeForeignKey(
        "self",
        blank=True,
        db_index=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent"),
    )
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = ValidityManager()

    class Meta:
        app_label = "geo"
        verbose_name_plural = "Area Types"
        unique_together = ("country", "area_level", "name")

    def __str__(self) -> str:
        return self.name
