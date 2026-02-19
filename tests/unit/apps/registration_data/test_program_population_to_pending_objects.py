import datetime

import pytest

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    AreaFactory,
    BusinessAreaFactory,
    CountryFactory,
    DeliveryMechanismFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.household.const import HEAD, MALE, ROLE_ALTERNATE, ROLE_PRIMARY
from hope.apps.registration_data.tasks.import_program_population import import_program_population
from hope.models import Account, Document, Household, Individual, IndividualIdentity, IndividualRoleInHousehold
from hope.models.utils import MergeStatusModel

HOUSEHOLD_FIELDS = (
    "consent_sign",
    "consent",
    "consent_sharing",
    "residence_status",
    "country_origin",
    "zip_code",
    "size",
    "address",
    "country",
    "female_age_group_0_5_count",
    "female_age_group_6_11_count",
    "female_age_group_12_17_count",
    "female_age_group_18_59_count",
    "female_age_group_60_count",
    "pregnant_count",
    "male_age_group_0_5_count",
    "male_age_group_6_11_count",
    "male_age_group_12_17_count",
    "male_age_group_18_59_count",
    "male_age_group_60_count",
    "female_age_group_0_5_disabled_count",
    "female_age_group_6_11_disabled_count",
    "female_age_group_12_17_disabled_count",
    "female_age_group_18_59_disabled_count",
    "female_age_group_60_disabled_count",
    "male_age_group_0_5_disabled_count",
    "male_age_group_6_11_disabled_count",
    "male_age_group_12_17_disabled_count",
    "male_age_group_18_59_disabled_count",
    "male_age_group_60_disabled_count",
    "flex_fields",
    "start",
    "deviceid",
    "name_enumerator",
    "org_enumerator",
    "org_name_enumerator",
    "village",
    "registration_method",
    "currency",
    "unhcr_id",
    "geopoint",
    "returnee",
    "fchild_hoh",
    "child_hoh",
    "detail_id",
    "collect_type",
    "unicef_id",
)

INDIVIDUAL_FIELDS = (
    "photo",
    "full_name",
    "given_name",
    "middle_name",
    "family_name",
    "relationship",
    "sex",
    "birth_date",
    "estimated_birth_date",
    "marital_status",
    "phone_no",
    "phone_no_alternative",
    "email",
    "disability",
    "flex_fields",
    "deduplication_batch_status",
    "deduplication_batch_results",
    "observed_disability",
    "seeing_disability",
    "hearing_disability",
    "physical_disability",
    "memory_disability",
    "selfcare_disability",
    "comms_disability",
    "who_answers_phone",
    "who_answers_alt_phone",
    "pregnant",
    "work_status",
    "detail_id",
    "disability_certificate_picture",
    "preferred_language",
    "age_at_registration",
    "payment_delivery_phone_no",
    "wallet_name",
    "blockchain_name",
    "wallet_address",
    "unicef_id",
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> object:
    return BusinessAreaFactory()


@pytest.fixture
def country() -> object:
    return CountryFactory()


@pytest.fixture
def country_origin() -> object:
    return CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="0616")


@pytest.fixture
def admin_areas() -> list:
    return [AreaFactory(), AreaFactory(), AreaFactory(), AreaFactory()]


@pytest.fixture
def program_from(business_area: object) -> object:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_to(business_area: object) -> object:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi_to(business_area: object, program_to: object) -> object:
    return RegistrationDataImportFactory(business_area=business_area, program=program_to)


@pytest.fixture
def rdi_from(business_area: object, program_from: object) -> object:
    return RegistrationDataImportFactory(business_area=business_area, program=program_from)


@pytest.fixture
def head_individual(business_area: object, program_from: object, rdi_from: object) -> object:
    return IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2021, 1, 1),
        last_registration_date=datetime.date(2021, 1, 1),
        given_name="Test",
        full_name="Test Testowski",
        middle_name="",
        family_name="Testowski",
        phone_no="123-123-123",
        phone_no_alternative="",
        relationship=HEAD,
        sex=MALE,
        birth_date=datetime.date(1955, 9, 7),
    )


