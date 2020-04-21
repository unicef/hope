import factory.fuzzy
from django.contrib.gis.geos import Point
from pytz import utc

from household.const import NATIONALITIES
from household.models import (
    RESIDENCE_STATUS_CHOICE,
    SEX_CHOICE,
    YES_NO_CHOICE,
    MARTIAL_STATUS_CHOICE,
    IDENTIFICATION_TYPE_CHOICE,
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
    country = factory.Faker("country_code", representation='alpha-2')
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
    geopoint = factory.LazyAttribute(lambda o: Point(factory.Faker("latlng").generate()))
    unhcr_id = factory.Faker("uuid4")
    f_0_5_age_group = factory.fuzzy.FuzzyInteger(3, 8)
    f_6_11_age_group = factory.fuzzy.FuzzyInteger(3, 8)
    f_12_17_age_group = factory.fuzzy.FuzzyInteger(3, 8)
    f_adults = factory.fuzzy.FuzzyInteger(3, 8)
    f_pregnant = factory.fuzzy.FuzzyInteger(3, 8)
    m_0_5_age_group = factory.fuzzy.FuzzyInteger(3, 8)
    m_6_11_age_group = factory.fuzzy.FuzzyInteger(3, 8)
    m_12_17_age_group = factory.fuzzy.FuzzyInteger(3, 8)
    m_adults = factory.fuzzy.FuzzyInteger(3, 8)
    f_0_5_disability = factory.fuzzy.FuzzyInteger(3, 8)
    f_6_11_disability = factory.fuzzy.FuzzyInteger(3, 8)
    f_12_17_disability = factory.fuzzy.FuzzyInteger(3, 8)
    f_adults_disability = factory.fuzzy.FuzzyInteger(3, 8)
    m_0_5_disability = factory.fuzzy.FuzzyInteger(3, 8)
    m_6_11_disability = factory.fuzzy.FuzzyInteger(3, 8)
    m_12_17_disability = factory.fuzzy.FuzzyInteger(3, 8)
    m_adults_disability = factory.fuzzy.FuzzyInteger(3, 8)


class ImportedIndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = ImportedIndividual

    individual_ca_id = factory.Faker("uuid4")
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
    estimated_birth_date = factory.fuzzy.FuzzyChoice(
        YES_NO_CHOICE, getter=lambda c: c[0],
    )

    martial_status = factory.fuzzy.FuzzyChoice(
        MARTIAL_STATUS_CHOICE, getter=lambda c: c[0],
    )
    phone_no = factory.Faker("phone_number")
    phone_no_alternative = ""
    id_type = factory.fuzzy.FuzzyChoice(
        IDENTIFICATION_TYPE_CHOICE, getter=lambda c: c[0],
    )
    birth_certificate_no = ""
    birth_certificate_photo = ""
    drivers_license_no = ""
    drivers_license_photo = ""
    electoral_card_no = ""
    electoral_card_photo = ""
    unhcr_id_no = ""
    unhcr_id_photo = ""
    national_passport = ""
    national_passport_photo = ""
    scope_id_no = ""
    scope_id_photo = ""
    other_id_type = ""
    other_id_no = ""
    other_id_photo = ""
    registration_data_import = factory.SubFactory(
        RegistrationDataImportDatahubFactory
    )
    work_status = factory.fuzzy.FuzzyChoice(
        YES_NO_CHOICE, getter=lambda c: c[0],
    )
    disability = factory.fuzzy.FuzzyChoice(
        YES_NO_CHOICE, getter=lambda c: c[0],
    )
    household = factory.SubFactory(ImportedHouseholdFactory)
