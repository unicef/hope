import factory
from factory import fuzzy
from pytz import utc

from core.fixtures import AdminAreaFactory
from household.const import NATIONALITIES
from household.models import (
    Household,
    EntitlementCard,
    Individual,
    SEX_CHOICE,
    MARITAL_STATUS_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    RELATIONSHIP_CHOICE,
    DocumentType,
    Document,
)
from registration_data.fixtures import RegistrationDataImportFactory


class HouseholdFactory(factory.DjangoModelFactory):
    class Meta:
        model = Household

    consent = factory.django.ImageField(color="blue")
    residence_status = factory.fuzzy.FuzzyChoice(
        RESIDENCE_STATUS_CHOICE, getter=lambda c: c[0],
    )
    country_origin = factory.Faker("country_code")
    country = factory.Faker("country_code")
    size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    registration_data_import = factory.SubFactory(
        RegistrationDataImportFactory,
    )
    registration_date = factory.Faker(
        "date_this_year", before_today=True, after_today=False
    )
    flex_fields = {}


class DocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Document

    document_number = factory.Faker("pystr", min_chars=None, max_chars=20)
    type = factory.LazyAttribute(
        lambda o: DocumentType.objects.order_by("?").first()
    )


class IndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = Individual

    full_name = factory.LazyAttribute(
        lambda o: f"{o.given_name} {o.middle_name} {o.family_name}"
    )
    given_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    family_name = factory.Faker("last_name")
    sex = factory.fuzzy.FuzzyChoice(SEX_CHOICE, getter=lambda c: c[0],)
    birth_date = factory.Faker(
        "date_of_birth", tzinfo=utc, minimum_age=16, maximum_age=90
    )
    marital_status = factory.fuzzy.FuzzyChoice(
        MARITAL_STATUS_CHOICE, getter=lambda c: c[0],
    )
    phone_no = factory.Faker("phone_number")
    phone_no_alternative = ""
    relationship = factory.fuzzy.FuzzyChoice(
        [value for value, label in RELATIONSHIP_CHOICE if value != "HEAD"]
    )
    household = factory.SubFactory(HouseholdFactory)
    registration_data_import = factory.SubFactory(RegistrationDataImportFactory)
    disability = factory.fuzzy.FuzzyChoice([True, False])


class EntitlementCardFactory(factory.DjangoModelFactory):
    class Meta:
        model = EntitlementCard

    card_number = factory.Faker("credit_card_number")
    status = fuzzy.FuzzyChoice(
        EntitlementCard.STATUS_CHOICE, getter=lambda c: c[0],
    )
    card_type = factory.Faker("credit_card_provider")
    current_card_size = "Lorem"
    card_custodian = factory.Faker("name")
    service_provider = factory.Faker("company")
    household = factory.SubFactory(HouseholdFactory)


def create_household(household_args=None, individual_args=None):
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}
    household = HouseholdFactory.build(**household_args)
    individuals = IndividualFactory.create_batch(
        household.size, household=household, **individual_args
    )
    individuals[0].relationship = "HEAD"
    individuals[0].save()
    household.head_of_household = individuals[0]
    household.registration_data_import.imported_by.save()
    household.registration_data_import.save()
    household.save()
    return household, individuals
