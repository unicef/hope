import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.household.const import (
    FEMALE,
    MALE,
    REMOVED_BY_COLLISION,
)
from hope.apps.program.collision_detectors import IdentificationKeyCollisionDetector
from hope.models import (
    Account,
    AccountType,
    Area,
    AreaType,
    Country,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
    Program,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def poland() -> Country:
    return Country.objects.create(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")


@pytest.fixture
def germany() -> Country:
    return Country.objects.create(name="Germany", iso_code2="DE", iso_code3="DEU", iso_num="276")


@pytest.fixture
def program(poland: Country, germany: Country) -> Program:
    business_area = create_afghanistan()
    business_area.countries.add(poland, germany)

    return ProgramFactory(
        name="Test Program for Household",
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def admin1(state: AreaType) -> Area:
    return Area.objects.create(name="Kabul", area_type=state, p_code="AF11")


@pytest.fixture
def admin2(district: AreaType) -> Area:
    return Area.objects.create(name="Kabul1", area_type=district, p_code="AF1115")


@pytest.fixture
def state(poland: Country) -> AreaType:
    return AreaType.objects.create(name="State", country=poland)


@pytest.fixture
def district(poland: Country, state: AreaType) -> AreaType:
    return AreaType.objects.create(name="District", parent=state, country=poland)


@pytest.fixture
def account_type() -> AccountType:
    return AccountType.objects.create(key="bank_account", label="Bank Account")


@pytest.fixture
def source_household(program: Program, admin1: Area, account_type: AccountType) -> tuple[Household, Individual]:
    household, individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.0002",
            "rdi_merge_status": "PENDING",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "size": 954,
            "returnee": True,
            "identification_key": "SAME-KEY-001",
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.0011",
                "rdi_merge_status": "PENDING",
                "business_area": program.business_area,
                "sex": MALE,
                "phone_no": "+48555444333",
                "identification_key": "IND-KEY-002",
            },
        ],
    )

    ind = individuals[0]

    Account.objects.create(
        individual=ind,
        number="ACC-123456",
        rdi_merge_status=Individual.MERGED,
        account_type=account_type,
    )

    ind.flex_fields = {"muac": 0}
    ind.save()
    household.flex_fields = {"eggs": "SOURCE"}
    household.save()

    return (household, ind)


@pytest.fixture
def destination_household(program: Program, admin1: Area, account_type: AccountType) -> tuple[Household, Individual]:
    household, individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.2002",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "size": 3,
            "returnee": False,
            "address": "Destination Address",
            "identification_key": "SAME-KEY-001",
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.2001",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
                "phone_no": "+48111222333",
                "full_name": "Destination Individual",
                "given_name": "Destination",
                "family_name": "Individual",
                "identification_key": "IND-KEY-001",
            },
            {
                "unicef_id": "IND-00-0000.00134",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
                "phone_no": "+48123123123",
                "identification_key": "IND-KEY-002",
            },
        ],
    )

    ind = individuals[0]
    Account.objects.create(
        individual=ind,
        number="999",
        rdi_merge_status=Individual.MERGED,
        account_type=account_type,
    )
    ind.flex_fields = {"muac": 10}
    ind.save()
    household.flex_fields = {"eggs": "DESTINATION"}
    household.save()

    return (household, ind)


def test_update_individual_identities_with_fixture_households(
    source_household: tuple[Household, Individual],
    destination_household: tuple[Household, Individual],
    poland: Country,
    program: Program,
) -> None:
    """Test that identities are transferred from source to destination individual and old ones are deleted."""
    source_individual = source_household[1]
    destination_individual = destination_household[1]

    from hope.models import Partner

    partner = Partner.objects.create(name="Test Partner")

    IndividualIdentity.objects.create(
        individual=source_individual,
        partner=partner,
        country=poland,
        number="SOURCE-ID-123",
    )

    IndividualIdentity.objects.create(
        individual=source_individual,
        partner=partner,
        country=poland,
        number="SOURCE-ID-456",
    )

    dest_identity = IndividualIdentity.objects.create(
        individual=destination_individual,
        partner=partner,
        country=poland,
        number="DEST-ID-789",
    )

    program.collision_detector = IdentificationKeyCollisionDetector
    program.save()

    detector = IdentificationKeyCollisionDetector(program)
    detector._update_individual_identities(destination_individual, source_individual)

    assert not IndividualIdentity.objects.filter(id=dest_identity.id).exists()

    transferred_identities = IndividualIdentity.objects.filter(individual=destination_individual)
    assert transferred_identities.count() == 2

    identity_numbers = set(transferred_identities.values_list("number", flat=True))
    assert "SOURCE-ID-123" in identity_numbers
    assert "SOURCE-ID-456" in identity_numbers

    for identity in transferred_identities:
        assert identity.partner == partner
        assert identity.country == poland


