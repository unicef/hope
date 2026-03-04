"""Tests for PDU online edit bulk merge functionality."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeForPDUFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    PDUOnlineEditFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.models import BusinessArea, PDUOnlineEdit, PeriodicFieldData, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def partner(db: Any) -> Any:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Any) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def rdi(afghanistan: BusinessArea) -> Any:
    return RegistrationDataImportFactory(business_area=afghanistan)


@pytest.fixture
def household_and_individuals(afghanistan: BusinessArea, program: Program, rdi: Any) -> tuple:
    individual1 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=None,
    )
    individual2 = IndividualFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        household=None,
    )

    household = HouseholdFactory(
        business_area=afghanistan,
        program=program,
        registration_data_import=rdi,
        head_of_household=None,
    )
    household.head_of_household = individual1
    household.save()

    individual1.household = household
    individual1.save()
    individual2.household = household
    individual2.save()

    return household, [individual1, individual2]


@pytest.fixture
def household(household_and_individuals: tuple) -> Any:
    return household_and_individuals[0]


@pytest.fixture
def individuals(household_and_individuals: tuple) -> list:
    return household_and_individuals[1]


@pytest.fixture
def individual1(individuals: list) -> Any:
    return individuals[0]


@pytest.fixture
def individual2(individuals: list) -> Any:
    return individuals[1]


@pytest.fixture
def string_attribute(program: Program) -> Any:
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="String Attribute",
        pdu_data=PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round 1", "Round 2"],
        ),
    )


@pytest.fixture
def decimal_attribute(program: Program) -> Any:
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="Decimal Attribute",
        pdu_data=PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        ),
    )


@pytest.fixture
def boolean_attribute(program: Program) -> Any:
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="Boolean Attribute",
        pdu_data=PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.BOOL,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        ),
    )


@pytest.fixture
def date_attribute(program: Program) -> Any:
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="Date Attribute",
        pdu_data=PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        ),
    )


@pytest.fixture
def setup_individuals_with_pdu(
    individual1: Any,
    individual2: Any,
    program: Program,
    string_attribute: Any,
    decimal_attribute: Any,
    boolean_attribute: Any,
    date_attribute: Any,
) -> None:
    populate_pdu_with_null_values(program, individual1.flex_fields)
    populate_pdu_with_null_values(program, individual2.flex_fields)
    individual1.save()
    individual2.save()


@pytest.fixture
def pdu_edit_approved_1(
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    individual1: Any,
    string_attribute: Any,
    decimal_attribute: Any,
    setup_individuals_with_pdu: None,
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Approved Edit 1",
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
        edit_data=[
            {
                "individual_uuid": str(individual1.id),
                "pdu_fields": {
                    string_attribute.name: {
                        "value": "Test String Value 1",
                        "subtype": PeriodicFieldData.STRING,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": True,
                    },
                    decimal_attribute.name: {
                        "value": 123.45,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": True,
                    },
                },
            }
        ],
    )


@pytest.fixture
def pdu_edit_approved_2(
    afghanistan: BusinessArea,
    program: Program,
    user: User,
    individual2: Any,
    boolean_attribute: Any,
    date_attribute: Any,
    setup_individuals_with_pdu: None,
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Approved Edit 2",
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
        edit_data=[
            {
                "individual_uuid": str(individual2.id),
                "pdu_fields": {
                    boolean_attribute.name: {
                        "value": True,
                        "subtype": PeriodicFieldData.BOOL,
                        "round_number": 1,
                        "collection_date": "2024-01-16",
                        "is_editable": True,
                    },
                    date_attribute.name: {
                        "value": "2024-01-20",
                        "subtype": PeriodicFieldData.DATE,
                        "round_number": 1,
                        "collection_date": "2024-01-16",
                        "is_editable": True,
                    },
                },
            }
        ],
    )


@pytest.fixture
def pdu_edit_approved_not_authorized(
    afghanistan: BusinessArea,
    program: Program,
    individual2: Any,
    boolean_attribute: Any,
    date_attribute: Any,
    setup_individuals_with_pdu: None,
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Approved Edit Not Authorized",
        status=PDUOnlineEdit.Status.APPROVED,
        edit_data=[
            {
                "individual_uuid": str(individual2.id),
                "pdu_fields": {
                    boolean_attribute.name: {
                        "value": True,
                        "subtype": PeriodicFieldData.BOOL,
                        "round_number": 1,
                        "collection_date": "2024-01-16",
                        "is_editable": True,
                    },
                    date_attribute.name: {
                        "value": "2024-01-20",
                        "subtype": PeriodicFieldData.DATE,
                        "round_number": 1,
                        "collection_date": "2024-01-16",
                        "is_editable": True,
                    },
                },
            }
        ],
    )


@pytest.fixture
def pdu_edit_ready(
    afghanistan: BusinessArea, program: Program, user: User, setup_individuals_with_pdu: None
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Ready Edit",
        status=PDUOnlineEdit.Status.READY,
        authorized_users=[user],
    )


@pytest.fixture
def pdu_edit_new(
    afghanistan: BusinessArea, program: Program, user: User, setup_individuals_with_pdu: None
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="New Edit",
        status=PDUOnlineEdit.Status.NEW,
        authorized_users=[user],
    )


@pytest.fixture
def pdu_edit_merged(
    afghanistan: BusinessArea, program: Program, user: User, setup_individuals_with_pdu: None
) -> PDUOnlineEdit:
    return PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Already Merged Edit",
        status=PDUOnlineEdit.Status.MERGED,
        authorized_users=[user],
    )


@pytest.fixture
def url_bulk_merge(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-bulk-merge",
        kwargs={"business_area_slug": afghanistan.slug, "program_slug": program.slug},
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_ONLINE_MERGE], status.HTTP_200_OK),
        ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_403_FORBIDDEN),
        ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_bulk_merge_permissions(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_1: PDUOnlineEdit,
    pdu_edit_approved_2: PDUOnlineEdit,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, permissions, afghanistan, program)

    data = {"ids": [pdu_edit_approved_1.id, pdu_edit_approved_2.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)
    assert response.status_code == expected_status


def test_bulk_merge_check_authorized_user_single_edit(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_not_authorized: PDUOnlineEdit,
    individual1: Any,
    string_attribute: Any,
    decimal_attribute: Any,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Verify initial state of individual data
    individual1.refresh_from_db()
    initial_string_value = individual1.flex_fields[string_attribute.name]["1"]["value"]
    initial_decimal_value = individual1.flex_fields[decimal_attribute.name]["1"]["value"]
    assert initial_string_value is None
    assert initial_decimal_value is None

    # Attempt to merge an edit the user is not authorized for
    data = {"ids": [pdu_edit_approved_not_authorized.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    response_json = response.json()
    assert (
        f"You are not an authorized user for PDU Online Edit: {pdu_edit_approved_not_authorized.id}"
        in response_json["detail"]
    )

    # Verify the edit was not merged
    pdu_edit_approved_not_authorized.refresh_from_db()
    assert pdu_edit_approved_not_authorized.status == PDUOnlineEdit.Status.APPROVED

    # Verify individual data was not updated
    individual1.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] == initial_string_value
    assert individual1.flex_fields[decimal_attribute.name]["1"]["value"] == initial_decimal_value


def test_bulk_merge_check_authorized_user_mixed(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_not_authorized: PDUOnlineEdit,
    pdu_edit_approved_1: PDUOnlineEdit,
    individual1: Any,
    individual2: Any,
    string_attribute: Any,
    decimal_attribute: Any,
    boolean_attribute: Any,
    date_attribute: Any,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Verify initial state of individual data for both individuals
    individual1.refresh_from_db()
    individual2.refresh_from_db()
    initial_string_value = individual1.flex_fields[string_attribute.name]["1"]["value"]
    initial_decimal_value = individual1.flex_fields[decimal_attribute.name]["1"]["value"]
    initial_boolean_value = individual2.flex_fields[boolean_attribute.name]["1"]["value"]
    initial_date_value = individual2.flex_fields[date_attribute.name]["1"]["value"]
    assert initial_string_value is None
    assert initial_decimal_value is None
    assert initial_boolean_value is None
    assert initial_date_value is None

    # Attempt to merge an edit the user is not authorized for
    data = {"ids": [pdu_edit_approved_not_authorized.id, pdu_edit_approved_1.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    response_json = response.json()
    assert (
        f"You are not an authorized user for PDU Online Edit: {pdu_edit_approved_not_authorized.id}"
        in response_json["detail"]
    )

    # Verify no edits were merged
    pdu_edit_approved_not_authorized.refresh_from_db()
    pdu_edit_approved_1.refresh_from_db()
    assert pdu_edit_approved_not_authorized.status == PDUOnlineEdit.Status.APPROVED
    assert pdu_edit_approved_1.status == PDUOnlineEdit.Status.APPROVED

    # Verify individual data was not updated for both individuals
    individual1.refresh_from_db()
    individual2.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] == initial_string_value
    assert individual1.flex_fields[decimal_attribute.name]["1"]["value"] == initial_decimal_value
    assert individual2.flex_fields[boolean_attribute.name]["1"]["value"] == initial_boolean_value
    assert individual2.flex_fields[date_attribute.name]["1"]["value"] == initial_date_value


def test_bulk_merge_success(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_1: PDUOnlineEdit,
    pdu_edit_approved_2: PDUOnlineEdit,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    data = {"ids": [pdu_edit_approved_1.id, pdu_edit_approved_2.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "2 PDU Online Edits queued for merging."}

    # Verify edits status changed to MERGED
    pdu_edit_approved_1.refresh_from_db()
    pdu_edit_approved_2.refresh_from_db()

    assert pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED
    assert pdu_edit_approved_2.status == PDUOnlineEdit.Status.MERGED


def test_bulk_merge_single_edit(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_1: PDUOnlineEdit,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    data = {"ids": [pdu_edit_approved_1.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "1 PDU Online Edits queued for merging."}

    pdu_edit_approved_1.refresh_from_db()
    assert pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED


def test_bulk_merge_invalid_status(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_1: PDUOnlineEdit,
    pdu_edit_ready: PDUOnlineEdit,
    individual1: Any,
    string_attribute: Any,
    decimal_attribute: Any,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Verify initial state of individual data
    individual1.refresh_from_db()
    initial_string_value = individual1.flex_fields[string_attribute.name]["1"]["value"]
    initial_decimal_value = individual1.flex_fields[decimal_attribute.name]["1"]["value"]
    assert initial_string_value is None
    assert initial_decimal_value is None

    # Try to merge edits that are not in APPROVED status
    data = {"ids": [pdu_edit_approved_1.id, pdu_edit_ready.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "PDU Online Edit is not in the 'Approved' status and cannot be merged." in response_json[0]

    # Verify no edits were merged
    pdu_edit_approved_1.refresh_from_db()
    pdu_edit_ready.refresh_from_db()
    assert pdu_edit_approved_1.status == PDUOnlineEdit.Status.APPROVED
    assert pdu_edit_ready.status == PDUOnlineEdit.Status.READY

    # Verify individual data was not updated
    individual1.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] == initial_string_value
    assert individual1.flex_fields[decimal_attribute.name]["1"]["value"] == initial_decimal_value


def test_bulk_merge_mixed_statuses(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_1: PDUOnlineEdit,
    pdu_edit_ready: PDUOnlineEdit,
    pdu_edit_new: PDUOnlineEdit,
    pdu_edit_merged: PDUOnlineEdit,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Try to merge mix of APPROVED, READY, NEW, and MERGED edits
    data = {
        "ids": [
            pdu_edit_approved_1.id,
            pdu_edit_ready.id,
            pdu_edit_new.id,
            pdu_edit_merged.id,
        ]
    }
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "PDU Online Edit is not in the 'Approved' status and cannot be merged." in response_json[0]


def test_bulk_merge_empty_ids(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    data = {"ids": []}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_bulk_merge_non_existent_ids(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    non_existent_id = 99999
    data = {"ids": [non_existent_id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert "One or more PDU online edits not found." in response_json[0]


def test_bulk_merge_preserves_other_fields(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_1: PDUOnlineEdit,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Store original values
    original_name = pdu_edit_approved_1.name
    original_created_by = pdu_edit_approved_1.created_by
    original_created_at = pdu_edit_approved_1.created_at
    original_number_of_records = pdu_edit_approved_1.number_of_records
    original_approved_by = pdu_edit_approved_1.approved_by
    original_approved_at = pdu_edit_approved_1.approved_at

    data = {"ids": [pdu_edit_approved_1.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_200_OK

    pdu_edit_approved_1.refresh_from_db()

    # Verify only status changed
    assert pdu_edit_approved_1.name == original_name
    assert pdu_edit_approved_1.created_by == original_created_by
    assert pdu_edit_approved_1.created_at == original_created_at
    assert pdu_edit_approved_1.number_of_records == original_number_of_records
    assert pdu_edit_approved_1.approved_by == original_approved_by
    assert pdu_edit_approved_1.approved_at == original_approved_at

    # Verify status changed to MERGED
    assert pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED


def test_bulk_merge_updates_individual_data_string_and_decimal(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_1: PDUOnlineEdit,
    individual1: Any,
    string_attribute: Any,
    decimal_attribute: Any,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Verify initial state - flex_fields should be null/empty for these fields
    individual1.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] is None
    assert individual1.flex_fields[decimal_attribute.name]["1"]["value"] is None

    # Perform bulk merge
    data = {"ids": [pdu_edit_approved_1.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_200_OK
    pdu_edit_approved_1.refresh_from_db()
    assert pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED

    # Verify individual data was updated
    individual1.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] == "Test String Value 1"
    assert individual1.flex_fields[string_attribute.name]["1"]["collection_date"] == "2024-01-15"
    assert individual1.flex_fields[decimal_attribute.name]["1"]["value"] == 123.45
    assert individual1.flex_fields[decimal_attribute.name]["1"]["collection_date"] == "2024-01-15"


def test_bulk_merge_updates_individual_data_boolean_and_date(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_2: PDUOnlineEdit,
    individual2: Any,
    boolean_attribute: Any,
    date_attribute: Any,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Verify initial state - flex_fields should be null/empty for these fields
    individual2.refresh_from_db()
    assert individual2.flex_fields[boolean_attribute.name]["1"]["value"] is None
    assert individual2.flex_fields[date_attribute.name]["1"]["value"] is None

    # Perform bulk merge
    data = {"ids": [pdu_edit_approved_2.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_200_OK
    pdu_edit_approved_2.refresh_from_db()
    assert pdu_edit_approved_2.status == PDUOnlineEdit.Status.MERGED

    # Verify individual data was updated
    individual2.refresh_from_db()
    assert individual2.flex_fields[boolean_attribute.name]["1"]["value"] is True
    assert individual2.flex_fields[boolean_attribute.name]["1"]["collection_date"] == "2024-01-16"
    assert individual2.flex_fields[date_attribute.name]["1"]["value"] == "2024-01-20"
    assert individual2.flex_fields[date_attribute.name]["1"]["collection_date"] == "2024-01-16"


def test_bulk_merge_multiple_edits_updates_multiple_individuals(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    pdu_edit_approved_1: PDUOnlineEdit,
    pdu_edit_approved_2: PDUOnlineEdit,
    individual1: Any,
    individual2: Any,
    string_attribute: Any,
    boolean_attribute: Any,
    decimal_attribute: Any,
    date_attribute: Any,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Verify initial state
    individual1.refresh_from_db()
    individual2.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] is None
    assert individual2.flex_fields[boolean_attribute.name]["1"]["value"] is None

    # Perform bulk merge for both edits
    data = {"ids": [pdu_edit_approved_1.id, pdu_edit_approved_2.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_200_OK

    # Verify both edits were processed
    pdu_edit_approved_1.refresh_from_db()
    pdu_edit_approved_2.refresh_from_db()
    assert pdu_edit_approved_1.status == PDUOnlineEdit.Status.MERGED
    assert pdu_edit_approved_2.status == PDUOnlineEdit.Status.MERGED

    individual1.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] == "Test String Value 1"
    assert individual1.flex_fields[decimal_attribute.name]["1"]["value"] == 123.45

    individual2.refresh_from_db()
    assert individual2.flex_fields[boolean_attribute.name]["1"]["value"] is True
    assert individual2.flex_fields[date_attribute.name]["1"]["value"] == "2024-01-20"


def test_bulk_merge_with_non_editable_fields_skips_update(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual1: Any,
    string_attribute: Any,
    setup_individuals_with_pdu: None,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Create edit with non-editable field
    pdu_edit_non_editable = PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        name="Non-Editable Edit",
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
        edit_data=[
            {
                "individual_uuid": str(individual1.id),
                "pdu_fields": {
                    string_attribute.name: {
                        "value": "Should Not Be Updated",
                        "subtype": PeriodicFieldData.STRING,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": False,  # Non-editable field
                    }
                },
            }
        ],
    )

    # Verify initial state
    individual1.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] is None

    # Perform bulk merge
    data = {"ids": [pdu_edit_non_editable.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    assert response.status_code == status.HTTP_200_OK
    pdu_edit_non_editable.refresh_from_db()
    assert pdu_edit_non_editable.status == PDUOnlineEdit.Status.MERGED

    # Verify individual data was NOT updated (since field was not editable)
    individual1.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] is None


def test_bulk_merge_with_existing_data_prevents_overwrite(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual1: Any,
    string_attribute: Any,
    decimal_attribute: Any,
    setup_individuals_with_pdu: None,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # Merge fails when trying to overwrite existing data.
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    # Pre-populate individual with existing data
    individual1.flex_fields[string_attribute.name]["1"]["value"] = "Existing Value"
    individual1.flex_fields[string_attribute.name]["1"]["collection_date"] = "2024-01-10"
    individual1.save()

    # Verify initial state - individual has existing data that should not be overwritten
    initial_value = individual1.flex_fields[string_attribute.name]["1"]["value"]
    initial_collection_date = individual1.flex_fields[string_attribute.name]["1"]["collection_date"]
    assert initial_value == "Existing Value"
    assert initial_collection_date == "2024-01-10"

    # Create edit that would overwrite existing data
    pdu_edit = PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
        edit_data=[
            {
                "individual_uuid": str(individual1.id),
                "pdu_fields": {
                    string_attribute.name: {
                        "value": "New Value",
                        "subtype": PeriodicFieldData.STRING,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": True,
                    },
                    decimal_attribute.name: {
                        "value": 999.99,
                        "subtype": PeriodicFieldData.DECIMAL,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": True,
                    },
                },
            }
        ],
    )

    # Attempt to merge edit that would overwrite existing data
    data = {"ids": [pdu_edit.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)

    # Should return 200 (task queued successfully), but the task should fail
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json == {"message": "1 PDU Online Edits queued for merging."}
    pdu_edit.refresh_from_db()
    assert pdu_edit.status == PDUOnlineEdit.Status.FAILED_MERGE

    # Verify individual data was NOT updated
    individual1.refresh_from_db()
    assert individual1.flex_fields[string_attribute.name]["1"]["value"] == initial_value
    assert individual1.flex_fields[string_attribute.name]["1"]["collection_date"] == initial_collection_date
    assert individual1.flex_fields[decimal_attribute.name]["1"]["value"] is None


def test_bulk_merge_validate_value_string_invalid(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual1: Any,
    string_attribute: Any,
    setup_individuals_with_pdu: None,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    pdu_edit = PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
        edit_data=[
            {
                "individual_uuid": str(individual1.id),
                "pdu_fields": {
                    string_attribute.name: {
                        "value": 123,  # Invalid: should be string
                        "subtype": PeriodicFieldData.STRING,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": True,
                    }
                },
            }
        ],
    )

    data = {"ids": [pdu_edit.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)
    assert response.status_code == status.HTTP_200_OK

    pdu_edit.refresh_from_db()
    assert pdu_edit.status == PDUOnlineEdit.Status.FAILED_MERGE


def test_bulk_merge_validate_value_bool_invalid(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual1: Any,
    boolean_attribute: Any,
    setup_individuals_with_pdu: None,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    pdu_edit = PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
        edit_data=[
            {
                "individual_uuid": str(individual1.id),
                "pdu_fields": {
                    boolean_attribute.name: {
                        "value": "true",  # Invalid: should be boolean
                        "subtype": PeriodicFieldData.BOOL,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": True,
                    }
                },
            }
        ],
    )

    data = {"ids": [pdu_edit.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)
    assert response.status_code == status.HTTP_200_OK

    pdu_edit.refresh_from_db()
    assert pdu_edit.status == PDUOnlineEdit.Status.FAILED_MERGE


def test_bulk_merge_validate_value_decimal_invalid(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual1: Any,
    decimal_attribute: Any,
    setup_individuals_with_pdu: None,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    pdu_edit = PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
        edit_data=[
            {
                "individual_uuid": str(individual1.id),
                "pdu_fields": {
                    decimal_attribute.name: {
                        "value": "123.45",  # Invalid: should be number
                        "subtype": PeriodicFieldData.DECIMAL,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": True,
                    }
                },
            }
        ],
    )

    data = {"ids": [pdu_edit.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)
    assert response.status_code == status.HTTP_200_OK

    pdu_edit.refresh_from_db()
    assert pdu_edit.status == PDUOnlineEdit.Status.FAILED_MERGE


def test_bulk_merge_validate_value_date_invalid(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    individual1: Any,
    date_attribute: Any,
    setup_individuals_with_pdu: None,
    url_bulk_merge: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PDU_ONLINE_MERGE],
        afghanistan,
        program,
    )

    pdu_edit = PDUOnlineEditFactory(
        business_area=afghanistan,
        program=program,
        status=PDUOnlineEdit.Status.APPROVED,
        authorized_users=[user],
        edit_data=[
            {
                "individual_uuid": str(individual1.id),
                "pdu_fields": {
                    date_attribute.name: {
                        "value": "2024/01/15",  # Invalid: wrong format
                        "subtype": PeriodicFieldData.DATE,
                        "round_number": 1,
                        "collection_date": "2024-01-15",
                        "is_editable": True,
                    }
                },
            }
        ],
    )

    data = {"ids": [pdu_edit.id]}
    response = authenticated_client.post(url_bulk_merge, data=data)
    assert response.status_code == status.HTTP_200_OK

    pdu_edit.refresh_from_db()
    assert pdu_edit.status == PDUOnlineEdit.Status.FAILED_MERGE
