import factory.fuzzy
from pytz import utc

from household.const import NATIONALITIES
from registration_datahub.models import (
    RegistrationDataImportDatahub,
    ImportedHousehold,
    ImportedIndividual,
)


class RegistrationDataImportDatahubFactory(factory.DjangoModelFactory):
    class Meta:
        model = RegistrationDataImportDatahub

    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    import_date = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=utc,
    )


class ImportedHouseholdFactory(factory.DjangoModelFactory):
    class Meta:
        model = ImportedHousehold

    household_ca_id = factory.Faker("uuid4")
    consent = factory.django.ImageField(color="blue")
    residence_status = factory.fuzzy.FuzzyChoice(
        ImportedHousehold.RESIDENCE_STATUS_CHOICE, getter=lambda c: c[0],
    )
    nationality = factory.fuzzy.FuzzyChoice(
        NATIONALITIES, getter=lambda c: c[0],
    )
    family_size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    location = "Lorem Ipsum"
    registration_data_import_id = factory.SubFactory(
        RegistrationDataImportDatahubFactory,
    )
    # set it manually
    head_of_household = None
    representative = None
    registration_date = factory.Faker(
        "date_this_year", before_today=True, after_today=False
    )


class ImportedIndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = ImportedIndividual

    individual_ca_id = factory.Faker("uuid4")
    full_name = factory.LazyAttribute(
        lambda o: f"{o.first_name} {o.middle_name} {o.last_name}"
    )
    first_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    sex = factory.fuzzy.FuzzyChoice(
        ImportedIndividual.SEX_CHOICE, getter=lambda c: c[0],
    )
    dob = factory.Faker(
        "date_of_birth", tzinfo=utc, minimum_age=16, maximum_age=90
    )
    estimated_dob = factory.fuzzy.FuzzyChoice(
        ImportedIndividual.YES_NO_CHOICE, getter=lambda c: c[0],
    )
    nationality = factory.fuzzy.FuzzyChoice(
        NATIONALITIES, getter=lambda c: c[0],
    )
    martial_status = factory.fuzzy.FuzzyChoice(
        ImportedIndividual.MARTIAL_STATUS_CHOICE, getter=lambda c: c[0],
    )
    phone_number = factory.Faker("phone_number")
    phone_number_alternative = ""
    identification_type = factory.fuzzy.FuzzyChoice(
        ImportedIndividual.IDENTIFICATION_TYPE_CHOICE, getter=lambda c: c[0],
    )
    identification_number = factory.Faker("uuid4")
    registration_data_import_id = factory.SubFactory(
        RegistrationDataImportDatahubFactory
    )
    work_status = factory.fuzzy.FuzzyChoice(
        ImportedIndividual.YES_NO_CHOICE, getter=lambda c: c[0],
    )
    disability = factory.fuzzy.FuzzyChoice(
        ImportedIndividual.DISABILITY_CHOICE, getter=lambda c: c[0],
    )
    household = factory.SubFactory(ImportedHouseholdFactory)
