import factory
from faker import Faker

from hct_mis_api.apps.geo.models import Area, AreaType

faker = Faker()


def create_fake_multipolygon():
    from django.contrib.gis.geos import MultiPolygon, Polygon

    p1 = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
    p2 = Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))

    return MultiPolygon(p1, p2)


class AreaTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = AreaType

    name = None
    country = None
    area_level = None
    parent = None


class AreaFactory(factory.DjangoModelFactory):
    class Meta:
        model = Area

    name = factory.LazyFunction(faker.city)
    parent = None
    p_code = None
    area_type = None
    geom = factory.LazyFunction(create_fake_multipolygon)
    point = None