@pytest.fixture
def base_household_context(
    business_area: object,
    program_from: object,
    rdi_from: object,
    head_individual: object,
    admin_areas: list,
    country: object,
    country_origin: object,
) -> dict:
    household = HouseholdFactory(
        registration_data_import=rdi_from,
        first_registration_date=datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc),
        last_registration_date=datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc),
        program=program_from,
        business_area=business_area,
        admin1=admin_areas[0],
        admin2=admin_areas[1],
        admin3=admin_areas[2],
        admin4=admin_areas[3],
        detail_id="1234567890",
        flex_fields={"enumerator_id": "123", "some": "thing"},
        country=country,
        country_origin=country_origin,
        head_of_household=head_individual,
        create_role=False,
        size=2,
    )
    second_individual = IndividualFactory(
        household=household,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2024, 2, 21),
        last_registration_date=datetime.date(2024, 2, 24),
    )
    return {"household": household, "individuals": [head_individual, second_individual]}


@pytest.fixture
def base_population(
    base_household_context: dict,
    program_from: object,
    country: object,
) -> dict:
    household = base_household_context["household"]
    head_individual = base_household_context["individuals"][0]
    secondary_individual = base_household_context["individuals"][1]

    role = IndividualRoleInHouseholdFactory(
        household=household,
        individual=secondary_individual,
        role=ROLE_PRIMARY,
    )
    document_type = DocumentTypeFactory(key="birth_certificate")
    document = DocumentFactory(
        individual=head_individual,
        program=program_from,
        type=document_type,
        country=country,
    )
    identity = IndividualIdentityFactory(
        individual=head_individual,
        country=country,
        partner=PartnerFactory(),
    )
    DeliveryMechanismFactory(code="mobile_money")
    account_type = AccountTypeFactory(key="mobile")
    account = AccountFactory(
        individual=head_individual,
        data={"phone_number_test": "1234567890"},
        rdi_merge_status=MergeStatusModel.MERGED,
        account_type=account_type,
    )
    return {
        "household": household,
        "individuals": [head_individual, secondary_individual],
        "role": role,
        "document": document,
        "identity": identity,
        "account": account,
    }


