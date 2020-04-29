import factory.fuzzy
from django.contrib.gis.geos import Point
from pytz import utc

from household.const import NATIONALITIES
from household.models import (
    RESIDENCE_STATUS_CHOICE,
    SEX_CHOICE,
    MARITAL_STATUS_CHOICE,
)
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

    consent = factory.django.ImageField(color="blue")
    residence_status = factory.fuzzy.FuzzyChoice(
        RESIDENCE_STATUS_CHOICE, getter=lambda c: c[0],
    )
    country = factory.Faker("country_code", representation="alpha-2")
    country_origin = factory.fuzzy.FuzzyChoice(
        NATIONALITIES, getter=lambda c: c[0],
    )
    size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    registration_data_import = factory.SubFactory(
        RegistrationDataImportDatahubFactory,
    )
    registration_date = factory.Faker(
        "date_this_year", before_today=True, after_today=False
    )
    admin1 = ""
    admin2 = ""
    geopoint = factory.LazyAttribute(
        lambda o: Point(factory.Faker("latlng").generate())
    )
    female_age_group_0_5_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_6_11_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_12_17_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_adults_count = factory.fuzzy.FuzzyInteger(3, 8)
    pregnant_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_0_5_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_6_11_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_12_17_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_adults_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_0_5_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_6_11_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_12_17_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_adults_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_0_5_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_6_11_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_12_17_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_adults_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)


class ImportedIndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = ImportedIndividual

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
    estimated_birth_date = factory.fuzzy.FuzzyChoice((True, False))
    marital_status = factory.fuzzy.FuzzyChoice(
        MARITAL_STATUS_CHOICE, getter=lambda c: c[0],
    )
    phone_no = factory.Faker("phone_number")
    phone_no_alternative = ""
    registration_data_import = factory.SubFactory(
        RegistrationDataImportDatahubFactory
    )
    disability = factory.fuzzy.FuzzyChoice((True, False))
    household = factory.SubFactory(ImportedHouseholdFactory)
