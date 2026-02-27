import copy
from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    CountryFactory,
    DataCollectingTypeFactory,
    FlexibleAttributeForPDUFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    PeriodicFieldDataFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import (
    Area,
    BeneficiaryGroup,
    BusinessArea,
    Country,
    DataCollectingType,
    FlexibleAttribute,
    Partner,
    PeriodicFieldData,
    Program,
    User,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def ukraine() -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine")


@pytest.fixture
def unicef_partner() -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=unicef_partner)


@pytest.fixture
def unicef_partner_in_afghanistan(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF Partner for afghanistan", parent=unicef_partner)


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def country(afghanistan: BusinessArea) -> Country:
    country = CountryFactory()
    country.business_areas.set([afghanistan])
    return country


@pytest.fixture
def area1(country: Country) -> Area:
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, area_type=admin_type, p_code="AF01U", name="Area1")


@pytest.fixture
def area2(country: Country) -> Area:
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, area_type=admin_type, p_code="AF02U", name="Area2")


@pytest.fixture
def dct_standard() -> DataCollectingType:
    return DataCollectingTypeFactory(label="Full", code="full", type=DataCollectingType.Type.STANDARD)


@pytest.fixture
def dct_social() -> DataCollectingType:
    return DataCollectingTypeFactory(label="SW Full", code="sw_full", type=DataCollectingType.Type.SOCIAL)


@pytest.fixture
def bg_household() -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Household", master_detail=True)


@pytest.fixture
def bg_sw() -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Social Worker", master_detail=False)


@pytest.fixture
def initial_program_data(dct_standard: DataCollectingType, bg_household: BeneficiaryGroup) -> dict:
    return {
        "name": "Test Program To Update",
        "description": "Initial description.",
        "start_date": "2030-01-01",
        "end_date": "2033-12-31",
        "sector": Program.CHILD_PROTECTION,
        "data_collecting_type": dct_standard,
        "beneficiary_group": bg_household,
        "budget": 100000,
        "population_goal": 100,
        "status": Program.DRAFT,
        "partner_access": Program.NONE_PARTNERS_ACCESS,
        "cash_plus": False,
        "frequency_of_payments": Program.REGULAR,
        "administrative_areas_of_implementation": "Areas of Implementation21",
        "reconciliation_window_in_days": 0,
        "send_reconciliation_window_expiry_notifications": False,
    }


@pytest.fixture
def program(initial_program_data: dict, afghanistan: BusinessArea, partner: Partner) -> Program:
    program = ProgramFactory(**initial_program_data, business_area=afghanistan, programme_code="PROU")
    role_with_all_permissions = RoleFactory(name="Role with all permissions", is_available_for_partner=True)
    role_with_all_permissions.is_available_for_partner = True
    role_with_all_permissions.save()
    RoleAssignmentFactory(
        partner=partner,
        business_area=afghanistan,
        program=program,
        role=role_with_all_permissions,
    )
    return program


@pytest.fixture
def pdu_data_to_be_removed() -> PeriodicFieldData:
    return PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL,
        number_of_rounds=3,
        rounds_names=[
            "Round 1 To Be Removed",
            "Round 2 To Be Removed",
            "Round 3 To Be Removed",
        ],
    )


@pytest.fixture
def pdu_field_to_be_removed(program: Program, pdu_data_to_be_removed: PeriodicFieldData) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="PDU Field To Be Removed",
        pdu_data=pdu_data_to_be_removed,
    )


@pytest.fixture
def pdu_data_to_be_updated() -> PeriodicFieldData:
    return PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.STRING,
        number_of_rounds=2,
        rounds_names=["Round 1 To Be Updated", "Round 2 To Be Updated"],
    )


@pytest.fixture
def pdu_field_to_be_updated(program: Program, pdu_data_to_be_updated: PeriodicFieldData) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="PDU Field To Be Updated",
        pdu_data=pdu_data_to_be_updated,
    )


