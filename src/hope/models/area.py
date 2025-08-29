from typing import Any

from django.db import models
from django.db.models import JSONField, Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from natural_keys import NaturalKeyModel

from hope.models.area_type import AreaType
from hope.models.country import UpgradeModel, ValidityManager
from hope.models.utils import TimeStampedUUIDModel


class Area(NaturalKeyModel, MPTTModel, UpgradeModel, TimeStampedUUIDModel):
    name = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self",
        blank=True,
        db_index=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Parent"),
    )
    p_code = models.CharField(max_length=32, blank=True, null=True, verbose_name="P Code")
    area_type = models.ForeignKey(AreaType, on_delete=models.CASCADE)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = ValidityManager()

    class Meta:
        app_label = "geo"
        verbose_name_plural = "Areas"
        ordering = ("name",)
        constraints = [
            UniqueConstraint(
                fields=["p_code"],
                name="unique_area_p_code_not_blank",
                condition=~Q(p_code=""),
            )
        ]
        permissions = (("import_areas", "Can import areas"),)

    class MPTTMeta:
        order_insertion_by = ("name", "p_code")

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_admin_areas_as_choices(
        cls,
        admin_level: int | None = None,
        business_area_slug: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if admin_level:
            params["area_type__area_level"] = admin_level

        if business_area_slug:
            params["area_type__country__business_areas__slug"] = business_area_slug

        queryset = cls.objects.filter(**params).order_by("name")
        return [
            {
                "label": {"English(EN)": f"{area.name}-{area.p_code}"},
                "value": area.p_code,
            }
            for area in queryset
        ]
