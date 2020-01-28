import factory
from factory import fuzzy
from pytz import utc

from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from household.models import Household, RegistrationDataImport


class RegistrationDataImportFactory(factory.DjangoModelFactory):
    class Meta:
        model = RegistrationDataImport

    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    status = factory.fuzzy.FuzzyChoice(
        RegistrationDataImport.STATUS_CHOICE, getter=lambda c: c[0],
    )
    import_date = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=utc,
    )
    imported_by = factory.SubFactory(UserFactory)
    data_source = factory.fuzzy.FuzzyChoice(
        RegistrationDataImport.DATA_SOURCE_CHOICE, getter=lambda c: c[0],
    )
    number_of_individuals = factory.fuzzy.FuzzyInteger(100, 10000)
    number_of_households = factory.fuzzy.FuzzyInteger(3, 50)


class HouseholdFactory(factory.DjangoModelFactory):
    class Meta:
        model = Household

    household_ca_id = factory.Faker("uuid4")
    consent = factory.django.ImageField(color="blue")
    residence_status = factory.fuzzy.FuzzyChoice(
        Household.RESIDENCE_STATUS_CHOICE, getter=lambda c: c[0],
    )
    nationality = factory.Faker("country_code")
    family_size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    location = factory.SubFactory(LocationFactory)
    registration_data_import_id = factory.SubFactory(
        RegistrationDataImportFactory,
    )
