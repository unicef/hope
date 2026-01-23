"""Geo-related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import Area, AreaType, Country


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("name", "short_name", "iso_code2", "iso_code3", "iso_num")

    name = factory.Sequence(lambda n: f"Country {n}")
    short_name = factory.LazyAttribute(lambda o: o.name)
    iso_code2 = factory.Sequence(lambda n: f"{chr(65 + (n % 26))}{chr(65 + ((n // 26) % 26))}")  # AA, BA, CA, etc.
    iso_code3 = factory.Sequence(lambda n: f"{chr(65 + (n % 26))}{chr(65 + ((n // 26) % 26))}A")  # AAA, BAA, etc.
    iso_num = factory.Sequence(lambda n: f"{n:04d}")


class AreaTypeFactory(DjangoModelFactory):
    class Meta:
        model = AreaType
        django_get_or_create = ("name", "country", "area_level")

    name = factory.Sequence(lambda n: f"Area Type {n}")
    country = factory.SubFactory(CountryFactory)
    area_level = 1


class AreaFactory(DjangoModelFactory):
    class Meta:
        model = Area

    name = factory.Sequence(lambda n: f"Area {n}")
    p_code = factory.Sequence(lambda n: f"PC{n:06d}")
    area_type = factory.SubFactory(AreaTypeFactory)