def test_update_documents_with_fixture_households(
    source_household: tuple[Household, Individual],
    destination_household: tuple[Household, Individual],
    poland: Country,
    program: Program,
) -> None:
    """Test that documents are transferred from source to destination, preserving statuses for matching docs."""
    source_individual = source_household[1]
    destination_individual = destination_household[1]

    doc_type_national_id = DocumentType.objects.create(label="National ID", key="national_id")

    doc_type_passport = DocumentType.objects.create(label="Passport", key="passport")

    Document.objects.create(
        individual=source_individual,
        document_number="DOC-123",
        type=doc_type_national_id,
        program=program,
        country=poland,
        status=Document.STATUS_PENDING,
    )

    Document.objects.create(
        individual=source_individual,
        document_number="DOC-456",
        type=doc_type_passport,
        program=program,
        country=poland,
        status=Document.STATUS_PENDING,
    )

    dest_doc1 = Document.objects.create(
        individual=destination_individual,
        document_number="DOC-123",
        type=doc_type_national_id,
        program=program,
        country=poland,
        status=Document.STATUS_INVALID,
    )

    dest_doc2 = Document.objects.create(
        individual=destination_individual,
        document_number="DOC-789",
        type=doc_type_passport,
        program=program,
        country=poland,
        status=Document.STATUS_NEED_INVESTIGATION,
    )

    detector = IdentificationKeyCollisionDetector(program)
    detector._update_documents(destination_individual, source_individual)

    assert not Document.objects.filter(id=dest_doc1.id).exists()
    assert not Document.objects.filter(id=dest_doc2.id).exists()

    transferred_docs = Document.objects.filter(individual=destination_individual)

    assert transferred_docs.count() == 2

    transferred_doc1 = Document.objects.get(individual=destination_individual, document_number="DOC-123")
    transferred_doc2 = Document.objects.get(individual=destination_individual, document_number="DOC-456")

    assert transferred_doc1.status == Document.STATUS_INVALID

    assert transferred_doc2.status == Document.STATUS_PENDING

    assert transferred_doc1.type == doc_type_national_id
    assert transferred_doc1.country == poland
    assert transferred_doc1.program == program

    assert transferred_doc2.type == doc_type_passport
    assert transferred_doc2.country == poland
    assert transferred_doc2.program == program

    assert transferred_doc1.individual == destination_individual
    assert transferred_doc2.individual == destination_individual

    assert transferred_doc1.rdi_merge_status == Individual.MERGED
    assert transferred_doc2.rdi_merge_status == Individual.MERGED


def test_update_individual_with_fixture_households(
    source_household: tuple[Household, Individual],
    destination_household: tuple[Household, Individual],
    poland: Country,
    program: Program,
) -> None:
    """Test that individual fields are copied from source to destination, excluding system fields."""
    source_individual = source_household[1]
    destination_individual = (
        destination_household[0].individuals(manager="all_objects").get(unicef_id="IND-00-0000.00134")
    )

    source_individual.full_name = "Source Full Name"
    source_individual.given_name = "Source"
    source_individual.middle_name = "Middle"
    source_individual.family_name = "Name"
    source_individual.marital_status = "MARRIED"
    source_individual.work_status = "YES"
    source_individual.email = "source@example.com"
    source_individual.save()

    destination_original_id = destination_individual.id
    destination_original_unicef_id = destination_individual.unicef_id
    destination_original_household_id = destination_individual.household_id

    detector = IdentificationKeyCollisionDetector(program)
    detector._update_individual(destination_individual, source_individual)

    destination_individual.refresh_from_db()

    assert destination_individual.full_name == "Source Full Name"
    assert destination_individual.given_name == "Source"
    assert destination_individual.middle_name == "Middle"
    assert destination_individual.family_name == "Name"
    assert destination_individual.marital_status == "MARRIED"
    assert destination_individual.work_status == "YES"
    assert destination_individual.email == "source@example.com"

    assert destination_individual.id == destination_original_id
    assert destination_individual.unicef_id == destination_original_unicef_id
    assert destination_individual.household_id == destination_original_household_id


