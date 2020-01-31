from decimal import Decimal

import mptt
import pycountry
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from model_utils.models import UUIDModel
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from core.coutries import COUNTRY_NAME_TO_ALPHA2_CODE
from core.utils import unique_slugify
from utils.models import TimeStampedUUIDModel


class Country(TimeStampedUUIDModel):
    """
    Represents a country which has many offices and sections.
    Taken from https://github.com/unicef/etools/blob/master/EquiTrack/users/models.py
    on Sep. 14, 2017.
    """

    name = models.CharField(max_length=100)
    country_short_code = models.CharField(max_length=10, null=True, blank=True)
    long_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

    @property
    def details(self):
        """
        Tries to retrieve a usable country reference
        :return: pycountry Country object or None
        """
        lookup = None

        if not self.country_short_code:
            lookup = {
                "alpha_2": COUNTRY_NAME_TO_ALPHA2_CODE.get(self.name, None)
            }
        elif len(self.country_short_code) == 3:
            lookup = {"alpha_3": self.country_short_code}
        elif len(self.country_short_code) == 2:
            lookup = {"alpha_2": self.country_short_code}

        if lookup:
            try:
                return pycountry.countries.get(**lookup)
            except KeyError:
                pass


class BusinessArea(TimeStampedUUIDModel):
    """
    BusinessArea (EPRP called Workspace, also synonym was
    country/region) model.
    It's used for drop down menu in top bar in the UI. Many times
    BusinessArea means country.
    region_name is a short code for distinct business areas
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


class GatewayType(TimeStampedUUIDModel):
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

    country = models.ForeignKey(
        Country, related_name="gateway_types", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Location type"
        unique_together = ("country", "admin_level")

    def __str__(self):
        return "{} - {}".format(self.country, self.name)


class LocationManager(TreeManager):
    def get_queryset(self):
        return (
            super(LocationManager, self)
            .get_queryset()
            .order_by("title")
            .select_related("gateway")
        )


class Location(MPTTModel):
    """
    Location model define place where agents are working.
    The background of the location can be:
    Country > Region > City > District/Point.
    Either a point or geospatial object.
    pcode should be unique.
    related models:
        indicator.Reportable (ForeignKey): "reportable"
        core.Location (ForeignKey): "self"
        core.GatewayType: "gateway"
    """

    class Meta:
        unique_together = ("title", "p_code")
        ordering = ["title"]

    objects = LocationManager()

    title = models.CharField(max_length=255)
    business_area = models.ForeignKey(
        "BusinessArea",
        on_delete=models.SET_NULL,
        related_name="locations",
        null=True,
    )
    gateway = models.ForeignKey(
        GatewayType,
        verbose_name="Location Type",
        related_name="locations",
        on_delete=models.CASCADE,
    )
    carto_db_table = models.ForeignKey(
        "core.CartoDBTable",
        related_name="locations",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    latitude = models.DecimalField(
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=5,
        validators=[
            MinValueValidator(Decimal(-90)),
            MaxValueValidator(Decimal(90)),
        ],
    )
    longitude = models.DecimalField(
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=5,
        validators=[
            MinValueValidator(Decimal(-180)),
            MaxValueValidator(Decimal(180)),
        ],
    )
    p_code = models.CharField(
        max_length=32, blank=True, null=True, verbose_name="Postal Code"
    )
    parent = TreeForeignKey(
        "self",
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        on_delete=models.CASCADE,
    )
    geom = models.MultiPolygonField(null=True, blank=True)
    point = models.PointField(null=True, blank=True)

    def __str__(self):
        if self.p_code:
            return "{} ({} {})".format(
                self.title,
                self.gateway.name,
                "{}: {}".format(
                    "CERD" if self.gateway.name == "School" else "PCode",
                    self.p_code or "",
                ),
            )

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


class CartoDBTable(MPTTModel):
    """
    Represents a table in CartoDB, it is used to imports locations
    related models:
        core.GatewayType: 'gateway'
        core.Country: 'country'
    """

    class Meta:
        verbose_name_plural = "CartoDB tables"

    domain = models.CharField(max_length=254, verbose_name=_("Domain"))
    table_name = models.CharField(max_length=254, verbose_name=_("Table Name"))
    display_name = models.CharField(
        max_length=254, default="", blank=True, verbose_name=_("Display Name")
    )
    location_type = models.ForeignKey(
        GatewayType, verbose_name=_("Location Type"), on_delete=models.CASCADE,
    )
    name_col = models.CharField(
        max_length=254, default="name", verbose_name=_("Name Column")
    )
    pcode_col = models.CharField(
        max_length=254, default="pcode", verbose_name=_("Pcode Column")
    )
    parent_code_col = models.CharField(
        max_length=254,
        default="",
        blank=True,
        verbose_name=_("Parent Code Column"),
    )
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        verbose_name=_("Parent"),
        on_delete=models.CASCADE,
    )
    country = models.ForeignKey(
        Country, related_name="carto_db_tables", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.table_name


mptt.register(Location, order_insertion_by=["title"])
mptt.register(CartoDBTable, order_insertion_by=["table_name"])
