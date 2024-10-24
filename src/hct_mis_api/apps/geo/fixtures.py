from django.contrib.gis.geos import MultiPolygon, Polygon

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.geo.models import Area, AreaType, Country

faker = Faker()


def create_fake_multipolygon() -> MultiPolygon:
    p1 = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
    p2 = Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))

    return MultiPolygon(p1, p2)


class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("name", "short_name", "iso_code2", "iso_code3", "iso_num")

    name = "Afghanistan"
    short_name = "Afghanistan"
    iso_code2 = "AF"
    iso_code3 = "AFG"
    iso_num = "0004"
    parent = None


class AreaTypeFactory(DjangoModelFactory):
    class Meta:
        model = AreaType
        django_get_or_create = ("name", "country", "area_level")

    name = factory.LazyFunction(faker.domain_word)
    country = factory.SubFactory(CountryFactory)
    area_level = fuzzy.FuzzyChoice([1, 2, 3, 4])
    parent = None


class AreaFactory(DjangoModelFactory):
    class Meta:
        model = Area
        django_get_or_create = ("p_code",)

    name = factory.LazyFunction(faker.city)
    parent = None
    p_code = factory.LazyFunction(lambda: faker.bothify(text="AF@@@@@@"))
    area_type = factory.SubFactory(AreaTypeFactory)
    geom = factory.LazyFunction(create_fake_multipolygon)
    point = None