def test_update_household_with_fixture_households(
    source_household: tuple[Household, Individual],
    destination_household: tuple[Household, Individual],
    program: Program,
) -> None:
    """Test that household fields are copied from source to destination, excluding system fields."""
    source_household_obj = source_household[0]
    destination_household_obj = destination_household[0]
    head_of_household = destination_household[1]

    # Save original values that should be preserved
    destination_original_id = destination_household_obj.id
    destination_original_unicef_id = destination_household_obj.unicef_id
    destination_original_program_id = destination_household_obj.program_id
    destination_original_rdi_status = destination_household_obj.rdi_merge_status

    # Modify source household data
    source_household_obj.size = 100
    source_household_obj.address = "Modified Source Address"
    source_household_obj.returnee = True
    source_household_obj.flex_fields = {"eggs": "MODIFIED_SOURCE"}
    source_household_obj.save()

    # Execute the update household method
    detector = IdentificationKeyCollisionDetector(program)
    detector._update_household(destination_household_obj, source_household_obj, head_of_household)

    # Refresh the destination household from DB
    destination_household_obj.refresh_from_db()

    # Verify fields were updated
    assert destination_household_obj.size == 100
    assert destination_household_obj.address == "Modified Source Address"
    assert destination_household_obj.returnee is True
    assert destination_household_obj.flex_fields.get("eggs") == "MODIFIED_SOURCE"

    # Verify excluded fields weren't modified
    assert destination_household_obj.id == destination_original_id
    assert destination_household_obj.unicef_id == destination_original_unicef_id
    assert destination_household_obj.program_id == destination_original_program_id
    assert destination_household_obj.rdi_merge_status == destination_original_rdi_status

    # Verify head of household relationship was maintained
    assert destination_household_obj.head_of_household == head_of_household


