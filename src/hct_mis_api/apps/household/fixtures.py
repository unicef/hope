import random
from typing import Any, Dict, List, Optional, Tuple

import factory
from factory import enums, fuzzy
from factory.django import DjangoModelFactory
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
    SEX_CHOICE,
    UNICEF,
    BankAccountInfo,
    Document,
    DocumentType,
    EntitlementCard,
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
    IndividualIdentity,
    IndividualRoleInHousehold,
    PendingBankAccountInfo,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.utils.models import MergeStatusModel

faker = Faker()


def flex_field_households(o: Any) -> Dict:
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


def flex_field_individual(o: Any) -> Dict:
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


class HouseholdCollectionFactory(DjangoModelFactory):
    class Meta:
        model = HouseholdCollection

    unicef_id = factory.Sequence(lambda n: f"HHC-{n}")


class HouseholdFactory(DjangoModelFactory):
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
    country_origin = factory.LazyAttribute(
        lambda o: geo_models.Country.objects.exclude(name="Unknown or Not Applicable").order_by("?").first()
    )
    country = factory.LazyAttribute(
        lambda o: geo_models.Country.objects.exclude(name="Unknown or Not Applicable").order_by("?").first()
    )
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
    household_collection = factory.SubFactory(HouseholdCollectionFactory)
    program = factory.SubFactory(ProgramFactory)
    rdi_merge_status = MergeStatusModel.MERGED

    @classmethod
    def build(cls, **kwargs: Any) -> Household:
        """Build an instance of the associated class, with overriden attrs."""
        if "registration_data_import__imported_by__partner" not in kwargs:
            kwargs["registration_data_import__imported_by__partner"] = PartnerFactory(name="UNICEF")
        return cls._generate(enums.BUILD_STRATEGY, kwargs)


class PendingHouseholdFactory(HouseholdFactory):
    rdi_merge_status = PendingHousehold.PENDING

    class Meta:
        model = PendingHousehold


class IndividualIdentityFactory(DjangoModelFactory):
    rdi_merge_status = MergeStatusModel.MERGED

    class Meta:
        model = IndividualIdentity

    number = factory.Faker("pystr", min_chars=None, max_chars=20)


class IndividualRoleInHouseholdFactory(DjangoModelFactory):
    rdi_merge_status = MergeStatusModel.MERGED

    class Meta:
        model = IndividualRoleInHousehold


class IndividualCollectionFactory(DjangoModelFactory):
    class Meta:
        model = IndividualCollection

    unicef_id = factory.Sequence(lambda n: f"INDC-{n}")


class IndividualFactory(DjangoModelFactory):
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
    phone_no = factory.Sequence(lambda n: f"+48 609 456 {n % 1000:03d}")
    phone_no_valid = True
    phone_no_alternative = ""
    phone_no_alternative_valid = True
    email = factory.Sequence(lambda n: f'factory.Faker("email"){n}')
    relationship = factory.fuzzy.FuzzyChoice([value for value, label in RELATIONSHIP_CHOICE[1:] if value != "HEAD"])
    household = factory.SubFactory(HouseholdFactory)
    registration_data_import = factory.SubFactory(RegistrationDataImportFactory)
    disability = NOT_DISABLED
    flex_fields = factory.LazyAttribute(flex_field_individual)
    first_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    last_registration_date = factory.Faker("date_time_this_year", before_now=True, after_now=False, tzinfo=utc)
    business_area = factory.LazyAttribute(lambda o: o.registration_data_import.business_area)
    unicef_id = factory.Sequence(lambda n: f"IND-{n}")
    individual_collection = factory.SubFactory(IndividualCollectionFactory)
    program = factory.SubFactory(ProgramFactory)
    rdi_merge_status = MergeStatusModel.MERGED


class PendingIndividualFactory(IndividualFactory):
    rdi_merge_status = PendingIndividual.PENDING

    class Meta:
        model = PendingIndividual


class BankAccountInfoFactory(DjangoModelFactory):
    class Meta:
        model = BankAccountInfo

    individual = factory.SubFactory(IndividualFactory)
    bank_name = random.choice(["CityBank", "Santander", "JPMorgan"])
    bank_account_number = factory.LazyAttribute(lambda x: random.randint(10**26, 10**27 - 1))
    bank_branch_name = random.choice(["BranchCityBank", "BranchSantander", "BranchJPMorgan"])
    account_holder_name = factory.Faker("last_name")
    rdi_merge_status = MergeStatusModel.MERGED


class PendingBankAccountInfoFactory(BankAccountInfoFactory):
    rdi_merge_status = PendingIndividual.PENDING

    class Meta:
        model = PendingBankAccountInfo


class DocumentTypeFactory(DjangoModelFactory):
    class Meta:
        model = DocumentType
        django_get_or_create = ("key",)

    key = factory.fuzzy.FuzzyChoice([value.lower() for value, _ in IDENTIFICATION_TYPE_CHOICE])
    label = factory.LazyAttribute(lambda o: o.key.replace("_", " ").title())


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document
        django_get_or_create = ("document_number", "type", "country", "program")

    document_number = factory.Faker("pystr", min_chars=None, max_chars=20)
    type = factory.SubFactory(DocumentTypeFactory)
    individual = factory.SubFactory(IndividualFactory)
    country = factory.LazyAttribute(lambda o: geo_models.Country.objects.order_by("?").first())
    program = factory.SubFactory(ProgramFactory)
    rdi_merge_status = MergeStatusModel.MERGED


