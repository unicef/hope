import random
import time

from django.contrib.gis.geos import Point

import factory.fuzzy
from faker import Faker
from pytz import utc

from hct_mis_api.apps.household.const import NATIONALITIES
from hct_mis_api.apps.household.models import (
    HUMANITARIAN_PARTNER,
    MARITAL_STATUS_CHOICE,
    ORG_ENUMERATOR_CHOICES,
    RESIDENCE_STATUS_CHOICE,
    UNICEF,
    SEX_CHOICE,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
    ImportedDocument,
    ImportedDocumentType,
)

faker = Faker()


class RegistrationDataImportDatahubFactory(factory.DjangoModelFactory):
    class Meta:
        model = RegistrationDataImportDatahub

    factory.LazyFunction(
        lambda: f"{faker.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)} - {time.time_ns()}"
    )
    import_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        tzinfo=utc,
    )


class ImportedHouseholdFactory(factory.DjangoModelFactory):
    class Meta:
        model = ImportedHousehold

    consent_sign = factory.django.ImageField(color="blue")
    consent = True
    consent_sharing = (UNICEF, HUMANITARIAN_PARTNER)
    residence_status = factory.fuzzy.FuzzyChoice(
        RESIDENCE_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    country = factory.Faker("country_code", representation="alpha-2")
    country_origin = factory.fuzzy.FuzzyChoice(
        NATIONALITIES,
        getter=lambda c: c[0],
    )
    size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    registration_data_import = factory.SubFactory(
        RegistrationDataImportDatahubFactory,
    )
    first_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    last_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    admin1 = ""
    admin2 = ""
    geopoint = factory.LazyAttribute(lambda o: Point(factory.Faker("latlng").generate()))
    female_age_group_0_5_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_6_11_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_12_17_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_18_59_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_60_count = factory.fuzzy.FuzzyInteger(3, 8)
    pregnant_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_0_5_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_6_11_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_12_17_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_18_59_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_60_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_0_5_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_6_11_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_12_17_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_18_59_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    female_age_group_60_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_0_5_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_6_11_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_12_17_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_18_59_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    male_age_group_60_disabled_count = factory.fuzzy.FuzzyInteger(3, 8)
    start = factory.Faker("date_time_this_month", before_now=True, after_now=False, tzinfo=utc)
    deviceid = factory.Faker("md5")
    name_enumerator = factory.Faker("name")
    org_enumerator = factory.fuzzy.FuzzyChoice(
        ORG_ENUMERATOR_CHOICES,
        getter=lambda c: c[0],
    )
    org_name_enumerator = "Partner Organization"
    village = factory.Faker("city")


class ImportedIndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = ImportedIndividual

    full_name = factory.LazyAttribute(lambda o: f"{o.given_name} {o.middle_name} {o.family_name}")
    given_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    family_name = factory.Faker("last_name")
    sex = factory.fuzzy.FuzzyChoice(
        SEX_CHOICE,
        getter=lambda c: c[0],
    )
    birth_date = factory.Faker("date_of_birth", tzinfo=utc, minimum_age=16, maximum_age=90)
    estimated_birth_date = factory.fuzzy.FuzzyChoice((True, False))
    marital_status = factory.fuzzy.FuzzyChoice(
        MARITAL_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    phone_no = factory.Faker("phone_number")
    phone_no_alternative = ""
    registration_data_import = factory.SubFactory(RegistrationDataImportDatahubFactory)
    disability = False
    household = factory.SubFactory(ImportedHouseholdFactory)
    first_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    last_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)


def create_imported_household(household_args=None, individual_args=None):
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}
    household = ImportedHouseholdFactory(**household_args)
    individuals = ImportedIndividualFactory.create_batch(household.size, household=household, **individual_args)
    individuals[0].relationship = "HEAD"
    individuals[0].save()
    household.head_of_household = individuals[0]
    household.save()
    return household, individuals


def create_imported_household_and_individuals(household_data=None, individuals_data=None):
    if household_data is None:
        household_data = {}
    if individuals_data is None:
        individuals_data = {}
    household = ImportedHouseholdFactory.build(**household_data, size=len(individuals_data))
    individuals = [
        ImportedIndividualFactory(household=household, **individual_data) for individual_data in individuals_data
    ]
    household.head_of_household = individuals[0]
    household.save()
    return household, individuals


class ImportedDocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = ImportedDocument

    document_number = factory.Faker("pystr", min_chars=None, max_chars=20)
    type = factory.LazyAttribute(lambda o: ImportedDocumentType.objects.order_by("?").first())
    individual = factory.SubFactory(ImportedIndividualFactory)


class ImportedDocumentTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = ImportedDocumentType

    type = random.choice(["BIRTH_CERTIFICATE", "TAX_ID", "DRIVERS_LICENSE"])