def test_create_pending_objects_from_objects(
    base_population: dict,
    program_from: object,
    program_to: object,
    rdi_to: object,
    business_area: object,
) -> None:
    assert Household.pending_objects.count() == 0
    assert Individual.pending_objects.count() == 0
    assert IndividualIdentity.pending_objects.count() == 0
    assert Document.pending_objects.count() == 0
    assert IndividualRoleInHousehold.pending_objects.count() == 0
    assert Account.all_objects.filter(rdi_merge_status=MergeStatusModel.PENDING).count() == 0

    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to.id),
        rdi=rdi_to,
    )

    assert Household.pending_objects.count() == 1
    assert Individual.pending_objects.count() == 2
    assert IndividualIdentity.pending_objects.count() == 1
    assert Document.pending_objects.count() == 1
    assert IndividualRoleInHousehold.pending_objects.count() == 1
    assert Account.all_objects.filter(rdi_merge_status=MergeStatusModel.PENDING).count() == 1

    household = base_population["household"]
    individuals = base_population["individuals"]
    document = base_population["document"]
    identity = base_population["identity"]

    pending_household = Household.pending_objects.first()
    assert pending_household is not None

    household.refresh_from_db()
    for individual in individuals:
        individual.refresh_from_db()

    for field in HOUSEHOLD_FIELDS:
        pending_household_field = getattr(pending_household, field)
        household_field = getattr(household, field)
        assert pending_household_field == household_field
    assert pending_household.first_registration_date != household.first_registration_date
    assert pending_household.last_registration_date != household.last_registration_date
    assert pending_household.program_id == program_to.id
    assert pending_household.registration_data_import_id == rdi_to.id
    assert pending_household.rdi_merge_status == MergeStatusModel.PENDING
    assert pending_household.household_collection is None

    pending_individuals = Individual.pending_objects.all()
    head_of_household_pending_individual = pending_individuals.get(relationship=HEAD)

    assert pending_household.head_of_household == head_of_household_pending_individual

    assert household.head_of_household == individuals[0]
    assert individuals[0].household == household
    assert individuals[1].household == household

    for field in INDIVIDUAL_FIELDS:
        imported_individual_field = getattr(head_of_household_pending_individual, field)
        individual_field = getattr(individuals[0], field)
        assert imported_individual_field == individual_field, field
    assert head_of_household_pending_individual.first_registration_date != individuals[0].first_registration_date
    assert head_of_household_pending_individual.last_registration_date != individuals[0].last_registration_date
    for pending_individual in pending_individuals:
        assert pending_individual.program_id == program_to.id
        assert pending_individual.registration_data_import_id == rdi_to.id
        assert pending_individual.rdi_merge_status == MergeStatusModel.PENDING
        assert pending_individual.individual_collection is None
        assert pending_individual.household == pending_household

    assert head_of_household_pending_individual.relationship == HEAD

    pending_document = Document.pending_objects.first()
    for field in (
        "document_number",
        "photo",
        "expiry_date",
        "issuance_date",
    ):
        pending_document_field = getattr(pending_document, field)
        document_field = getattr(document, field)
        assert pending_document_field == document_field

    assert pending_document.program_id == program_to.id
    assert pending_document.rdi_merge_status == MergeStatusModel.PENDING
    assert pending_document.individual == head_of_household_pending_individual
    assert pending_document.status == Document.STATUS_PENDING

    pending_identity = IndividualIdentity.pending_objects.first()
    assert pending_identity.number == identity.number
    assert pending_identity.country.iso_code2 == identity.country.iso_code2
    assert pending_identity.partner == identity.partner
    assert pending_identity.rdi_merge_status == MergeStatusModel.PENDING
    assert pending_identity.individual == head_of_household_pending_individual

    pending_individual_role_in_household = IndividualRoleInHousehold.pending_objects.first()
    assert pending_individual_role_in_household.household.unicef_id == household.unicef_id
    assert pending_individual_role_in_household.individual.unicef_id == individuals[1].unicef_id
    assert pending_individual_role_in_household.role == ROLE_PRIMARY
    assert pending_individual_role_in_household.rdi_merge_status == MergeStatusModel.PENDING
    assert pending_individual_role_in_household.household == pending_household
    assert pending_individual_role_in_household.individual == pending_individuals.exclude(relationship=HEAD).first()

    registration_data_import = RegistrationDataImportFactory(
        business_area=business_area,
        program=program_to,
    )
    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to.id),
        rdi=registration_data_import,
    )
    pending_household_count = (
        Household.pending_objects.filter(registration_data_import=registration_data_import)
        .order_by("created_at")
        .count()
    )
    pending_individual_count = (
        Individual.pending_objects.filter(registration_data_import=registration_data_import)
        .order_by("-created_at")
        .count()
    )
    assert pending_household_count == 0
    assert pending_individual_count == 0