def test_update_household_collision(
    source_household: tuple[Household, Individual],
    destination_household: tuple[Household, Individual],
    poland: Country,
    program: Program,
) -> None:
    """Test complete collision detection and household merge process."""
    source_household_obj = source_household[0]
    destination_household_obj = destination_household[0]
    source_individual = source_household[1]
    destination_individual = destination_household[1]
    head_of_household_identification_key = source_individual.identification_key
    individual_to_keep_and_update = Individual.all_objects.get(
        household=destination_household_obj, identification_key="IND-KEY-002"
    )

    destination_household_obj.head_of_household = destination_individual
    destination_household_obj.save()

    IndividualRoleInHousehold.objects.create(
        individual=destination_individual,
        household=destination_household_obj,
        role="PRIMARY",
    )
    IndividualRoleInHousehold.objects.create(
        individual=source_individual, household=source_household_obj, role="PRIMARY"
    )
    primary_collector_identification_key = source_individual.identification_key

    _, additional_individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.9999",
            "business_area": program.business_area,
            "program": program,
            "rdi_merge_status": "PENDING",
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.9999",
                "business_area": program.business_area,
                "sex": FEMALE,
                "phone_no": "+48999888777",
                "full_name": "Additional Individual",
                "given_name": "Additional",
                "family_name": "Individual",
                "identification_key": "IND-KEY-999",
                "rdi_merge_status": "PENDING",
            },
        ],
    )
    additional_individual = additional_individuals[0]

    additional_individual.household = source_household_obj
    additional_individual.save()

    IndividualRoleInHousehold.objects.create(
        individual=additional_individual,
        household=source_household_obj,
        role="ALTERNATE",
    )

    source_household_obj.head_of_household = source_individual
    source_household_obj.save()
    source_household_obj.flex_fields = {"custom_field": "Source Value"}
    source_household_obj.save()

    destination_original_id = destination_household_obj.id
    destination_original_unicef_id = destination_household_obj.unicef_id
    additional_individual_key = additional_individual.identification_key

    program.collision_detector = IdentificationKeyCollisionDetector
    program.save()

    detector = IdentificationKeyCollisionDetector(program)
    detector.initialize()

    collision_id = detector.detect_collision(source_household_obj)
    assert collision_id == str(destination_household_obj.id)

    detector.update_household(source_household_obj)

    destination_household_obj = Household.objects.get(id=destination_original_id)

    additional_individual = Individual.objects.get(identification_key=additional_individual_key)

    # 2 accounts exist: one from source (active), one from withdrawn individual (deactivated)
    assert Account.all_objects.count() == 2
    # The source account is active
    source_account = Account.objects.get(number="ACC-123456")
    assert source_account.active is True
    # The withdrawn individual's account is deactivated
    withdrawn_account = Account.objects.get(number="999")
    assert withdrawn_account.active is False

    assert destination_household_obj.id == destination_original_id
    assert destination_household_obj.unicef_id == destination_original_unicef_id

    assert (
        destination_household_obj.head_of_household.id
        == Individual.objects.get(identification_key=head_of_household_identification_key).id
    )

    assert "custom_field" in destination_household_obj.flex_fields
    assert destination_household_obj.flex_fields["custom_field"] == "Source Value"

    assert additional_individual.household_id == destination_household_obj.id

    roles = IndividualRoleInHousehold.objects.filter(household=destination_household_obj)
    assert roles.filter(role="PRIMARY").exists()
    assert roles.get(role="PRIMARY").individual.identification_key == primary_collector_identification_key
    assert roles.filter(role="ALTERNATE").exists()
    assert roles.get(role="ALTERNATE").individual.identification_key == additional_individual.identification_key

    assert Individual.objects.filter(id=individual_to_keep_and_update.id).exists()


def test_collision_withdraws_removed_individual_instead_of_deleting(
    program: Program,
    admin1: Area,
) -> None:
    """Test that individuals not in source are withdrawn with REMOVED_BY_COLLISION relationship, not deleted."""
    destination_household, destination_individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-DEST-001",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "identification_key": "COLLISION-KEY-001",
        },
        individuals_data=[
            {
                "unicef_id": "IND-DEST-001",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
                "identification_key": "IND-KEY-001",
                "relationship": "HEAD",
            },
            {
                "unicef_id": "IND-DEST-002",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": FEMALE,
                "identification_key": "IND-KEY-TO-REMOVE",
                "relationship": "WIFE_HUSBAND",
            },
        ],
    )

    individual_to_remove = destination_individuals[1]
    assert individual_to_remove.identification_key == "IND-KEY-TO-REMOVE"
    original_relationship = individual_to_remove.relationship

    destination_household.head_of_household = individual_to_remove
    destination_household.save()

    IndividualRoleInHousehold.objects.create(
        individual=individual_to_remove,
        household=destination_household,
        role="PRIMARY",
    )

    source_household, source_individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-SRC-001",
            "rdi_merge_status": "PENDING",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "identification_key": "COLLISION-KEY-001",
        },
        individuals_data=[
            {
                "unicef_id": "IND-SRC-001",
                "rdi_merge_status": "PENDING",
                "business_area": program.business_area,
                "sex": MALE,
                "identification_key": "IND-KEY-001",
            },
        ],
    )

    source_household.head_of_household = source_individuals[0]
    source_household.save()

    IndividualRoleInHousehold.objects.create(
        individual=source_individuals[0],
        household=source_household,
        role="PRIMARY",
    )

    program.collision_detector = IdentificationKeyCollisionDetector
    program.save()

    detector = IdentificationKeyCollisionDetector(program)
    detector.initialize()

    collision_id = detector.detect_collision(source_household)
    assert collision_id == str(destination_household.id)

    detector.update_household(source_household)

    individual_to_remove.refresh_from_db()
    assert Individual.all_objects.filter(id=individual_to_remove.id).exists(), (
        "Individual should NOT be deleted, only withdrawn"
    )

    assert individual_to_remove.relationship == REMOVED_BY_COLLISION

    assert "removed_by_collision_detector" in individual_to_remove.internal_data
    collision_data = individual_to_remove.internal_data["removed_by_collision_detector"]
    assert collision_data["previous_relationship"] == original_relationship
    assert "PRIMARY" in collision_data["previous_roles"]
    assert collision_data["was_head_of_household"] is True

    assert individual_to_remove.withdrawn is True
    assert individual_to_remove.withdrawn_date is not None

    assert individual_to_remove.household_id == destination_household.id

    assert not IndividualRoleInHousehold.objects.filter(
        individual=individual_to_remove, household=destination_household
    ).exists()


