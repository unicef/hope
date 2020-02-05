import factory
from factory import fuzzy
from faker import Faker

from core.countries import COUNTRIES_ALPHA2_CODE, COUNTRIES_ALPHA2_CODE_DICT
from core.models import Location, CartoDBTable, GatewayType, Country

COUNTRY_CODES_LIST = [x[0] for x in COUNTRIES_ALPHA2_CODE]
COUNTRY_NAMES_LIST = [x[1] for x in COUNTRIES_ALPHA2_CODE]

faker = Faker()


def create_fake_multipolygon():
    from django.contrib.gis.geos import Polygon, MultiPolygon

    p1 = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
    p2 = Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))

    return MultiPolygon(p1, p2)


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Country

    country_short_code = fuzzy.FuzzyChoice(COUNTRY_CODES_LIST)
    name = factory.LazyAttribute(
        lambda o: COUNTRIES_ALPHA2_CODE_DICT[o.country_short_code]
    )
    long_name = factory.LazyAttribute(
        lambda o: COUNTRIES_ALPHA2_CODE_DICT[o.country_short_code]
    )


class GatewayTypeFactory(factory.DjangoModelFactory):
    """
    Arguments:
        country {Country} -- Country ORM objects
    Ex) GatewayTypeFactory(country=country1)
    """

    class Meta:
        model = GatewayType
        django_get_or_create = ("name",)

    name = factory.LazyAttribute(
        lambda o: "{}-Admin Level {}".format(
            o.country.country_short_code, o.admin_level
        )
    )
    display_name = factory.LazyAttribute(lambda o: o.name)
    admin_level = factory.Sequence(lambda n: "%d" % n)

    # We are going to fill country manually
    country = factory.SubFactory(CountryFactory)


class CartoDBTableFactory(factory.DjangoModelFactory):
    class Meta:
        model = CartoDBTable

    domain = "example"
    table_name = factory.Faker("uuid4")
    display_name = factory.Faker("city")
    # We are going to fill location type manually
    location_type = factory.SubFactory(GatewayTypeFactory)
    name_col = factory.Faker("word")
    pcode_col = factory.Faker("word")
    parent_code_col = ""
    parent = None
    # We are going to fill location type manually
    country = factory.SubFactory(CountryFactory)


class LocationFactory(factory.DjangoModelFactory):
    """
    Arguments:
        gateway {GatewayType} -- GatewayType ORM objects
        carto_db_table {Country} -- CartoDBTable ORM objects
    Ex) LocationFactory(gateway=b, carto_db_table=c)
    """

    class Meta:
        model = Location
        django_get_or_create = ("title", "p_code",)

    title = factory.LazyFunction(faker.city)
    # We are going to fill location type manually
    business_area = None
    gateway = factory.SubFactory(GatewayTypeFactory)
    # We are going to fill CartoDBTable manually
    carto_db_table = factory.SubFactory(CartoDBTableFactory)
    latitude = factory.LazyFunction(faker.latitude)
    longitude = factory.LazyFunction(faker.longitude)
    p_code = factory.LazyAttribute(
        lambda o: "{}{}".format(
            o.gateway.country.country_short_code, faker.random_number(4)
        )
    )
    parent = None
    geom = factory.LazyFunction(create_fake_multipolygon)
    point = None
