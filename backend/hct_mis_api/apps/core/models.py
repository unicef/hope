from decimal import Decimal

import mptt
import pycountry
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from model_utils.models import SoftDeletableModel
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from core.utils import unique_slugify
from utils.models import TimeStampedUUIDModel, SoftDeletionTreeModel


class BusinessArea(TimeStampedUUIDModel):
    """
    BusinessArea (EPRP called Workspace, also synonym was
    country/region) model.
    It's used for drop down menu in top bar in the UI. Many times
    BusinessArea means country.
    region_name is a short code for distinct business arease
    <BusinessArea>
        <BUSINESS_AREA_CODE>0120</BUSINESS_AREA_CODE>
        <BUSINESS_AREA_NAME>Algeria</BUSINESS_AREA_NAME>
        <BUSINESS_AREA_LONG_NAME>THE PEOPLE'S DEMOCRATIC REPUBLIC OF ALGERIA</BUSINESS_AREA_LONG_NAME>
        <REGION_CODE>59</REGION_CODE>
        <REGION_NAME>MENAR</REGION_NAME>
    </BusinessArea>
    """

    code = models.CharField(max_length=10,)
    name = models.CharField(max_length=255)
    long_name = models.CharField(max_length=255)
    region_code = models.CharField(max_length=8)
    region_name = models.CharField(max_length=8)
    kobo_token = models.CharField(max_length=255, null=True, blank=True)

    slug = models.CharField(max_length=250, unique=True, db_index=True,)

    def save(self, *args, **kwargs):
        unique_slugify(self, self.name, slug_field_name="slug")
        super(BusinessArea, self).save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def can_import_ocha_response_plans(self):
        return any([c.details for c in self.countries.all()])


class AdminAreaType(TimeStampedUUIDModel):
    """
    Represents an Admin Type in location-related models.
    """

    name = models.CharField(max_length=64, unique=True, verbose_name=_("Name"))
    display_name = models.CharField(
        max_length=64, blank=True, null=True, verbose_name=_("Display Name")
    )
    admin_level = models.PositiveSmallIntegerField(
        verbose_name=_("Admin Level")
    )

    business_area = models.ForeignKey(
        "BusinessArea",
        on_delete=models.SET_NULL,
        related_name="admin_area_types",
        null=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "AdminAreaType type"
        unique_together = ("business_area", "admin_level")

    def __str__(self):
        return "{} - {}".format(self.business_area, self.name)


class AdminAreaManager(TreeManager):
    def get_queryset(self):
        return (
            super(AdminAreaManager, self)
            .get_queryset()
            .order_by("title")
            .select_related("admin_area_type")
        )


class AdminArea(MPTTModel, TimeStampedUUIDModel):
    """
    AdminArea model define place where agents are working.
    The background of the location can be:
    BussinesAreaa > State > Province > City > District/Point.
    Either a point or geospatial object.
    related models:
        indicator.Reportable (ForeignKey): "reportable"
        core.AdminArea (ForeignKey): "self"
        core.AdminAreaType: "type of admin area state/city"
    """

    class Meta:
        unique_together = ("title", "admin_area_type")
        ordering = ["title"]

    objects = AdminAreaManager()

    title = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )

    admin_area_type = models.ForeignKey(
        "AdminAreaType", on_delete=models.CASCADE, related_name="locations"
    )

    geom = MultiPolygonField(null=True, blank=True)
    point = PointField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def geo_point(self):
        return (
            self.point
            if self.point
            else self.geom.point_on_surface
            if self.geom
            else ""
        )

    @property
    def point_lat_long(self):
        return "Lat: {}, Long: {}".format(self.point.y, self.point.x)


class FlexibleAttribute(SoftDeletableModel, TimeStampedUUIDModel):
    TYPE_CHOICE = Choices(
        ("STRING", _("String")),
        ("IMAGE", _("Image")),
        ("INTEGER", _("Integer")),
        ("DECIMAL", _("Decimal")),
        ("SELECT_ONE", _("Select One")),
        ("SELECT_MANY", _("Select Many")),
        ("DATETIME", _("Datetime")),
        ("GEOPOINT", _("Geopoint")),
    )
    ASSOCIATED_WITH_CHOICES = (
        (0, _("Household")),
        (1, _("Individual")),
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICE)
    name = models.CharField(max_length=255, unique=True)
    required = models.BooleanField(default=False)
    label = JSONField(default=dict)
    hint = JSONField(default=dict)
    group = models.ForeignKey(
        "core.FlexibleAttributeGroup",
        on_delete=models.CASCADE,
        related_name="flex_attributes",
        null=True,
    )
    associated_with = models.SmallIntegerField(choices=ASSOCIATED_WITH_CHOICES)
    history = AuditlogHistoryField(pk_indexable=False)

    def __str__(self):
        return f"type: {self.type}, name: {self.name}"


class FlexibleAttributeGroup(SoftDeletionTreeModel):
    name = models.CharField(max_length=255, unique=True)
    label = JSONField(default=dict)
    required = models.BooleanField(default=False)
    repeatable = models.BooleanField(default=False)
    parent = TreeForeignKey(
        "self",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )
    history = AuditlogHistoryField(pk_indexable=False)

    def __str__(self):
        return f"name: {self.name}"


class FlexibleAttributeChoice(SoftDeletableModel, TimeStampedUUIDModel):
    class Meta:
        unique_together = ["list_name", "name"]

    list_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    label = JSONField(default=dict)
    admin = models.CharField(max_length=255)
    flex_attributes = models.ManyToManyField(
        "core.FlexibleAttribute", related_name="choices"
    )
    history = AuditlogHistoryField(pk_indexable=False)

    def __str__(self):
        return f"list name: {self.list_name}, name: {self.name}"


mptt.register(AdminArea, order_insertion_by=["title"])
mptt.register(FlexibleAttributeGroup, order_insertion_by=["name"])

auditlog.register(FlexibleAttributeChoice)
auditlog.register(FlexibleAttributeGroup)
auditlog.register(FlexibleAttribute)
