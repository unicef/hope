import time

from django.contrib.gis.geos import Point

import factory.fuzzy
from factory.django import DjangoModelFactory
from faker import Faker
from pytz import utc

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import (
    HUMANITARIAN_PARTNER,
    ORG_ENUMERATOR_CHOICES,
    RESIDENCE_STATUS_CHOICE,
    UNICEF,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    RegistrationDataImportDatahub,
)

faker = Faker()


class RegistrationDataImportDatahubFactory(DjangoModelFactory):
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


class ImportedHouseholdFactory(DjangoModelFactory):
    class Meta:
        model = ImportedHousehold

    consent_sign = factory.django.ImageField(color="blue")
    consent = True
    consent_sharing = (UNICEF, HUMANITARIAN_PARTNER)
    residence_status = factory.fuzzy.FuzzyChoice(
        RESIDENCE_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    country = factory.LazyFunction(lambda: Country.objects.order_by("?").first().iso_code2)
    country_origin = factory.LazyFunction(lambda: Country.objects.order_by("?").first().iso_code2)
    size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    registration_data_import = factory.SubFactory(
        RegistrationDataImportDatahubFactory,
    )
    first_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    last_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    admin1 = ""
    admin2 = ""
    admin3 = ""
    admin4 = ""
    admin1_title = ""
    admin2_title = ""
    admin3_title = ""
    admin4_title = ""
    geopoint = factory.LazyAttribute(lambda o: Point(faker.latlng()))
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
    enumerator_rec_id = factory.fuzzy.FuzzyInteger(9999999, 99999999)