@pytest.fixture
def pdu_data_to_be_preserved() -> PeriodicFieldData:
    return PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DATE,
        number_of_rounds=1,
        rounds_names=["Round To Be Preserved"],
    )


@pytest.fixture
def pdu_field_to_be_preserved(program: Program, pdu_data_to_be_preserved: PeriodicFieldData) -> FlexibleAttribute:
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="PDU Field To Be Preserved",
        pdu_data=pdu_data_to_be_preserved,
    )


@pytest.fixture
def base_payload_for_update_without_changes(
    initial_program_data: dict,
    program: Program,
    dct_standard: DataCollectingType,
    bg_household: BeneficiaryGroup,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_data_to_be_preserved: PeriodicFieldData,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_data_to_be_removed: PeriodicFieldData,
    pdu_field_to_be_updated: FlexibleAttribute,
    pdu_data_to_be_updated: PeriodicFieldData,
) -> dict:
    return {
        **initial_program_data,
        "slug": program.slug,
        "version": program.version,
        "data_collecting_type": dct_standard.code,
        "beneficiary_group": str(bg_household.id),
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
            },
            {
                "id": str(pdu_field_to_be_removed.id),
                "label": "PDU Field To Be Removed",
                "pdu_data": {
                    "subtype": pdu_data_to_be_removed.subtype,
                    "number_of_rounds": pdu_data_to_be_removed.number_of_rounds,
                    "rounds_names": pdu_data_to_be_removed.rounds_names,
                },
            },
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field To Be Updated",
                "pdu_data": {
                    "subtype": pdu_data_to_be_updated.subtype,
                    "number_of_rounds": pdu_data_to_be_updated.number_of_rounds,
                    "rounds_names": pdu_data_to_be_updated.rounds_names,
                },
            },
        ],
    }


@pytest.fixture
def base_expected_response_without_changes(
    base_payload_for_update_without_changes: dict,
    program: Program,
    partner: Partner,
    unicef_hq: Partner,
    unicef_partner_in_afghanistan: Partner,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
) -> dict:
    return {
        **base_payload_for_update_without_changes,
        "programme_code": program.programme_code,
        "budget": f"{program.budget:.2f}",
        "identification_key_individual_label": None,
        "pdu_fields": [
            {
                **pdu_field_data,
                "name": pdu_field.name,
                "pdu_data": pdu_field_data["pdu_data"],
            }
            for pdu_field_data, pdu_field in zip(
                base_payload_for_update_without_changes["pdu_fields"],
                [
                    pdu_field_to_be_preserved,
                    pdu_field_to_be_removed,
                    pdu_field_to_be_updated,
                ],
                strict=True,
            )
        ],
        "partners": [
            {
                "id": partner.id,
                "name": partner.name,
                "areas": None,
                "area_access": "BUSINESS_AREA",
            },
            {
                "id": unicef_hq.id,
                "name": unicef_hq.name,
                "areas": None,
                "area_access": "BUSINESS_AREA",
            },
            {
                "id": unicef_partner_in_afghanistan.id,
                "name": unicef_partner_in_afghanistan.name,
                "areas": None,
                "area_access": "BUSINESS_AREA",
            },
        ],
    }