def test_collision_skips_withdraw_if_individual_already_withdrawn(
    program: Program,
    admin1: Area,
) -> None:
    """Test that collision detector does not call withdraw() again if individual is already withdrawn."""
    from django.utils import timezone

    destination_household, destination_individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-DEST-002",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "identification_key": "COLLISION-KEY-002",
        },
        individuals_data=[
            {
                "unicef_id": "IND-DEST-003",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
                "identification_key": "IND-KEY-003",
                "relationship": "HEAD",
            },
            {
                "unicef_id": "IND-DEST-004",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": FEMALE,
                "identification_key": "IND-KEY-ALREADY-WITHDRAWN",
                "relationship": "WIFE_HUSBAND",
            },
        ],
    )

    already_withdrawn_individual = destination_individuals[1]
    assert already_withdrawn_individual.identification_key == "IND-KEY-ALREADY-WITHDRAWN"
    original_relationship = already_withdrawn_individual.relationship

    destination_household.head_of_household = already_withdrawn_individual
    destination_household.save()

    IndividualRoleInHousehold.objects.create(
        individual=already_withdrawn_individual,
        household=destination_household,
        role="PRIMARY",
    )

    original_withdrawn_date = timezone.now() - timezone.timedelta(days=30)
    already_withdrawn_individual.withdrawn = True
    already_withdrawn_individual.withdrawn_date = original_withdrawn_date
    already_withdrawn_individual.save()

    source_household, source_individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-SRC-002",
            "rdi_merge_status": "PENDING",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "identification_key": "COLLISION-KEY-002",
        },
        individuals_data=[
            {
                "unicef_id": "IND-SRC-003",
                "rdi_merge_status": "PENDING",
                "business_area": program.business_area,
                "sex": MALE,
                "identification_key": "IND-KEY-003",
            },
        ],
    )

    source_household.head_of_household = source_individuals[0]
    source_household.save()

    IndividualRoleInHousehold.objects.create(
        individual=source_individuals[0],
        household=source_household,
        role="PRIMARY",
    )

    program.collision_detector = IdentificationKeyCollisionDetector
    program.save()

    detector = IdentificationKeyCollisionDetector(program)
    detector.initialize()
    detector.update_household(source_household)

    already_withdrawn_individual.refresh_from_db()

    assert Individual.all_objects.filter(id=already_withdrawn_individual.id).exists()
    assert already_withdrawn_individual.relationship == REMOVED_BY_COLLISION
    assert "removed_by_collision_detector" in already_withdrawn_individual.internal_data
    collision_data = already_withdrawn_individual.internal_data["removed_by_collision_detector"]
    assert collision_data["previous_relationship"] == original_relationship
    assert "PRIMARY" in collision_data["previous_roles"]
    assert collision_data["was_head_of_household"] is True

    assert already_withdrawn_individual.withdrawn is True
    assert already_withdrawn_individual.withdrawn_date == original_withdrawn_date

    assert not IndividualRoleInHousehold.objects.filter(
        individual=already_withdrawn_individual, household=destination_household
    ).exists()
