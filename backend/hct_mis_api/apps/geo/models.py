# - Country
# - AreaType
# - Area
from typing import Any, Dict, List

from django.contrib.gis.db import models
from django.contrib.postgres.fields import CICharField
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.utils.models import TimeStampedUUIDModel
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.querysets import TreeQuerySet


class ValidityQuerySet(TreeQuerySet):
    def active(self, *args, **kwargs):
        return super().filter(valid_until__isnull=True).filter(*args, **kwargs)


class ValidityManager(TreeManager):
    _queryset_class = ValidityQuerySet


class UpgradeModel(models.Model):
    original_id = models.UUIDField(blank=True, null=True)

    class Meta:
        abstract = True


class Country(MPTTModel, UpgradeModel, TimeStampedUUIDModel):
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
        verbose_name_plural = "Countries"
        ordering = ("name",)

    def __str__(self):
        return self.name

    @classmethod
    def get_choices(cls) -> List[Dict[str, Any]]:
        queryset = cls.objects.all().order_by("name")
        return [
            {
                "label": {"English(EN)": country.name},
                "value": country.iso_code3,
            }
            for country in queryset
        ]


class AreaType(MPTTModel, UpgradeModel, TimeStampedUUIDModel):
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
        verbose_name_plural = "Area Types"
        unique_together = ("country", "area_level", "name")

    def __str__(self):
        return self.name


class Area(MPTTModel, UpgradeModel, TimeStampedUUIDModel):
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

    geom = models.MultiPolygonField(null=True, blank=True)
    point = models.PointField(null=True, blank=True)

    valid_from = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    valid_until = models.DateTimeField(blank=True, null=True)
    extras = JSONField(default=dict, blank=True)

    objects = ValidityManager()

    class Meta:
        verbose_name_plural = "Areas"
        unique_together = ("name", "p_code")

    def __str__(self):
        return self.name

    @classmethod
    def get_admin_areas_as_choices(cls, admin_level: int = None, business_area_slug: str = None):
        params = {}
        if admin_level:
            params["area_type__area_level"] = admin_level

        if business_area_slug:
            # slug may look like: `central-african-republic`
            # after replacing `-` with ` `
            # it should match case-insensitively `Central African Republic`
            # also, short_name does not contain dashes
            # so it won't fail for e.g. Timor-Leste
            # because short_name for it is just `Timor Leste`
            unslugged_business_area_slug = business_area_slug.replace("-", " ")
            params["area_type__country__short_name__iexact"] = unslugged_business_area_slug
            # still, this approach smells fishy because we're matching business area slug with country name
            # it's a good approximation for now but it should be improved somehow

        queryset = cls.objects.filter(**params).order_by("name")
        return [
            {
                "label": {"English(EN)": f"{area.name}-{area.p_code}"},
                "value": area.p_code,
            }
            for area in queryset
        ]