@pytest.fixture
def update_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:programs:programs-detail",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "slug": program.slug,
        },
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_update_program_with_permissions(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PROGRAMME_UPDATE], afghanistan, whole_business_area_access=True
    )

    payload = {
        **base_payload_for_update_without_changes,
        "name": "Test Program Updated",
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK
    program.refresh_from_db()
    assert program.name == "Test Program Updated"
    program.refresh_from_db()
    assert response.json() == {
        **base_expected_response_without_changes,
        "name": "Test Program Updated",
        "version": program.version,
    }


def test_update_program_without_permissions(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [], afghanistan, whole_business_area_access=True)

    payload = {
        **base_payload_for_update_without_changes,
        "name": "Test Program Updated",
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_program_with_no_changes(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = copy.deepcopy(base_payload_for_update_without_changes)
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK

    old_program_instance = program
    program.refresh_from_db()
    assert program == old_program_instance
    assert response.json() == {
        **base_expected_response_without_changes,
        "version": program.version,
    }


def test_update_data_collecting_type(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    dct_2 = DataCollectingTypeFactory(label="DCT2", code="dct2", type=DataCollectingType.Type.STANDARD)

    payload = {
        **base_payload_for_update_without_changes,
        "data_collecting_type": dct_2.code,
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK

    program.refresh_from_db()
    assert program.data_collecting_type == dct_2
    assert response.json() == {
        **base_expected_response_without_changes,
        "data_collecting_type": dct_2.code,
        "version": program.version,
    }


def test_update_data_collecting_type_invalid(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    dct_standard: DataCollectingType,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    dct_invalid = DataCollectingTypeFactory(
        label="DCT_INVALID",
        code="dct_invalid",
        type=DataCollectingType.Type.STANDARD,
    )
    payload = {
        **base_payload_for_update_without_changes,
        "data_collecting_type": dct_invalid.code,
    }

    # DCT inactive
    dct_invalid.active = False
    dct_invalid.save()
    response_for_inactive = authenticated_client.put(update_url, payload)
    assert response_for_inactive.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_inactive.json()
    assert (
        response_for_inactive.json()["data_collecting_type"][0]
        == "Only active Data Collecting Type can be used in Program."
    )
    program.refresh_from_db()
    assert program.data_collecting_type == dct_standard

    # DCT deprecated
    dct_invalid.active = True
    dct_invalid.deprecated = True
    dct_invalid.save()
    response_for_deprecated = authenticated_client.put(update_url, payload)
    assert response_for_deprecated.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_deprecated.json()
    assert (
        response_for_deprecated.json()["data_collecting_type"][0]
        == "Deprecated Data Collecting Type cannot be used in Program."
    )
    program.refresh_from_db()
    assert program.data_collecting_type == dct_standard

    # DCT limited to another BA
    dct_invalid.deprecated = False
    dct_invalid.save()
    ukraine = BusinessAreaFactory(name="Ukraine", slug="ukraine")
    dct_invalid.limit_to.add(ukraine)
    response_for_limited = authenticated_client.put(update_url, payload)
    assert response_for_limited.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_limited.json()
    assert (
        response_for_limited.json()["data_collecting_type"][0]
        == "This Data Collecting Type is not available for this Business Area."
    )
    program.refresh_from_db()
    assert program.data_collecting_type == dct_standard


def test_update_data_collecting_type_for_active_program(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    dct_standard: DataCollectingType,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    dct_2 = DataCollectingTypeFactory(label="DCT2", code="dct2", type=DataCollectingType.Type.STANDARD)

    program.status = Program.ACTIVE
    program.save()

    payload = {
        **base_payload_for_update_without_changes,
        "data_collecting_type": dct_2.code,
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response.json()
    assert response.json()["data_collecting_type"][0] == "Data Collecting Type can be updated only for Draft Programs."
    program.refresh_from_db()
    assert program.data_collecting_type == dct_standard


def test_update_data_collecting_type_for_program_with_population(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    dct_standard: DataCollectingType,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    dct_2 = DataCollectingTypeFactory(label="DCT2", code="dct2", type=DataCollectingType.Type.STANDARD)

    household = HouseholdFactory(program=program)
    IndividualFactory(household=household, program=program)
    IndividualFactory(household=household, program=program)

    payload = {
        **base_payload_for_update_without_changes,
        "data_collecting_type": dct_2.code,
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response.json()
    assert (
        response.json()["data_collecting_type"][0]
        == "Data Collecting Type can be updated only for Program without any households."
    )
    program.refresh_from_db()
    assert program.data_collecting_type == dct_standard


def test_update_data_collecting_type_invalid_with_beneficiary_group(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    dct_standard: DataCollectingType,
    dct_social: DataCollectingType,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "data_collecting_type": dct_social.code,
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "beneficiary_group" in response.json()
    assert (
        response.json()["beneficiary_group"][0]
        == "Selected combination of data collecting type and beneficiary group is invalid."
    )

    program.refresh_from_db()
    assert program.data_collecting_type == dct_standard


def test_update_beneficiary_group(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    bg_2 = BeneficiaryGroupFactory(name="Beneficiary Group 2", master_detail=True)

    payload = {
        **base_payload_for_update_without_changes,
        "beneficiary_group": str(bg_2.id),
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK

    program.refresh_from_db()
    assert program.beneficiary_group == bg_2
    assert response.json() == {
        **base_expected_response_without_changes,
        "beneficiary_group": str(bg_2.id),
        "version": program.version,
    }


def test_update_beneficiary_group_invalid_with_data_collecting_type(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    bg_household: BeneficiaryGroup,
    bg_sw: BeneficiaryGroup,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "beneficiary_group": str(bg_sw.id),
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "beneficiary_group" in response.json()
    assert (
        response.json()["beneficiary_group"][0]
        == "Selected combination of data collecting type and beneficiary group is invalid."
    )

    program.refresh_from_db()
    assert program.beneficiary_group == bg_household


def test_update_beneficiary_group_invalid_with_population(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    bg_household: BeneficiaryGroup,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )
    bg_2 = BeneficiaryGroupFactory(name="Beneficiary Group 2", master_detail=True)

    RegistrationDataImportFactory(program=program, business_area=afghanistan)

    payload = {
        **base_payload_for_update_without_changes,
        "beneficiary_group": str(bg_2.id),
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "beneficiary_group" in response.json()
    assert response.json()["beneficiary_group"][0] == "Beneficiary Group cannot be updated if Program has population."

    program.refresh_from_db()
    assert program.beneficiary_group == bg_household


def test_update_start_and_end_dates(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    ProgramCycleFactory(
        program=program,
        start_date="2030-06-01",
        end_date="2030-06-20",
    )

    payload = {
        **base_payload_for_update_without_changes,
        "start_date": "2030-01-01",
        "end_date": "2033-12-31",
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK

    program.refresh_from_db()
    assert program.start_date.strftime("%Y-%m-%d") == payload["start_date"]
    assert program.end_date.strftime("%Y-%m-%d") == payload["end_date"]
    assert response.json() == {
        **base_expected_response_without_changes,
        "start_date": payload["start_date"],
        "end_date": payload["end_date"],
        "version": program.version,
    }


def test_update_end_date_and_start_date_invalid_end_date_before_start_date(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "start_date": "2033-01-01",
        "end_date": "2032-12-31",
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "end_date" in response.json()
    assert "End date cannot be earlier than the start date." in response.json()["end_date"][0]

    program.refresh_from_db()
    assert program.start_date.strftime("%Y-%m-%d") == base_payload_for_update_without_changes["start_date"]
    assert program.end_date.strftime("%Y-%m-%d") == base_payload_for_update_without_changes["end_date"]


def test_update_end_date_and_start_date_invalid_end_date_before_last_cycle(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    ProgramCycleFactory(
        program=program,
        start_date="2030-06-01",
        end_date="2030-06-20",
    )
    ProgramCycleFactory(program=program, start_date="2032-01-01", end_date="2033-12-31")

    payload = {
        **base_payload_for_update_without_changes,
        "start_date": "2030-01-01",  # Start date is valid
        "end_date": "2033-06-30",  # End date is before the latest cycle's end_date
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "end_date" in response.json()
    assert "End date must be the same as or after the latest cycle." in response.json()["end_date"][0]

    program.refresh_from_db()
    assert program.start_date.strftime("%Y-%m-%d") == base_payload_for_update_without_changes["start_date"]
    assert program.end_date.strftime("%Y-%m-%d") == base_payload_for_update_without_changes["end_date"]


def test_update_end_date_and_start_date_invalid_start_date_after_first_cycle(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    ProgramCycleFactory(
        program=program,
        start_date="2030-06-01",
        end_date="2030-06-20",
    )
    ProgramCycleFactory(program=program, start_date="2032-01-01", end_date="2033-12-31")

    payload = {
        **base_payload_for_update_without_changes,
        "start_date": "2030-07-01",  # Start date is after the earliest cycle's start_date
        "end_date": "2034-12-31",  # End date is valid
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "start_date" in response.json()
    assert "Start date must be the same as or before the earliest cycle." in response.json()["start_date"][0]

    program.refresh_from_db()
    assert program.start_date.strftime("%Y-%m-%d") == base_payload_for_update_without_changes["start_date"]
    assert program.end_date.strftime("%Y-%m-%d") == base_payload_for_update_without_changes["end_date"]


def test_update_program_with_duplicate_name_same_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    ProgramFactory(
        business_area=afghanistan,
        name="Program Two",
        status=Program.DRAFT,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "name": "Program Two",
    }

    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.json()
    assert "Programme with this name already exists in this business area" in str(response.json()["name"])


def test_update_program_with_same_name_same_program(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "name": program.name,  # Same name as current program
        "budget": 200000,
    }

    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK

    program.refresh_from_db()
    assert program.name == base_payload_for_update_without_changes["name"]
    assert program.budget == 200000


def test_update_multiple_fields(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "name": "Test Program Updated Multiple Fields",
        "description": "Updated description.",
        "budget": 200000,
        "population_goal": 200,
        "cash_plus": True,
        "frequency_of_payments": Program.ONE_OFF,
    }
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK

    program.refresh_from_db()
    assert program.name == "Test Program Updated Multiple Fields"
    assert program.description == "Updated description."
    assert program.budget == 200000
    assert program.population_goal == 200
    assert program.cash_plus is True
    assert program.frequency_of_payments == Program.ONE_OFF
    assert response.json() == {
        **base_expected_response_without_changes,
        "name": "Test Program Updated Multiple Fields",
        "description": "Updated description.",
        "budget": "200000.00",
        "population_goal": 200,
        "cash_plus": True,
        "frequency_of_payments": Program.ONE_OFF,
        "version": program.version,
    }


def test_update_pdu_fields(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_data_to_be_preserved: PeriodicFieldData,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            # "PDU Field To Be Preserved" remains unchanged
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
            },
            # "PDU Field To Be Removed" is removed
            # "PDU Field To Be Updated" is updated
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3  # Initial count of PDU fields
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert FlexibleAttribute.objects.filter(program=program).count() == 2  # After update, one field is removed

    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field Updated"
    assert pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.BOOL
    assert pdu_field_to_be_updated.pdu_data.number_of_rounds == 3
    assert pdu_field_to_be_updated.pdu_data.rounds_names == [
        "Round 1 Updated",
        "Round 2 Updated",
        "Round 3 Updated",
    ]
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is True

    program.refresh_from_db()
    assert response.json() == {
        **base_expected_response_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
                "name": pdu_field_to_be_preserved.name,
            },
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
                "name": pdu_field_to_be_updated.name,
            },
        ],
        "version": program.version,
    }


def test_update_pdu_fields_and_add_new(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_data_to_be_preserved: PeriodicFieldData,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            # "PDU Field To Be Preserved" remains unchanged
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
            },
            # "PDU Field To Be Removed" is removed
            # "PDU Field To Be Updated" is updated
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
            },
            # New PDU field to be added
            {
                "label": "New PDU Field",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 2,
                    "rounds_names": ["Round 1 New", "Round 2 New"],
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3  # Initial count of PDU fields
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert (
        FlexibleAttribute.objects.filter(program=program).count() == 3
    )  # After update, one field is removed, one is updated, and one new is added

    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field Updated"
    assert pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.BOOL
    assert pdu_field_to_be_updated.pdu_data.number_of_rounds == 3
    assert pdu_field_to_be_updated.pdu_data.rounds_names == [
        "Round 1 Updated",
        "Round 2 Updated",
        "Round 3 Updated",
    ]
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is True
    new_pdu_field = FlexibleAttribute.objects.filter(program=program, name="new_pdu_field").first()
    assert new_pdu_field.label["English(EN)"] == "New PDU Field"
    assert new_pdu_field.pdu_data.subtype == PeriodicFieldData.STRING
    assert new_pdu_field.pdu_data.number_of_rounds == 2
    assert new_pdu_field.pdu_data.rounds_names == ["Round 1 New", "Round 2 New"]

    program.refresh_from_db()
    assert response.json() == {
        **base_expected_response_without_changes,
        "pdu_fields": [
            {
                "id": str(new_pdu_field.id),
                "label": "New PDU Field",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 2,
                    "rounds_names": ["Round 1 New", "Round 2 New"],
                },
                "name": new_pdu_field.name,
            },
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
                "name": pdu_field_to_be_preserved.name,
            },
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
                "name": pdu_field_to_be_updated.name,
            },
        ],
        "version": program.version,
    }


def test_update_pdu_fields_invalid_data(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_data_to_be_preserved: PeriodicFieldData,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
            },
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
            },
            {
                "label": "New PDU Field",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 1,
                    "rounds_names": ["Round 1 New", "Round 2 New"],
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3  # Initial count of PDU fields
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Number of rounds does not match the number of round names." in response.json()
    assert FlexibleAttribute.objects.filter(program=program).count() == 3  # No change

    # Check that the fields are not updated
    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"
    assert pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.STRING
    assert pdu_field_to_be_updated.pdu_data.number_of_rounds == 2
    assert pdu_field_to_be_updated.pdu_data.rounds_names == [
        "Round 1 To Be Updated",
        "Round 2 To Be Updated",
    ]
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is False
    assert FlexibleAttribute.objects.filter(program=program, name="new_pdu_field").exists() is False


def test_update_pdu_fields_invalid_data_duplicated_field_names_in_input(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_data_to_be_preserved: PeriodicFieldData,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
            },
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
            },
            {
                "label": "PDU Field Updated",  # Duplicate label
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 2,
                    "rounds_names": ["Round 1 New", "Round 2 New"],
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Time Series Field names must be unique." in response.json()
    assert FlexibleAttribute.objects.filter(program=program).count() == 3

    # Check that the fields are not updated
    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is False
    assert FlexibleAttribute.objects.filter(program=program, name="new_pdu_field").exists() is False


def test_update_pdu_fields_add_field_with_same_field_name_in_different_program(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_data_to_be_preserved: PeriodicFieldData,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    # pdu data with NEW field with name that already exists in the database but in different program -> no fail
    program2 = ProgramFactory(name="TestProgram2", business_area=afghanistan)
    pdu_data_existing = PeriodicFieldDataFactory()
    FlexibleAttributeForPDUFactory(
        program=program2,
        label="PDU Field Existing",
        pdu_data=pdu_data_existing,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
            },
            # "PDU Field To Be Removed" is removed
            # "PDU Field To Be Updated" is updated
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
            },
            {
                "label": "PDU Field Existing",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 2,
                    "rounds_names": ["Round 1 New", "Round 2 New"],
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3  # Initial count of PDU fields
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert (
        FlexibleAttribute.objects.filter(program=program).count() == 3
    )  # After update, one field is removed, one is updated, and one new is added

    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field Updated"
    assert pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.BOOL
    assert pdu_field_to_be_updated.pdu_data.number_of_rounds == 3
    assert pdu_field_to_be_updated.pdu_data.rounds_names == [
        "Round 1 Updated",
        "Round 2 Updated",
        "Round 3 Updated",
    ]
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is True
    new_pdu_field = FlexibleAttribute.objects.filter(program=program, name="pdu_field_existing").first()
    assert FlexibleAttribute.objects.filter(name="pdu_field_existing").count() == 2

    assert new_pdu_field.label["English(EN)"] == "PDU Field Existing"
    assert new_pdu_field.pdu_data.subtype == PeriodicFieldData.STRING
    assert new_pdu_field.pdu_data.number_of_rounds == 2
    assert new_pdu_field.pdu_data.rounds_names == ["Round 1 New", "Round 2 New"]

    program.refresh_from_db()
    assert response.json() == {
        **base_expected_response_without_changes,
        "pdu_fields": [
            {
                "id": str(new_pdu_field.id),
                "label": "PDU Field Existing",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 2,
                    "rounds_names": ["Round 1 New", "Round 2 New"],
                },
                "name": new_pdu_field.name,
            },
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
                "name": pdu_field_to_be_preserved.name,
            },
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
                "name": pdu_field_to_be_updated.name,
            },
        ],
        "version": program.version,
    }


def test_update_pdu_fields_with_same_name_in_different_program(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_data_to_be_preserved: PeriodicFieldData,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    # pdu data with NEW field with name that already exists in the database but in different program -> no fail
    program2 = ProgramFactory(name="TestProgram2", business_area=afghanistan)
    pdu_data_existing = PeriodicFieldDataFactory()
    FlexibleAttributeForPDUFactory(
        program=program2,
        label="PDU Field Existing",
        pdu_data=pdu_data_existing,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
            },
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Existing",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3  # Initial count of PDU fields
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert FlexibleAttribute.objects.filter(program=program).count() == 2  # After update, one field is removed

    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field Existing"
    assert pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.BOOL
    assert pdu_field_to_be_updated.pdu_data.number_of_rounds == 3
    assert pdu_field_to_be_updated.pdu_data.rounds_names == [
        "Round 1 Updated",
        "Round 2 Updated",
        "Round 3 Updated",
    ]
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is True

    program.refresh_from_db()
    assert response.json() == {
        **base_expected_response_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field Existing",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],
                },
                "name": pdu_field_to_be_updated.name,
            },
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
                "name": pdu_field_to_be_preserved.name,
            },
        ],
        "version": program.version,
    }


def test_update_pdu_fields_when_program_has_rdi(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_data_to_be_preserved: PeriodicFieldData,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_data_to_be_removed: PeriodicFieldData,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    # if program has RDI, it is not possible to remove or add PDU fields or update existing PDU fields -
    # only possible to increase number of rounds and add names for new rounds
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    RegistrationDataImportFactory(program=program, business_area=afghanistan)

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field - NAME WILL NOT BE UPDATED",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,  # subtype will NOT be updated
                    "number_of_rounds": 4,  # number of rounds will be increased
                    "rounds_names": [
                        "Round 1 To Be Updated",
                        "Round 2 To Be Updated",
                        "Round 3 New",
                        "Round 4 New",
                    ],  # can only add new rounds, cannot change existing names
                },
            },
            {
                "label": "New PDU Field",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 2,
                    "rounds_names": ["Round 1 New", "Round 2 New"],
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert (
        FlexibleAttribute.objects.filter(program=program).count() == 3
    )  # no field can be removed or added for program with RDI

    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"  # not updated
    assert pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.STRING  # not updated
    assert pdu_field_to_be_updated.pdu_data.number_of_rounds == 4  # updated
    assert pdu_field_to_be_updated.pdu_data.rounds_names == [
        "Round 1 To Be Updated",
        "Round 2 To Be Updated",
        "Round 3 New",
        "Round 4 New",
    ]  # updated
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is False  # not removed
    assert (
        FlexibleAttribute.objects.filter(program=program, name="new_pdu_field").exists() is False
    )  # new field not added

    program.refresh_from_db()
    assert response.json() == {
        **base_expected_response_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_preserved.id),
                "label": "PDU Field To Be Preserved",
                "pdu_data": {
                    "subtype": pdu_data_to_be_preserved.subtype,
                    "number_of_rounds": pdu_data_to_be_preserved.number_of_rounds,
                    "rounds_names": pdu_data_to_be_preserved.rounds_names,
                },
                "name": pdu_field_to_be_preserved.name,
            },
            {
                "id": str(pdu_field_to_be_removed.id),
                "label": "PDU Field To Be Removed",
                "pdu_data": {
                    "subtype": pdu_data_to_be_removed.subtype,
                    "number_of_rounds": pdu_data_to_be_removed.number_of_rounds,
                    "rounds_names": pdu_data_to_be_removed.rounds_names,
                },
                "name": pdu_field_to_be_removed.name,
            },
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field To Be Updated",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 4,
                    "rounds_names": [
                        "Round 1 To Be Updated",
                        "Round 2 To Be Updated",
                        "Round 3 New",
                        "Round 4 New",
                    ],
                },
                "name": pdu_field_to_be_updated.name,
            },
        ],
        "version": program.version,
    }


def test_update_pdu_fields_invalid_when_program_has_rdi_decrease_rounds(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    # round number CANNOT be decreased for Program with RDI
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    RegistrationDataImportFactory(program=program, business_area=afghanistan)

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field - NAME WILL NOT BE UPDATED",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,  # subtype will NOT be updated
                    "number_of_rounds": 1,  # number of rounds will NOT be decreased
                    "rounds_names": ["Round 1 To Be Updated"],
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "It is not possible to decrease the number of rounds for a Program with RDI or TP." in response.json()
    assert FlexibleAttribute.objects.filter(program=program).count() == 3

    # Check that the fields are not updated
    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"
    assert pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.STRING
    assert pdu_field_to_be_updated.pdu_data.number_of_rounds == 2
    assert pdu_field_to_be_updated.pdu_data.rounds_names == [
        "Round 1 To Be Updated",
        "Round 2 To Be Updated",
    ]
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is False


def test_update_pdu_fields_invalid_when_program_has_rdi_change_rounds_names(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    # names for existing rounds cannot be changed for Program with RDI
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    RegistrationDataImportFactory(program=program, business_area=afghanistan)

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [
            {
                "id": str(pdu_field_to_be_updated.id),
                "label": "PDU Field - NAME WILL NOT BE UPDATED",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,  # subtype will NOT be updated
                    "number_of_rounds": 3,
                    "rounds_names": [
                        "Round 1 Updated",
                        "Round 2 Updated",
                        "Round 3 Updated",
                    ],  # cannot change existing names
                },
            },
        ],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "It is not possible to change the names of existing rounds for a Program with RDI or TP." in response.json()
    assert FlexibleAttribute.objects.filter(program=program).count() == 3

    # Check that the fields are not updated
    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.label["English(EN)"] == "PDU Field To Be Updated"
    assert pdu_field_to_be_updated.pdu_data.subtype == PeriodicFieldData.STRING
    assert pdu_field_to_be_updated.pdu_data.number_of_rounds == 2
    assert pdu_field_to_be_updated.pdu_data.rounds_names == [
        "Round 1 To Be Updated",
        "Round 2 To Be Updated",
    ]
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is False


def test_update_pdu_fields_remove_all(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    update_url: str,
    base_payload_for_update_without_changes: dict,
    base_expected_response_without_changes: dict,
    pdu_field_to_be_preserved: FlexibleAttribute,
    pdu_field_to_be_removed: FlexibleAttribute,
    pdu_field_to_be_updated: FlexibleAttribute,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_UPDATE],
        afghanistan,
        whole_business_area_access=True,
    )

    payload = {
        **base_payload_for_update_without_changes,
        "pdu_fields": [],
    }
    assert FlexibleAttribute.objects.filter(program=program).count() == 3  # Initial count of PDU fields
    response = authenticated_client.put(update_url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert FlexibleAttribute.objects.filter(program=program).count() == 0  # After update, all fields are removed

    pdu_field_to_be_preserved.refresh_from_db()
    assert pdu_field_to_be_preserved.is_removed is True
    pdu_field_to_be_removed.refresh_from_db()
    assert pdu_field_to_be_removed.is_removed is True
    pdu_field_to_be_updated.refresh_from_db()
    assert pdu_field_to_be_updated.is_removed is True

    program.refresh_from_db()
    assert response.json() == {
        **base_expected_response_without_changes,
        "pdu_fields": [],
        "version": program.version,
    }
