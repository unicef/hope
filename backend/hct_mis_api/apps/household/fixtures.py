import random

import factory
from factory import enums, fuzzy
from faker import Faker
from pytz import utc

from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.models import (
    HUMANITARIAN_PARTNER,
    IDENTIFICATION_TYPE_CHOICE,
    MARITAL_STATUS_CHOICE,
    NOT_DISABLED,
    ORG_ENUMERATOR_CHOICES,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    UNICEF,
    BankAccountInfo,
    Document,
    DocumentType,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    SEX_CHOICE,
)
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory

faker = Faker()


def flex_field_households(o):
    return {
        "treatment_facility_h_f": random.sample(
            [
                "government_health_center",
                "governent_hospital",
                "other_public",
                "private_hospital",
                "pharmacy",
                "private_doctor",
                "other_private",
            ],
            k=2,
        ),
        "other_treatment_facility_h_f": random.choice(["testing other", "narodowy fundusz zdrowia", None]),
    }


def flex_field_individual(o):
    return {
        "wellbeing_index_i_f": random.choice(["24", "150d", "666", None]),
        "school_enrolled_before_i_f": random.choice(["0", "1", None]),
        "diff_challenges_i_f": random.choice(
            [
                "bullying",
                "distance_school",
                "exclude_disabled",
                "financial_cons",
                "no_interest",
                "performance_issues",
                "physical_abuse",
                "poor_teaching",
                "psych_distress",
                "safety_fear",
                "verbal_abuse",
                None,
            ]
        ),
    }


