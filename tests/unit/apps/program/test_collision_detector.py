import pytest
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import create_household_and_individuals

from hct_mis_api.apps.geo.models import Area, AreaType, Country
from hct_mis_api.apps.household.models import (
    FEMALE,
    MALE,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Account, AccountType
from hct_mis_api.apps.program.collision_detectors import (
    IdentificationKeyCollisionDetector,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture()
def poland() -> Country:
    return Country.objects.create(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")


@pytest.fixture()
def germany() -> Country:
    return Country.objects.create(name="Germany", iso_code2="DE", iso_code3="DEU", iso_num="276")


@pytest.fixture()
def program(poland: Country, germany: Country) -> Program:
    business_area = create_afghanistan()
    business_area.countries.add(poland, germany)

    program = ProgramFactory(name="Test Program for Household", status=Program.ACTIVE, business_area=business_area)
    return program


@pytest.fixture()
def admin1(state: AreaType) -> Area:
    return Area.objects.create(name="Kabul", area_type=state, p_code="AF11")


@pytest.fixture()
def admin2(district: AreaType) -> Area:
    return Area.objects.create(name="Kabul1", area_type=district, p_code="AF1115")


@pytest.fixture()
def state(poland: Country) -> AreaType:
    return AreaType.objects.create(name="State", country=poland)


@pytest.fixture()
def district(poland: Country, state: AreaType) -> AreaType:
    return AreaType.objects.create(name="District", parent=state, country=poland)


@pytest.fixture()
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
        individual=ind, number="ACC-123456", rdi_merge_status=Individual.MERGED, account_type=account_type
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
    Account.objects.create(individual=ind, number="999", rdi_merge_status=Individual.MERGED, account_type=account_type)
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
    """Test _update_individual_identities method using source and destination household fixtures.

    Plan:
    1. Setup:
       - Get individuals from source and destination households
       - Create partner for identities
       - Create multiple identities for source individual (to test all transferring)
       - Create one identity for destination individual (to test deletion)

    2. Test:
       - Call _update_individual_identities to transfer identities from source to destination
       - Verify source identities were transferred to destination individual
       - Verify destination identities were deleted
       - Verify identity attributes (like partner) were preserved in transfer

    3. Assertions:
       - Check destination's original identity no longer exists
       - Check number of identities transferred matches expected count
       - Check identity numbers match what was expected
       - Check all identity attributes were maintained
    """
    source_individual = source_household[1]
    destination_individual = destination_household[1]

    from hct_mis_api.apps.account.models import Partner

    partner = Partner.objects.create(name="Test Partner")

    IndividualIdentity.objects.create(
        individual=source_individual, partner=partner, country=poland, number="SOURCE-ID-123"
    )

    IndividualIdentity.objects.create(
        individual=source_individual, partner=partner, country=poland, number="SOURCE-ID-456"
    )

    dest_identity = IndividualIdentity.objects.create(
        individual=destination_individual, partner=partner, country=poland, number="DEST-ID-789"
    )

    program.collision_detection_enabled = True
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
    """Test _update_documents method using source and destination household fixtures.

    Plan:
    1. Setup:
       - Get individuals from source and destination households
       - Create document types for testing
       - Create multiple documents for source individual with different statuses
       - Create documents for destination individual with matching and non-matching numbers

    2. Test:
       - Call _update_documents to transfer documents from source to destination
       - Verify source documents were transferred to destination individual
       - Verify destination documents were deleted
       - Verify document statuses were preserved for matching documents
       - Verify document attributes were maintained

    3. Assertions:
       - Check destination's original documents no longer exist
       - Check number of documents transferred matches expected count
       - Check document numbers match what was expected
       - Check document statuses were preserved correctly
       - Check all document attributes were maintained
    """
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

    program.collision_detection_enabled = True
    program.save()

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
    """Test _update_individual method using source and destination household fixtures.

    Plan:
    1. Setup:
       - Get individuals from source and destination households
       - Set different field values on source individual to be transferred
       - Set initial values on destination individual that should be overwritten

    2. Test:
       - Call _update_individual to transfer data from source to destination
       - Verify fields are properly updated in the destination individual
       - Verify fields in the exclude list remain unchanged

    3. Assertions:
       - Check that data was correctly transferred from source to destination
       - Check that excluded fields were not modified
    """
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

    program.collision_detection_enabled = True
    program.save()

    detector = IdentificationKeyCollisionDetector(program)
    print(destination_individual, source_individual)
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
    """Test _update_household method using source and destination household fixtures.

    Plan:
    1. Setup:
       - Get households from source and destination fixtures
       - Set different field values on source household to be transferred
       - Set initial values on destination household that should be overwritten
       - Store the head of household for preservation

    2. Test:
       - Call _update_household to transfer data from source to destination
       - Verify fields are properly updated in the destination household
       - Verify fields in the exclude list remain unchanged

    3. Assertions:
       - Check that data was correctly transferred from source to destination
       - Check that excluded fields were not modified
       - Check that head of household relationship was maintained
    """
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

    # Enable collision detection
    program.collision_detection_enabled = True
    program.save()

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
    """Test the update_household method from IdentificationKeyCollisionDetector which handles household collisions.

    This test verifies the complete process of detecting and resolving a household collision:

    Plan:
    1. Setup:
       - Get source and destination households with same identification key
       - Set up the collision detector with appropriate program
       - Create different individuals in source and destination to test merging
       - Assign different roles to individuals in both households

    2. Test:
       - Initialize the detector and detect the collision
       - Execute the update_household method to merge households
       - Verify the collision is properly detected and resolved

    3. Assertions:
       - Verify collision is correctly detected using identification key
       - Verify individuals were transferred properly
       - Verify roles were preserved
       - Verify system fields remain unchanged
       - Verify data from source household was copied to destination household
    """
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
        individual=destination_individual, household=destination_household_obj, role="PRIMARY"
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
        individual=additional_individual, household=source_household_obj, role="ALTERNATE"
    )

    source_household_obj.head_of_household = source_individual
    source_household_obj.save()
    source_household_obj.flex_fields = {"custom_field": "Source Value"}
    source_household_obj.save()

    destination_original_id = destination_household_obj.id
    destination_original_unicef_id = destination_household_obj.unicef_id
    additional_individual_key = additional_individual.identification_key

    program.collision_detection_enabled = True
    program.collision_detector = IdentificationKeyCollisionDetector
    program.save()

    detector = IdentificationKeyCollisionDetector(program)
    detector.initialize()

    collision_id = detector.detect_collision(source_household_obj)
    assert collision_id == str(destination_household_obj.id)

    detector.update_household(source_household_obj)

    destination_household_obj = Household.objects.get(id=destination_original_id)

    additional_individual = Individual.objects.get(identification_key=additional_individual_key)

    assert Account.all_objects.count() == 1
    account = Account.objects.first()

    assert account.number == "ACC-123456"

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
