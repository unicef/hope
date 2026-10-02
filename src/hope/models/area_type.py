from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from natural_keys import NaturalKeyModel

from hope.models.country import Country, UpgradeModel, ValidityManager
from hope.models.utils import LongNameIndex, TimeStampedUUIDModel


class AreaTypeManager(ValidityManager):
    def get_by_natural_key(self, name: str, country: str, area_level: int) -> "AreaType":
        return self.get(name=name, country__iso_code3=country, area_level=area_level)


class AreaType(NaturalKeyModel, MPTTModel, UpgradeModel, TimeStampedUUIDModel):
    name = models.CharField(max_length=255, db_collation="und-ci-det")
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    area_level = models.PositiveIntegerField(default=1)
    parent = TreeForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent"),
    )
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = AreaTypeManager()

    class Meta:
        app_label = "geo"
        verbose_name_plural = "Area Types"
        unique_together = ("country", "area_level", "name")
        ordering = ("name",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="geo_areatype_created_at_7ce454f0"),
            LongNameIndex(fields=["updated_at"], name="geo_areatype_updated_at_6c355284"),
            LongNameIndex(fields=["name"], name="geo_areatype_name_b20b6ba6"),
            # django-mptt appends this index on its own unless Meta declares it. It is in the migration
            # state only: migrated databases do not have it.
            models.Index(fields=["tree_id", "lft"], name="geo_areatype_tree_id_lft_idx"),
        ]

    def __str__(self) -> str:
        return self.name