def test_not_import_excluded_objects(
    base_population: dict,
    business_area: object,
    program_from: object,
    program_to: object,
    rdi_from: object,
    rdi_to: object,
) -> None:
    assert base_population
    household_withdrawn_head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        withdrawn=True,
        relationship=HEAD,
        first_registration_date=datetime.date(2024, 2, 21),
        last_registration_date=datetime.date(2024, 2, 24),
    )
    household_withdrawn = HouseholdFactory(
        registration_data_import=rdi_from,
        program=program_from,
        business_area=business_area,
        withdrawn=True,
        head_of_household=household_withdrawn_head,
        create_role=False,
        size=2,
    )
    withdrawn_individual = IndividualFactory(
        household=household_withdrawn,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        withdrawn=True,
        first_registration_date=datetime.date(2024, 2, 21),
        last_registration_date=datetime.date(2024, 2, 24),
    )
    duplicate_individual = IndividualFactory(
        household=household_withdrawn,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        duplicate=True,
        first_registration_date=datetime.date(2024, 2, 21),
        last_registration_date=datetime.date(2024, 2, 24),
    )

    household_collection = HouseholdCollectionFactory()
    individual_collection = IndividualCollectionFactory()

    household_already_in_program_head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        relationship=HEAD,
        first_registration_date=datetime.date(2024, 2, 21),
        last_registration_date=datetime.date(2024, 2, 24),
    )
    household_already_in_program = HouseholdFactory(
        registration_data_import=rdi_from,
        program=program_from,
        business_area=business_area,
        head_of_household=household_already_in_program_head,
        create_role=False,
        household_collection=household_collection,
        size=1,
    )
    individual_already_in_program = household_already_in_program_head

    household_already_in_program_repr = HouseholdFactory(
        registration_data_import=rdi_to,
        program=program_to,
        business_area=business_area,
        head_of_household=IndividualFactory(
            household=None,
            registration_data_import=rdi_to,
            business_area=business_area,
            program=program_to,
            relationship=HEAD,
            first_registration_date=datetime.date(2024, 2, 21),
            last_registration_date=datetime.date(2024, 2, 24),
        ),
        create_role=False,
        household_collection=household_collection,
        size=1,
    )
    household_already_in_program_repr.unicef_id = household_already_in_program.unicef_id
    household_already_in_program_repr.save(update_fields=["unicef_id"])

    individual_already_in_program.individual_collection = individual_collection
    individual_already_in_program.save(update_fields=["individual_collection"])

    individual_already_in_program_repr = household_already_in_program_repr.head_of_household
    individual_already_in_program_repr.individual_collection = individual_collection
    individual_already_in_program_repr.unicef_id = individual_already_in_program.unicef_id
    individual_already_in_program_repr.save(update_fields=["individual_collection", "unicef_id"])

    assert Household.pending_objects.count() == 0
    assert Individual.pending_objects.count() == 0
    assert IndividualIdentity.pending_objects.count() == 0
    assert Document.pending_objects.count() == 0
    assert IndividualRoleInHousehold.pending_objects.count() == 0
    assert Account.all_objects.filter(rdi_merge_status=MergeStatusModel.PENDING).count() == 0

    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to.id),
        rdi=rdi_to,
    )

    assert not Household.pending_objects.filter(unicef_id=household_withdrawn.unicef_id).exists()
    assert not Individual.pending_objects.filter(unicef_id=withdrawn_individual.unicef_id).exists()
    assert not Individual.pending_objects.filter(unicef_id=duplicate_individual.unicef_id).exists()
    assert not Household.pending_objects.filter(unicef_id=household_already_in_program.unicef_id).exists()
    assert not Individual.pending_objects.filter(unicef_id=individual_already_in_program.unicef_id).exists()


def test_import_program_population_with_excluded_individuals(
    business_area: object,
    program_from: object,
    program_to: object,
    rdi_to: object,
    rdi_from: object,
) -> None:
    individual_already_in_program_to = IndividualFactory(
        registration_data_import=rdi_to,
        business_area=business_area,
        program=program_to,
    )
    household_head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        relationship=HEAD,
    )
    household = HouseholdFactory(
        registration_data_import=rdi_from,
        program=program_from,
        business_area=business_area,
        head_of_household=household_head,
        create_role=False,
        size=1,
    )
    individual_already_in_program_from = household_head
    IndividualRoleInHouseholdFactory(
        household=household,
        individual=individual_already_in_program_from,
        role=ROLE_PRIMARY,
    )
    individual_collection = IndividualCollectionFactory()
    individual_already_in_program_to.individual_collection = individual_collection
    individual_already_in_program_to.save(update_fields=["individual_collection"])
    individual_already_in_program_from.individual_collection = individual_collection
    individual_already_in_program_from.unicef_id = individual_already_in_program_to.unicef_id
    individual_already_in_program_from.save(update_fields=["individual_collection", "unicef_id"])

    assert not Individual.pending_objects.filter(unicef_id=individual_already_in_program_from.unicef_id).exists()
    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to.id),
        rdi=rdi_to,
    )

    assert not Individual.pending_objects.filter(unicef_id=individual_already_in_program_from.unicef_id).exists()

    new_hh_repr = Household.pending_objects.filter(
        unicef_id=household.unicef_id,
        program=program_to,
    ).first()
    assert new_hh_repr.representatives.count() == 1
    assert new_hh_repr.representatives.first() == individual_already_in_program_to

    assert new_hh_repr.head_of_household == individual_already_in_program_to

    assert (
        IndividualRoleInHousehold.objects.filter(
            household=household,
            individual=individual_already_in_program_from,
        ).first()
        is not None
    )
    assert (
        IndividualRoleInHousehold.pending_objects.filter(
            household=new_hh_repr,
            individual=individual_already_in_program_to,
        ).first()
        is not None
    )


