"""Geo-related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import Area, AreaType, Country


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = (
            "name",
            "short_name",
            "iso_code2",
            "iso_code3",
            "iso_num",
        )

    name = "Afghanistan"
    short_name = "Afghanistan"
    iso_code2 = "AF"
    iso_code3 = "AFG"
    iso_num = "0004"


class AreaTypeFactory(DjangoModelFactory):
    class Meta:
        model = AreaType
        django_get_or_create = ("name", "country", "area_level")

    name = factory.Sequence(lambda n: f"Area Type {n}")
    country = factory.SubFactory(CountryFactory)
    area_level = 2


class AreaFactory(DjangoModelFactory):
    class Meta:
        model = Area
        django_get_or_create = ("p_code",)

    name = factory.Sequence(lambda n: f"Area {n}")
    p_code = factory.Sequence(lambda n: f"AF{n:06d}")
    area_type = factory.SubFactory(AreaTypeFactory)