class PendingDocumentFactory(DocumentFactory):
    rdi_merge_status = MergeStatusModel.PENDING

    class Meta:
        model = PendingDocument
        django_get_or_create = ("document_number", "type", "country", "program")


class DocumentAllowDuplicatesFactory(DjangoModelFactory):
    class Meta:
        model = Document

    document_number = factory.Faker("pystr", min_chars=None, max_chars=20)
    type = factory.SubFactory(DocumentTypeFactory)
    individual = factory.SubFactory(IndividualFactory)
    country = factory.LazyAttribute(lambda o: geo_models.Country.objects.order_by("?").first())
    rdi_merge_status = MergeStatusModel.MERGED


class EntitlementCardFactory(DjangoModelFactory):
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


def create_household(
    household_args: Optional[Dict] = None, individual_args: Optional[Dict] = None
) -> Tuple[Household, List[Individual]]:
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}

    partner = PartnerFactory(name="UNICEF")
    household_args["registration_data_import__imported_by__partner"] = partner

    household = HouseholdFactory.build(**household_args)
    individuals = IndividualFactory.create_batch(
        household.size, household=None, program=household.program, **individual_args
    )

    household.head_of_household = individuals[0]
    household.household_collection.save()
    household.program.save()
    # household.registration_data_import.imported_by.partner.save()
    household.registration_data_import.imported_by.save()
    household.registration_data_import.program.save()
    household.registration_data_import.save()
    household.program.save()
    household.save()

    individuals_to_update = []
    for index, individual in enumerate(individuals):
        if index == 0:
            individual.relationship = "HEAD"
        individual.household = household
        individuals_to_update.append(individual)

    Individual.objects.bulk_update(individuals_to_update, ("relationship", "household"))

    primary_collector, alternate_collector = IndividualFactory.create_batch(
        2, household=None, program=household.program, relationship="NON_BENEFICIARY"
    )
    primary_collector_irh = IndividualRoleInHousehold(
        individual=primary_collector, household=household, role=ROLE_PRIMARY, rdi_merge_status=MergeStatusModel.MERGED
    )
    primary_collector_irh.save()
    alternate_collector_irh = IndividualRoleInHousehold(
        individual=alternate_collector,
        household=household,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    alternate_collector_irh.save()

    return household, individuals


def create_household_for_fixtures(
    household_args: Optional[Dict] = None, individual_args: Optional[Dict] = None
) -> Tuple[Household, Individual]:
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}
    household = HouseholdFactory.build(**household_args)
    individuals = IndividualFactory.create_batch(
        household.size, household=None, program=household.program, **individual_args
    )

    household.household_collection.save()
    household.program.save()
    household.head_of_household = individuals[0]
    household.registration_data_import.imported_by.save()
    household.registration_data_import.program.save()
    household.registration_data_import.save()
    household.program.save()
    household.save()

    individuals_to_update = []
    for index, individual in enumerate(individuals):
        if index == 0:
            individual.relationship = "HEAD"
        individual.household = household
        individuals_to_update.append(individual)

    Individual.objects.bulk_update(individuals_to_update, ("relationship", "household"))

    if random.choice([True, False]) and len(individuals) >= 2:
        IndividualRoleInHousehold.objects.create(
            individual=individuals[0], household=household, role=ROLE_PRIMARY, rdi_merge_status=MergeStatusModel.MERGED
        )
        IndividualRoleInHousehold.objects.create(
            individual=individuals[1],
            household=household,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
    else:
        primary_collector, alternate_collector = IndividualFactory.create_batch(
            2, household=None, program=household.program, relationship="NON_BENEFICIARY"
        )
        primary_collector_irh = IndividualRoleInHousehold(
            individual=primary_collector,
            household=household,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        primary_collector_irh.save()
        alternate_collector_irh = IndividualRoleInHousehold(
            individual=alternate_collector,
            household=household,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        alternate_collector_irh.save()

    return household, individuals


def create_household_and_individuals(
    household_data: Optional[Dict] = None, individuals_data: Optional[List[Dict]] = None, imported: bool = False
) -> Tuple[Household, List[Individual]]:
    if household_data is None:
        household_data = {}
    if individuals_data is None:
        individuals_data = []
    if household_data.get("size") is None:
        household_data["size"] = len(individuals_data)
    if "program" not in household_data:
        household_data["program"] = ProgramFactory()

    household: Household = HouseholdFactory.build(**household_data)
    household.program.save()
    household.household_collection.save()
    household.registration_data_import.program = household.program
    household.registration_data_import.program.save()
    household.registration_data_import.imported_by.save()
    household.registration_data_import.save()
    for individual_data in individuals_data:
        if "program" not in individual_data:
            individual_data["program"] = household.program
        if "registration_data_import" not in individual_data:
            individual_data["registration_data_import"] = household.registration_data_import
    individuals: List[Individual] = [
        IndividualFactory(
            household=None,
            **individual_data,
        )
        for individual_data in individuals_data
    ]
    household.head_of_household = individuals[0]
    household.save()

    individuals_to_update = []
    for index, individual in enumerate(individuals):
        if index == 0:
            individual.relationship = "HEAD"
        individual.household = household
        individuals_to_update.append(individual)
    Individual.objects.bulk_update(individuals_to_update, ("relationship", "household"))

    return household, individuals


def create_individual_document(individual: Individual, document_type: Optional[str] = None) -> Document:
    additional_fields = {}
    if document_type:
        document_type = DocumentTypeFactory(type=document_type)
        additional_fields["type"] = document_type
    document = DocumentFactory(individual=individual, **additional_fields)
    return document