def test_import_program_population_individual_without_household(
    business_area: object, program_to: object, rdi_to: object
) -> None:
    program_from = ProgramFactory(business_area=business_area)
    rdi_from = RegistrationDataImportFactory(business_area=business_area, program=program_from)
    household_head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        relationship=HEAD,
    )
    HouseholdFactory(
        registration_data_import=rdi_from,
        program=program_from,
        business_area=business_area,
        head_of_household=household_head,
        create_role=False,
        size=1,
    )
    individual_without_hh = IndividualFactory(
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
    )

    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to.id),
        rdi=rdi_to,
    )

    assert Individual.pending_objects.filter(program=program_to).count() == 2

    individual_without_hh_repr = Individual.pending_objects.filter(
        program=program_to,
        unicef_id=individual_without_hh.unicef_id,
    ).first()

    assert individual_without_hh_repr is not None
    assert individual_without_hh_repr.household is None


def test_import_program_population_withdrawn_individual_with_role(
    business_area: object, program_to: object, rdi_to: object
) -> None:
    program_from = ProgramFactory(business_area=business_area)
    rdi_from = RegistrationDataImportFactory(business_area=business_area, program=program_from)
    head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        relationship=HEAD,
    )
    household = HouseholdFactory(
        registration_data_import=rdi_from,
        program=program_from,
        business_area=business_area,
        head_of_household=head,
        create_role=False,
        size=2,
    )
    individual = IndividualFactory(
        household=household,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
    )

    IndividualRoleInHouseholdFactory(
        household=household,
        individual=individual,
        role=ROLE_ALTERNATE,
    )
    individual.withdrawn = True
    individual.save(update_fields=["withdrawn"])

    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to.id),
        rdi=rdi_to,
    )

    assert Individual.pending_objects.filter(program=program_to).count() == 1

    assert not IndividualRoleInHousehold.pending_objects.filter(
        role=ROLE_ALTERNATE,
    ).exists()


def test_import_program_population_import_from_ids(
    base_population: dict,
    business_area: object,
    program_from: object,
    rdi_from: object,
    rdi_to: object,
) -> None:
    program_to_import_from_ids = ProgramFactory(business_area=business_area)
    program_to_without_import_from_ids = ProgramFactory(business_area=business_area)

    household_1_head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2021, 2, 1),
        last_registration_date=datetime.date(2021, 2, 1),
        given_name="Test_1",
        full_name="Test_1 Testowski_1",
        family_name="Testowski_1",
        relationship=HEAD,
    )
    household_1 = HouseholdFactory(
        registration_data_import=rdi_from,
        first_registration_date=datetime.datetime(2021, 2, 1, tzinfo=datetime.timezone.utc),
        last_registration_date=datetime.datetime(2021, 2, 1, tzinfo=datetime.timezone.utc),
        program=program_from,
        business_area=business_area,
        head_of_household=household_1_head,
        create_role=False,
        size=2,
    )
    IndividualFactory(
        household=household_1,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2024, 2, 21),
        last_registration_date=datetime.date(2024, 2, 24),
    )
    IndividualRoleInHouseholdFactory(
        household=household_1,
        individual=household_1_head,
        role=ROLE_PRIMARY,
    )

    household_2_head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2021, 3, 1),
        last_registration_date=datetime.date(2021, 3, 1),
        given_name="Test_2",
        full_name="Test_2 Testowski_2",
        family_name="Testowski_2",
        relationship=HEAD,
    )
    household_2 = HouseholdFactory(
        registration_data_import=rdi_from,
        first_registration_date=datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc),
        last_registration_date=datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc),
        program=program_from,
        business_area=business_area,
        head_of_household=household_2_head,
        create_role=False,
        size=2,
    )
    IndividualFactory(
        household=household_2,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2024, 3, 21),
        last_registration_date=datetime.date(2024, 3, 24),
    )
    IndividualRoleInHouseholdFactory(
        household=household_2,
        individual=household_2_head,
        role=ROLE_PRIMARY,
    )
    IndividualIdentityFactory(
        individual=household_2_head,
        partner=PartnerFactory(),
    )

    assert Household.pending_objects.count() == 0
    assert Individual.pending_objects.count() == 0
    assert IndividualIdentity.pending_objects.count() == 0
    assert Document.pending_objects.count() == 0
    assert IndividualRoleInHousehold.pending_objects.count() == 0
    assert Account.all_objects.filter(rdi_merge_status=MergeStatusModel.PENDING).count() == 0

    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to_without_import_from_ids.id),
        rdi=rdi_to,
    )

    assert Household.pending_objects.filter(program=program_to_without_import_from_ids).count() == 3
    assert Individual.pending_objects.filter(program=program_to_without_import_from_ids).count() == 6
    assert (
        IndividualIdentity.pending_objects.filter(individual__program=program_to_without_import_from_ids).count() == 2
    )
    assert Document.pending_objects.filter(program=program_to_without_import_from_ids).count() == 1
    assert (
        IndividualRoleInHousehold.pending_objects.filter(household__program=program_to_without_import_from_ids).count()
        == 3
    )
    assert (
        Account.all_objects.filter(
            rdi_merge_status=MergeStatusModel.PENDING,
            individual__program=program_to_without_import_from_ids,
        ).count()
        == 1
    )

    registration_data_import = RegistrationDataImportFactory(
        business_area=business_area,
        program=program_from,
        import_from_ids=f"{base_population['household'].unicef_id},{household_2.unicef_id}",
    )
    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to_import_from_ids.id),
        rdi=registration_data_import,
    )
    assert Household.pending_objects.filter(program=program_to_import_from_ids).count() == 2
    assert Individual.pending_objects.filter(program=program_to_import_from_ids).count() == 4
    assert IndividualIdentity.pending_objects.filter(individual__program=program_to_import_from_ids).count() == 2
    assert Document.pending_objects.filter(program=program_to_import_from_ids).count() == 1
    assert IndividualRoleInHousehold.pending_objects.filter(household__program=program_to_import_from_ids).count() == 2
    assert (
        Account.all_objects.filter(
            rdi_merge_status=MergeStatusModel.PENDING,
            individual__program=program_to_import_from_ids,
        ).count()
        == 1
    )


