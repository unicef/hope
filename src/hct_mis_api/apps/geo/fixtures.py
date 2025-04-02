import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.geo.models import Area, AreaType, Country

faker = Faker()


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
