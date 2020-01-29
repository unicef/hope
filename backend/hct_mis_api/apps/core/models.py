from decimal import Decimal

import mptt
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from model_utils.models import UUIDModel
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel


class Country(UUIDModel):
    name = models.CharField(max_length=100)
    country_short_code = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )
    long_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name



class BusinessArea(UUIDModel):
    """
    BusinessArea (EPRP called Workspace, also synonym was
    emergency/country) model.
    It's used for drop down menu in top bar in the UI. Many times
    workspace is associated with only one country.
    """
    title = models.CharField(max_length=255)
    workspace_code = models.CharField(
        max_length=8,
        unique=True
    )
    countries = models.ManyToManyField(Country, related_name='workspaces')
    business_area_code = models.CharField(
        max_length=10,
        null=True, blank=True
    )
    latitude = models.DecimalField(
        null=True, blank=True,
        max_digits=8, decimal_places=5,
        validators=[
            MinValueValidator(Decimal(-90)),
            MaxValueValidator(Decimal(90))
        ]
    )
    longitude = models.DecimalField(
        null=True, blank=True,
        max_digits=8, decimal_places=5,
        validators=[
            MinValueValidator(Decimal(-180)),
            MaxValueValidator(Decimal(180))
        ]
    )
    initial_zoom = models.IntegerField(default=8)


    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def locations(self):
        """
        Returns a list of locations that belong to countries associated with
        this workspace.
        """
        result = self.countries.all().values_list(
            'gateway_types__locations').distinct()
        pks = []
        [pks.extend(filter(lambda x: x is not None, part)) for part in result]
        return Location.objects.filter(pk__in=pks)

    @property
    def can_import_ocha_response_plans(self):
        return any([
            c.details for c in self.countries.all()
        ])

class GatewayType(UUIDModel):
    """
    Represents an Admin Type in location-related models.
    """

    name = models.CharField(max_length=64, unique=True, verbose_name=_('Name'))
    display_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Display Name'))
    admin_level = models.PositiveSmallIntegerField(verbose_name=_('Admin Level'))

    country = models.ForeignKey(Country, related_name="gateway_types", on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']
        verbose_name = 'Location type'
        unique_together = ('country', 'admin_level')

    def __str__(self):
        return '{} - {}'.format(self.country, self.name)


class LocationManager(TreeManager):

    def get_queryset(self):
        return super(LocationManager, self).get_queryset().order_by('title').select_related('gateway')

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


    title = models.CharField(max_length=255)

    gateway = models.ForeignKey(
        GatewayType, verbose_name='Location Type', related_name='locations',  on_delete=models.CASCADE,
    )
    carto_db_table = models.ForeignKey(
        'core.CartoDBTable',
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
            MaxValueValidator(Decimal(90))
        ]
    )
    longitude = models.DecimalField(
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=5,
        validators=[
            MinValueValidator(Decimal(-180)),
            MaxValueValidator(Decimal(180))
        ]
    )
    p_code = models.CharField(max_length=32, blank=True, null=True, verbose_name='Postal Code')

    parent = TreeForeignKey(
        'self',
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.CASCADE
    )

    geom = models.MultiPolygonField(null=True, blank=True)
    point = models.PointField(null=True, blank=True)
    objects = LocationManager()

    class Meta:
        unique_together = ('title', 'p_code')
        ordering = ['title']

    def __str__(self):
        if self.p_code:
            return '{} ({} {})'.format(
                self.title,
                self.gateway.name,
                "{}: {}".format(
                    'CERD' if self.gateway.name == 'School' else 'PCode', self.p_code or ''
                ))

        return self.title

    @property
    def geo_point(self):
        return self.point if self.point else self.geom.point_on_surface if self.geom else ""

    @property
    def point_lat_long(self):
        return "Lat: {}, Long: {}".format(
            self.point.y,
            self.point.x
        )


class CartoDBTable(MPTTModel):
    """
    Represents a table in CartoDB, it is used to imports locations
    related models:
        core.GatewayType: 'gateway'
        core.Country: 'country'
    """

    domain = models.CharField(max_length=254, verbose_name=_('Domain'))
    table_name = models.CharField(max_length=254, verbose_name=_('Table Name'))
    display_name = models.CharField(max_length=254, default='', blank=True, verbose_name=_('Display Name'))
    location_type = models.ForeignKey(
        GatewayType, verbose_name=_('Location Type'),
        on_delete=models.CASCADE,
    )
    name_col = models.CharField(max_length=254, default='name', verbose_name=_('Name Column'))
    pcode_col = models.CharField(max_length=254, default='pcode', verbose_name=_('Pcode Column'))
    parent_code_col = models.CharField(max_length=254, default='', blank=True, verbose_name=_('Parent Code Column'))
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', db_index=True,
        verbose_name=_('Parent'),
        on_delete=models.CASCADE,
    )

    country = models.ForeignKey(Country, related_name="carto_db_tables",
        on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'CartoDB tables'

    def __str__(self):
        return self.table_name


mptt.register(Location, order_insertion_by=['title'])
mptt.register(CartoDBTable, order_insertion_by=['table_name'])
