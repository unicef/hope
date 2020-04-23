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
    MARTIAL_STATUS_CHOICE,
    IDENTIFICATION_TYPE_CHOICE,
    YES_NO_CHOICE,
    DISABILITY_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    RELATIONSHIP_CHOICE,
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


class IndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = Individual
    full_name = factory.LazyAttribute(
        lambda o: f"{o.given_name} {o.middle_name} {o.family_name}"
    )
    given_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    family_name = factory.Faker("last_name")
    years_in_school = factory.fuzzy.FuzzyInteger(1, 8)
    sex = factory.fuzzy.FuzzyChoice(SEX_CHOICE, getter=lambda c: c[0],)
    birth_date = factory.Faker(
        "date_of_birth", tzinfo=utc, minimum_age=16, maximum_age=90
    )
    estimated_birth_date = None
    marital_status = factory.fuzzy.FuzzyChoice(
        MARTIAL_STATUS_CHOICE, getter=lambda c: c[0],
    )
    phone_no = factory.Faker("phone_number")
    phone_no_alternative = ""
    relationship = factory.fuzzy.FuzzyChoice(
        [value for value, label in RELATIONSHIP_CHOICE if value != "HEAD"]
    )
    id_type = factory.fuzzy.FuzzyChoice(
        IDENTIFICATION_TYPE_CHOICE, getter=lambda c: c[0],
    )
    household = factory.SubFactory(HouseholdFactory)
    registration_data_import = factory.SubFactory(RegistrationDataImportFactory)
    work_status = factory.fuzzy.FuzzyChoice(
        YES_NO_CHOICE, getter=lambda c: c[0],
    )
    disability = factory.fuzzy.FuzzyChoice(
        DISABILITY_CHOICE, getter=lambda c: c[0],
    )
    serious_illness = factory.fuzzy.FuzzyChoice(
        YES_NO_CHOICE, getter=lambda c: c[0],
    )


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
