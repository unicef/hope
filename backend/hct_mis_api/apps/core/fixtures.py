import factory

from core.models import Location


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker('address')

    country = factory.Faker('country_code', representation="alpha-2")
