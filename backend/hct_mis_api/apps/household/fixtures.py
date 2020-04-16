import factory
from factory import fuzzy
from pytz import utc

from core.fixtures import LocationFactory
from household.const import NATIONALITIES
from household.models import (
    Household,
    EntitlementCard,
    Individual,
)
from registration_data.fixtures import RegistrationDataImportFactory


class HouseholdFactory(factory.DjangoModelFactory):
    class Meta:
        model = Household

    household_ca_id = factory.Faker("uuid4")
    consent = factory.django.ImageField(color="blue")
    residence_status = factory.fuzzy.FuzzyChoice(
        Household.RESIDENCE_STATUS_CHOICE, getter=lambda c: c[0],
    )
    nationality = factory.fuzzy.FuzzyChoice(
        NATIONALITIES, getter=lambda c: c[0],
    )
    family_size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    location = factory.SubFactory(LocationFactory)
    registration_data_import_id = factory.SubFactory(
        RegistrationDataImportFactory,
    )
    registration_date = factory.Faker(
        "date_this_year", before_today=True, after_today=False
    )
    # set it manually
    head_of_household = None
    flex_fields = {}


class IndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = Individual

    individual_ca_id = factory.Faker("uuid4")
    full_name = factory.LazyAttribute(
        lambda o: f"{o.first_name} {o.middle_name} {o.last_name}"
    )
    first_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    years_in_school = factory.fuzzy.FuzzyInteger(1, 8)
    sex = factory.fuzzy.FuzzyChoice(
        Individual.SEX_CHOICE, getter=lambda c: c[0],
    )
    dob = factory.Faker(
        "date_of_birth", tzinfo=utc, minimum_age=16, maximum_age=90
    )
    estimated_dob = None
    nationality = factory.fuzzy.FuzzyChoice(
        NATIONALITIES, getter=lambda c: c[0],
    )
    martial_status = factory.fuzzy.FuzzyChoice(
        Individual.MARTIAL_STATUS_CHOICE, getter=lambda c: c[0],
    )
    phone_number = factory.Faker("phone_number")
    phone_number_alternative = ""
    identification_type = factory.fuzzy.FuzzyChoice(
        Individual.IDENTIFICATION_TYPE_CHOICE, getter=lambda c: c[0],
    )
    identification_number = factory.Faker("uuid4")
    household = factory.SubFactory(HouseholdFactory)
    registration_data_import_id = factory.SubFactory(
        RegistrationDataImportFactory
    )
    work_status = factory.fuzzy.FuzzyChoice(
        Individual.YES_NO_CHOICE, getter=lambda c: c[0],
    )
    disability = factory.fuzzy.FuzzyChoice(
        Individual.DISABILITY_CHOICE, getter=lambda c: c[0],
    )
    serious_illness = factory.fuzzy.FuzzyChoice(
        Individual.YES_NO_CHOICE, getter=lambda c: c[0],
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
