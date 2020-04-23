import factory
from factory import fuzzy
from faker import Faker

from core.countries import COUNTRIES_ALPHA2_CODE, COUNTRIES_ALPHA2_CODE_DICT
from core.models import AdminArea, AdminAreaType

COUNTRY_CODES_LIST = [x[0] for x in COUNTRIES_ALPHA2_CODE]
COUNTRY_NAMES_LIST = [x[1] for x in COUNTRIES_ALPHA2_CODE]

faker = Faker()


def create_fake_multipolygon():
    from django.contrib.gis.geos import Polygon, MultiPolygon

    p1 = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
    p2 = Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))

    return MultiPolygon(p1, p2)


class AdminAreaTypeFactory(factory.DjangoModelFactory):
    """
    Arguments:
        country {Country} -- Country ORM objects
    Ex) AdminAreaTypeFactory(country=country1)
    """

    class Meta:
        model = AdminAreaType
        django_get_or_create = ("name",)

    name = None
    display_name = factory.LazyAttribute(lambda o: o.name)
    admin_level = None
    business_area = None


class AdminAreaFactory(factory.DjangoModelFactory):
    """
    Arguments:
        admin_area_type {AdminAreaType} -- AdminAreaType ORM objects
    """

    class Meta:
        model = AdminArea
        django_get_or_create = (
            "title",
            "admin_area_type",
        )

    title = factory.LazyFunction(faker.city)
    # We are going to fill admin_area_type type manually
    admin_area_type = None
    parent = None
    geom = factory.LazyFunction(create_fake_multipolygon)
    point = None
