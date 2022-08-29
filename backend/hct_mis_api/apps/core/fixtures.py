import factory
from faker import Faker

from hct_mis_api.apps.core.models import AdminArea, AdminAreaLevel

faker = Faker()


def create_fake_multipolygon():
    from django.contrib.gis.geos import MultiPolygon, Polygon

    p1 = Polygon(((0, 0), (0, 1), (1, 1), (0, 0)))
    p2 = Polygon(((1, 1), (1, 2), (2, 2), (1, 1)))

    return MultiPolygon(p1, p2)


class AdminAreaLevelFactory(factory.DjangoModelFactory):
    """
    Arguments:
        country {Country} -- Country ORM objects
    Ex) AdminAreaTypeFactory(country=country1)
    """

    class Meta:
        model = AdminAreaLevel
        django_get_or_create = (
            "business_area",
            "admin_level",
        )

    name = None
    display_name = factory.LazyAttribute(lambda o: o.name)
    admin_level = None
    business_area = None


class AdminAreaFactory(factory.DjangoModelFactory):
    """
    Arguments:
        admin_area_level {AdminAreaType} -- AdminAreaType ORM objects
    """

    class Meta:
        model = AdminArea
        django_get_or_create = (
            "title",
            "admin_area_level",
        )

    title = factory.LazyFunction(faker.city)
    # We are going to fill admin_area_level type manually
    admin_area_level = None
    parent = None
    geom = factory.LazyFunction(create_fake_multipolygon)
    point = None


def create_afghanistan(is_payment_plan_applicable=False):
    from hct_mis_api.apps.core.models import BusinessArea

    BusinessArea.objects.create(
        **{
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "approval_number_required": 2,
            "authorization_number_required": 2,
            "finance_review_number_required": 3,
            "is_payment_plan_applicable": is_payment_plan_applicable,
        },
    )