def test_import_program_population_exclude_external_collectors(
    base_population: dict,
    business_area: object,
    program_from: object,
    rdi_from: object,
    rdi_to: object,
) -> None:
    assert base_population
    program_to_exclude_external_collectors = ProgramFactory(business_area=business_area)
    program_to_without_exclude_external_collectors = ProgramFactory(business_area=business_area)

    household_1_head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2021, 2, 1),
        last_registration_date=datetime.date(2021, 2, 1),
        given_name="Test_1",
        full_name="Test_1 Testowski_1",
        family_name="Testowski_1",
        relationship=HEAD,
    )
    household_1 = HouseholdFactory(
        registration_data_import=rdi_from,
        first_registration_date=datetime.datetime(2021, 2, 1, tzinfo=datetime.timezone.utc),
        last_registration_date=datetime.datetime(2021, 2, 1, tzinfo=datetime.timezone.utc),
        program=program_from,
        business_area=business_area,
        head_of_household=household_1_head,
        create_role=False,
        size=2,
    )
    IndividualFactory(
        household=household_1,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2024, 2, 21),
        last_registration_date=datetime.date(2024, 2, 24),
    )
    external_collector_primary = IndividualFactory(
        program=program_from,
        business_area=business_area,
        registration_data_import=rdi_from,
    )
    IndividualRoleInHouseholdFactory(
        household=household_1,
        individual=external_collector_primary,
        role=ROLE_PRIMARY,
    )
    IndividualRoleInHouseholdFactory(
        household=household_1,
        individual=household_1_head,
        role=ROLE_ALTERNATE,
    )

    household_2_head = IndividualFactory(
        household=None,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2021, 3, 1),
        last_registration_date=datetime.date(2021, 3, 1),
        given_name="Test_2",
        full_name="Test_2 Testowski_2",
        family_name="Testowski_2",
        relationship=HEAD,
    )
    household_2 = HouseholdFactory(
        registration_data_import=rdi_from,
        first_registration_date=datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc),
        last_registration_date=datetime.datetime(2021, 3, 1, tzinfo=datetime.timezone.utc),
        program=program_from,
        business_area=business_area,
        head_of_household=household_2_head,
        create_role=False,
        size=2,
    )
    IndividualFactory(
        household=household_2,
        registration_data_import=rdi_from,
        business_area=business_area,
        program=program_from,
        first_registration_date=datetime.date(2024, 3, 21),
        last_registration_date=datetime.date(2024, 3, 24),
    )
    IndividualRoleInHouseholdFactory(
        household=household_2,
        individual=household_2_head,
        role=ROLE_PRIMARY,
    )
    external_collector_alternate = IndividualFactory(
        program=program_from,
        business_area=business_area,
        registration_data_import=rdi_from,
    )
    IndividualRoleInHouseholdFactory(
        household=household_2,
        individual=external_collector_alternate,
        role=ROLE_ALTERNATE,
    )
    IndividualIdentityFactory(
        individual=external_collector_alternate,
        partner=PartnerFactory(),
    )

    assert Household.pending_objects.count() == 0
    assert Individual.pending_objects.count() == 0
    assert IndividualIdentity.pending_objects.count() == 0
    assert Document.pending_objects.count() == 0
    assert IndividualRoleInHousehold.pending_objects.count() == 0
    assert Account.all_objects.filter(rdi_merge_status=MergeStatusModel.PENDING).count() == 0

    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to_without_exclude_external_collectors.id),
        rdi=rdi_to,
    )

    assert Household.pending_objects.filter(program=program_to_without_exclude_external_collectors).count() == 3
    assert Individual.pending_objects.filter(program=program_to_without_exclude_external_collectors).count() == 8
    assert (
        IndividualIdentity.pending_objects.filter(
            individual__program=program_to_without_exclude_external_collectors
        ).count()
        == 2
    )
    assert Document.pending_objects.filter(program=program_to_without_exclude_external_collectors).count() == 1
    assert (
        IndividualRoleInHousehold.pending_objects.filter(
            household__program=program_to_without_exclude_external_collectors
        ).count()
        == 5
    )
    assert (
        Account.all_objects.filter(
            rdi_merge_status=MergeStatusModel.PENDING,
            individual__program=program_to_without_exclude_external_collectors,
        ).count()
        == 1
    )

    registration_data_import = RegistrationDataImportFactory(
        business_area=business_area,
        program=program_from,
        exclude_external_collectors=True,
    )
    import_program_population(
        import_from_program_id=str(program_from.id),
        import_to_program_id=str(program_to_exclude_external_collectors.id),
        rdi=registration_data_import,
    )
    assert Household.pending_objects.filter(program=program_to_exclude_external_collectors).count() == 3
    assert Individual.pending_objects.filter(program=program_to_exclude_external_collectors).count() == 7
    assert (
        IndividualIdentity.pending_objects.filter(individual__program=program_to_exclude_external_collectors).count()
        == 1
    )
    assert Document.pending_objects.filter(program=program_to_exclude_external_collectors).count() == 1
    assert (
        IndividualRoleInHousehold.pending_objects.filter(
            household__program=program_to_exclude_external_collectors
        ).count()
        == 4
    )
    assert (
        Account.all_objects.filter(
            rdi_merge_status=MergeStatusModel.PENDING,
            individual__program=program_to_exclude_external_collectors,
        ).count()
        == 1
    )

    assert (
        external_collector_primary.copied_to(manager="pending_objects")
        .filter(program=program_to_exclude_external_collectors)
        .count()
        == 1
    )
    assert (
        external_collector_alternate.copied_to(manager="pending_objects")
        .filter(program=program_to_exclude_external_collectors)
        .count()
        == 0
    )
    household_1_copy = Household.pending_objects.filter(
        unicef_id=household_1.unicef_id,
        program=program_to_exclude_external_collectors,
    ).first()
    household_2_copy = Household.pending_objects.filter(
        unicef_id=household_2.unicef_id,
        program=program_to_exclude_external_collectors,
    ).first()
    assert household_1_copy.individuals_and_roles(manager="pending_objects").filter(role=ROLE_PRIMARY).count() == 1
    assert household_1_copy.individuals_and_roles(manager="pending_objects").filter(role=ROLE_ALTERNATE).count() == 1
    assert household_2_copy.individuals_and_roles(manager="pending_objects").filter(role=ROLE_PRIMARY).count() == 1
    assert household_2_copy.individuals_and_roles(manager="pending_objects").filter(role=ROLE_ALTERNATE).count() == 0
