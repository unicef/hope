import factory
from faker import Faker
import random
from factory import fuzzy
from hct_mis_api.apps.geo.models import Area, AreaType, Country

faker = Faker()


def create_fake_multipolygon():
    from django.contrib.gis.geos import MultiPolygon, Polygon

    p1 = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
    p2 = Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))

    return MultiPolygon(p1, p2)


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('name', 'short_name', 'iso_code2', 'iso_code3', 'iso_num')

    name = "Afghanistan"
    short_name = "Afghanistan"
    iso_code2 = "AF"
    iso_code3 = "AFG"
    iso_num = "0004"
    parent = None


class AreaTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = AreaType
        django_get_or_create = ('name', 'country', 'area_level')

    name = factory.LazyFunction(faker.domain_word)
    country = factory.SubFactory(CountryFactory)
    area_level = fuzzy.FuzzyChoice([1, 2, 3, 4])
    parent = None


class AreaFactory(factory.DjangoModelFactory):
    class Meta:
        model = Area
        django_get_or_create = ('name', 'p_code', 'area_type')

    name = factory.LazyFunction(faker.city)
    parent = None
    p_code = faker.bothify(text='AF@@@@@@')
    area_type = factory.SubFactory(AreaTypeFactory)
    geom = factory.LazyFunction(create_fake_multipolygon)
    point = None