class HouseholdFactory(factory.DjangoModelFactory):
    class Meta:
        model = Household

    unicef_id = factory.Sequence(lambda n: f"HH-{n}")
    consent_sign = factory.django.ImageField(color="blue")
    consent = True
    consent_sharing = (UNICEF, HUMANITARIAN_PARTNER)
    residence_status = factory.fuzzy.FuzzyChoice(
        RESIDENCE_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    country_origin = factory.LazyAttribute(lambda o: geo_models.Country.objects.order_by("?").first())
    country = factory.LazyAttribute(lambda o: geo_models.Country.objects.order_by("?").first())
    size = factory.fuzzy.FuzzyInteger(3, 8)
    address = factory.Faker("address")
    registration_data_import = factory.SubFactory(
        RegistrationDataImportFactory,
    )
    first_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    last_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    flex_fields = factory.LazyAttribute(flex_field_households)
    business_area = factory.LazyAttribute(lambda o: o.registration_data_import.business_area)
    start = factory.Faker("date_time_this_month", before_now=True, after_now=False, tzinfo=utc)
    deviceid = factory.Faker("md5")
    name_enumerator = factory.Faker("name")
    org_enumerator = factory.fuzzy.FuzzyChoice(
        ORG_ENUMERATOR_CHOICES,
        getter=lambda c: c[0],
    )
    org_name_enumerator = "Partner Organization"
    village = factory.Faker("city")
    female_age_group_0_5_count = factory.fuzzy.FuzzyInteger(0, 3)
    female_age_group_6_11_count = factory.fuzzy.FuzzyInteger(0, 3)
    female_age_group_12_17_count = factory.fuzzy.FuzzyInteger(0, 3)
    female_age_group_18_59_count = factory.fuzzy.FuzzyInteger(0, 3)
    female_age_group_60_count = factory.fuzzy.FuzzyInteger(0, 3)
    pregnant_count = factory.fuzzy.FuzzyInteger(0, 3)
    male_age_group_0_5_count = factory.fuzzy.FuzzyInteger(0, 3)
    male_age_group_6_11_count = factory.fuzzy.FuzzyInteger(0, 3)
    male_age_group_12_17_count = factory.fuzzy.FuzzyInteger(0, 3)
    male_age_group_18_59_count = factory.fuzzy.FuzzyInteger(0, 3)
    male_age_group_60_count = factory.fuzzy.FuzzyInteger(0, 3)

    @classmethod
    def build(cls, **kwargs):
        """Build an instance of the associated class, with overriden attrs."""
        if "registration_data_import__imported_by__partner" not in kwargs:
            kwargs["registration_data_import__imported_by__partner"] = PartnerFactory(name="UNICEF")
        return cls._generate(enums.BUILD_STRATEGY, kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        hoh = kwargs.get("head_of_household", None)
        if not hoh:
            hoh = IndividualFactory(household=None)
            kwargs["head_of_household"] = hoh
        ret = super()._create(model_class, *args, **kwargs)
        hoh.household = ret
        hoh.save()
        return ret


class IndividualIdentityFactory(factory.DjangoModelFactory):
    class Meta:
        model = IndividualIdentity

    number = factory.Faker("pystr", min_chars=None, max_chars=20)


class IndividualFactory(factory.DjangoModelFactory):
    class Meta:
        model = Individual

    full_name = factory.LazyAttribute(lambda o: f"{o.given_name} {o.middle_name} {o.family_name}")
    given_name = factory.Faker("first_name")
    middle_name = factory.Faker("first_name")
    family_name = factory.Faker("last_name")
    sex = factory.fuzzy.FuzzyChoice(
        SEX_CHOICE,
        getter=lambda c: c[0],
    )
    birth_date = factory.Faker("date_of_birth", tzinfo=utc, minimum_age=16, maximum_age=90)
    marital_status = factory.fuzzy.FuzzyChoice(
        MARITAL_STATUS_CHOICE,
        getter=lambda c: c[0],
    )
    phone_no = factory.LazyAttribute(lambda _: f"+380 {faker.msisdn()[:9]}")
    phone_no_alternative = ""
    relationship = factory.fuzzy.FuzzyChoice([value for value, label in RELATIONSHIP_CHOICE[1:] if value != "HEAD"])
    household = factory.SubFactory(HouseholdFactory)
    registration_data_import = factory.SubFactory(RegistrationDataImportFactory)
    disability = NOT_DISABLED
    flex_fields = factory.LazyAttribute(flex_field_individual)
    first_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    last_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    business_area = factory.LazyAttribute(lambda o: o.registration_data_import.business_area)
    unicef_id = factory.Sequence(lambda n: f"IND-{n}")


class BankAccountInfoFactory(factory.DjangoModelFactory):
    class Meta:
        model = BankAccountInfo

    individual = factory.SubFactory(IndividualFactory)
    bank_name = random.choice(["CityBank", "Santander", "JPMorgan"])
    bank_account_number = random.randint(10**26, 10**27 - 1)


class DocumentTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = DocumentType
        django_get_or_create = ("type",)

    type = factory.fuzzy.FuzzyChoice([value for value, _ in IDENTIFICATION_TYPE_CHOICE])


class DocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Document
        django_get_or_create = ("document_number", "type", "country")

    document_number = factory.Faker("pystr", min_chars=None, max_chars=20)
    type = factory.SubFactory(DocumentTypeFactory)
    individual = factory.SubFactory(IndividualFactory)
    country = factory.LazyAttribute(lambda o: geo_models.Country.objects.order_by("?").first())


class EntitlementCardFactory(factory.DjangoModelFactory):
    class Meta:
        model = EntitlementCard

    card_number = factory.Faker("credit_card_number")
    status = fuzzy.FuzzyChoice(
        EntitlementCard.STATUS_CHOICE,
        getter=lambda c: c[0],
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

    partner = PartnerFactory(name="UNICEF")
    household_args["registration_data_import__imported_by__partner"] = partner

    household = HouseholdFactory.build(**household_args)
    individuals = IndividualFactory.create_batch(household.size, household=None, **individual_args)

    household.head_of_household = individuals[0]
    # household.registration_data_import.imported_by.partner.save()
    household.registration_data_import.imported_by.save()
    household.registration_data_import.save()
    household.save()

    individuals_to_update = []
    for index, individual in enumerate(individuals):
        if index == 0:
            individual.relationship = "HEAD"
        individual.household = household
        individuals_to_update.append(individual)

    Individual.objects.bulk_update(individuals_to_update, ("relationship", "household"))

    primary_collector, alternate_collector = IndividualFactory.create_batch(
        2, household=None, relationship="NON_BENEFICIARY"
    )
    primary_collector_irh = IndividualRoleInHousehold(
        individual=primary_collector, household=household, role=ROLE_PRIMARY
    )
    primary_collector_irh.save()
    alternate_collector_irh = IndividualRoleInHousehold(
        individual=alternate_collector, household=household, role=ROLE_ALTERNATE
    )
    alternate_collector_irh.save()

    return household, individuals


def create_household_for_fixtures(household_args=None, individual_args=None):
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}
    household = HouseholdFactory.build(**household_args)
    individuals = IndividualFactory.create_batch(household.size, household=None, **individual_args)

    household.head_of_household = individuals[0]
    household.registration_data_import.imported_by.save()
    household.registration_data_import.save()
    household.save()

    individuals_to_update = []
    for index, individual in enumerate(individuals):
        if index == 0:
            individual.relationship = "HEAD"
        individual.household = household
        individuals_to_update.append(individual)

    Individual.objects.bulk_update(individuals_to_update, ("relationship", "household"))

    if random.choice([True, False]) and len(individuals) >= 2:
        IndividualRoleInHousehold.objects.create(individual=individuals[0], household=household, role=ROLE_PRIMARY)
        IndividualRoleInHousehold.objects.create(individual=individuals[1], household=household, role=ROLE_ALTERNATE)
    else:
        primary_collector, alternate_collector = IndividualFactory.create_batch(
            2, household=None, relationship="NON_BENEFICIARY"
        )
        primary_collector_irh = IndividualRoleInHousehold(
            individual=primary_collector, household=household, role=ROLE_PRIMARY
        )
        primary_collector_irh.save()
        alternate_collector_irh = IndividualRoleInHousehold(
            individual=alternate_collector, household=household, role=ROLE_ALTERNATE
        )
        alternate_collector_irh.save()

    return household, individuals


def create_household_and_individuals(household_data=None, individuals_data=None, imported=False):
    if household_data is None:
        household_data = {}
    if individuals_data is None:
        individuals_data = {}
    if household_data.get("size") is None:
        household_data["size"] = len(individuals_data)
    household = HouseholdFactory.build(**household_data)
    household.registration_data_import.imported_by.save()
    household.registration_data_import.save()
    individuals = [IndividualFactory(household=household, **individual_data) for individual_data in individuals_data]
    household.head_of_household = individuals[0]
    household.save()
    return household, individuals


def create_individual_document(individual, document_type=None):
    additional_fields = {}
    if document_type:
        document_type = DocumentTypeFactory(type=document_type)
        additional_fields["type"] = document_type
    document = DocumentFactory(individual=individual, **additional_fields)
    return document
