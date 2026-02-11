"""Tests for program create API endpoint."""

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
    PartnerFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import (
    Area,
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    FlexibleAttribute,
    Partner,
    PeriodicFieldData,
    Program,
    User,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def partner(afghanistan: BusinessArea) -> Partner:
    partner = PartnerFactory(name="TestPartner")
    partner.allowed_business_areas.add(afghanistan)
    return partner


@pytest.fixture
def partner2(afghanistan: BusinessArea) -> Partner:
    partner = PartnerFactory(name="TestPartner2")
    partner.allowed_business_areas.add(afghanistan)
    return partner


@pytest.fixture
def unicef_partner(db: Any) -> Partner:
    return PartnerFactory(name="UNICEF")


@pytest.fixture
def unicef_hq(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF HQ", parent=unicef_partner)


@pytest.fixture
def unicef_partner_in_afghanistan(unicef_partner: Partner) -> Partner:
    return PartnerFactory(name="UNICEF Partner for afghanistan", parent=unicef_partner)


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def area1(afghanistan: BusinessArea) -> Area:
    country = CountryFactory()
    country.business_areas.set([afghanistan])
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, area_type=admin_type, p_code="AF01", name="Area1")


@pytest.fixture
def area2(afghanistan: BusinessArea) -> Area:
    country = CountryFactory()
    country.business_areas.set([afghanistan])
    admin_type = AreaTypeFactory(country=country, area_level=1)
    return AreaFactory(parent=None, area_type=admin_type, p_code="AF02", name="Area2")


@pytest.fixture
def dct_standard(db: Any) -> DataCollectingType:
    return DataCollectingTypeFactory(label="Full", code="full", type=DataCollectingType.Type.STANDARD)


@pytest.fixture
def dct_social(db: Any) -> DataCollectingType:
    return DataCollectingTypeFactory(label="SW Full", code="sw_full", type=DataCollectingType.Type.SOCIAL)


@pytest.fixture
def bg_household(db: Any) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Household", master_detail=True)


@pytest.fixture
def bg_sw(db: Any) -> BeneficiaryGroup:
    return BeneficiaryGroupFactory(name="Social Worker", master_detail=False)


@pytest.fixture
def valid_input_data_standard(dct_standard: DataCollectingType, bg_household: BeneficiaryGroup) -> dict:
    return {
        "name": "Test Program",
        "programme_code": None,
        "start_date": "2030-01-01",
        "end_date": "2033-12-31",
        "sector": Program.CHILD_PROTECTION,
        "data_collecting_type": dct_standard.code,
        "beneficiary_group": str(bg_household.id),
        "budget": 1000000,
        "population_goal": 1000,
        "cash_plus": False,
        "frequency_of_payments": Program.REGULAR,
        "administrative_areas_of_implementation": "",
        "partner_access": Program.ALL_PARTNERS_ACCESS,
        "partners": [],
        "pdu_fields": [],
        "reconciliation_window_in_days": 0,
        "send_reconciliation_window_expiry_notifications": False,
    }


@pytest.fixture
def expected_response_standard(
    valid_input_data_standard: dict,
    unicef_hq: Partner,
    unicef_partner_in_afghanistan: Partner,
) -> dict:
    return {
        **valid_input_data_standard,
        "description": "",
        "status": Program.DRAFT,
        "budget": "1000000.00",
        "partners": [
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
def list_url(afghanistan: BusinessArea) -> str:
    return reverse(
        "api:programs:programs-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


def test_create_program_with_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    expected_response_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PROGRAMME_CREATE], afghanistan, whole_business_area_access=True
    )

    response = authenticated_client.post(list_url, valid_input_data_standard)
    assert response.status_code == status.HTTP_201_CREATED
    program = Program.objects.get(pk=response.json()["id"])
    expected_response = {
        **expected_response_standard,
        "id": str(program.id),
        "programme_code": program.programme_code,  # programme_code is auto-generated
        "slug": program.slug,  # slug is auto-generated
        "version": program.version,
    }
    assert response.json() == expected_response


def test_create_program_without_permission(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(user, [], afghanistan, whole_business_area_access=True)

    response = authenticated_client.post(list_url, valid_input_data_standard)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_program_with_programme_code(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    expected_response_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_program_code = {
        **valid_input_data_standard,
        "programme_code": "T3st",
    }
    response = authenticated_client.post(list_url, input_data_with_program_code)
    assert response.status_code == status.HTTP_201_CREATED
    program = Program.objects.get(pk=response.json()["id"])
    expected_response = {
        **expected_response_standard,
        "id": str(program.id),
        "programme_code": "T3ST",  # programme_code is uppercased
        "slug": "t3st",  # slug is a slugified version of program_code
        "version": program.version,
    }
    assert response.json() == expected_response


def test_create_program_with_programme_code_invalid(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_program_code = {
        **valid_input_data_standard,
        "programme_code": "T#ST",  # Invalid program code
    }
    response = authenticated_client.post(list_url, input_data_with_program_code)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "programme_code" in response.json()
    assert (
        "Programme code should be exactly 4 characters long and may only contain letters, digits and character: -"
        in response.json()["programme_code"][0]
    )


def test_create_program_with_programme_code_existing(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    ProgramFactory(programme_code="T3ST", business_area=afghanistan)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_program_code = {
        **valid_input_data_standard,
        "programme_code": "T3st",
    }
    response = authenticated_client.post(list_url, input_data_with_program_code)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "programme_code" in response.json()
    assert response.json()["programme_code"][0] == "Programme code is already used."


def test_create_program_with_missing_data(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    missing_input_data = {
        **valid_input_data_standard,
    }
    missing_input_data.pop("name")
    response = authenticated_client.post(
        list_url,
        missing_input_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.json()
    assert response.json()["name"][0] == "This field is required."


def test_create_program_with_invalid_data_collecting_type(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    dct_invalid = DataCollectingTypeFactory(label="Invalid", code="invalid", type=DataCollectingType.Type.STANDARD)
    invalid_input_data = {
        **valid_input_data_standard,
        "data_collecting_type": dct_invalid.code,
    }

    # DCT inactive
    dct_invalid.active = False
    dct_invalid.save()
    response_for_inactive = authenticated_client.post(list_url, invalid_input_data)
    assert response_for_inactive.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_inactive.json()
    assert (
        response_for_inactive.json()["data_collecting_type"][0]
        == "Only active Data Collecting Type can be used in Program."
    )

    # DCT deprecated
    dct_invalid.active = True
    dct_invalid.deprecated = True
    dct_invalid.save()
    response_for_deprecated = authenticated_client.post(list_url, invalid_input_data)
    assert response_for_deprecated.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_deprecated.json()
    assert (
        response_for_deprecated.json()["data_collecting_type"][0]
        == "Deprecated Data Collecting Type cannot be used in Program."
    )

    # DCT limited to another BA
    dct_invalid.deprecated = False
    dct_invalid.save()
    ukraine = BusinessAreaFactory(name="Ukraine", slug="ukraine")
    dct_invalid.limit_to.add(ukraine)
    response_for_limited = authenticated_client.post(list_url, invalid_input_data)
    assert response_for_limited.status_code == status.HTTP_400_BAD_REQUEST
    assert "data_collecting_type" in response_for_limited.json()
    assert (
        response_for_limited.json()["data_collecting_type"][0]
        == "This Data Collecting Type is not available for this Business Area."
    )

    # DCT valid
    dct_invalid.limit_to.add(afghanistan)
    response_for_valid = authenticated_client.post(list_url, invalid_input_data)
    assert response_for_valid.status_code == status.HTTP_201_CREATED


def test_create_program_with_invalid_beneficiary_group(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    bg_sw: BeneficiaryGroup,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    invalid_input_data = {
        **valid_input_data_standard,
        "beneficiary_group": str(bg_sw.id),  # Invalid DCT and BG combination
    }
    response = authenticated_client.post(list_url, invalid_input_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "beneficiary_group" in response.json()
    assert (
        response.json()["beneficiary_group"][0]
        == "Selected combination of data collecting type and beneficiary group is invalid."
    )


def test_create_program_with_invalid_dates(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    invalid_input_data = {
        **valid_input_data_standard,
        "start_date": "2033-01-01",  # Start date after end date
        "end_date": "2030-12-31",
    }
    response = authenticated_client.post(list_url, invalid_input_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "end_date" in response.json()
    assert response.json()["end_date"][0] == "End date cannot be earlier than the start date."


def test_create_program_without_end_date(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    expected_response_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    invalid_input_data = {
        **valid_input_data_standard,
        "end_date": None,
    }
    response = authenticated_client.post(list_url, invalid_input_data)
    assert response.status_code == status.HTTP_201_CREATED
    program = Program.objects.get(pk=response.json()["id"])
    expected_response = {
        **expected_response_standard,
        "id": str(program.id),
        "programme_code": program.programme_code,
        "slug": program.slug,
        "end_date": None,
        "version": program.version,
    }
    assert response.json() == expected_response


def test_create_program_with_duplicate_name_same_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )

    ProgramFactory(
        business_area=afghanistan,
        name="Duplicate Program Name",
        status=Program.DRAFT,
    )

    duplicate_input_data = {
        **valid_input_data_standard,
        "name": "Duplicate Program Name",
    }

    response = authenticated_client.post(list_url, duplicate_input_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "name" in response.json()
    assert "Programme with this name already exists in this business area" in str(response.json()["name"])


def test_create_program_with_duplicate_name_different_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )

    ukraine = BusinessAreaFactory(name="Ukraine", slug="ukraine")
    ProgramFactory(
        business_area=ukraine,
        name="Same Program Name",
        status=Program.DRAFT,
    )

    same_name_input_data = {
        **valid_input_data_standard,
        "name": "Same Program Name",
    }

    response = authenticated_client.post(list_url, same_name_input_data)
    assert response.status_code == status.HTTP_201_CREATED

    assert Program.objects.filter(name="Same Program Name").count() == 2
    assert Program.objects.filter(name="Same Program Name", business_area=afghanistan).exists()
    assert Program.objects.filter(name="Same Program Name", business_area=ukraine).exists()


def test_create_program_with_partners_data(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    partner: Partner,
    partner2: Partner,
    area1: Area,
    list_url: str,
    valid_input_data_standard: dict,
    expected_response_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_partners_data = {
        **valid_input_data_standard,
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        "partners": [
            {
                "partner": str(partner.id),
                "areas": [str(area1.id)],
            },
            {
                "partner": str(partner2.id),
                "areas": [],
            },
        ],
    }

    # TODO: the below code is needed due to the temporary solution on the partners access in program actions
    RoleAssignmentFactory(partner=partner, business_area=afghanistan, program=None)
    RoleAssignmentFactory(partner=partner2, business_area=afghanistan, program=None)
    # TODO: remove the above code when the partners access in program actions is implemented properly

    response = authenticated_client.post(list_url, input_data_with_partners_data)
    assert response.status_code == status.HTTP_201_CREATED
    program = Program.objects.get(pk=response.json()["id"])
    assert response.json() == {
        **expected_response_standard,
        "id": str(program.id),
        "programme_code": program.programme_code,
        "slug": program.slug,
        "version": program.version,
        "partners": [
            {
                "id": partner.id,
                "name": partner.name,
                "areas": [
                    {
                        "id": str(area1.id),
                        "level": area1.level,
                    },
                ],
                "area_access": "ADMIN_AREA",
            },
            {
                "id": partner2.id,
                "name": partner2.name,
                "areas": None,
                "area_access": "BUSINESS_AREA",
            },
            *expected_response_standard["partners"],
        ],
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
    }


def test_create_program_with_invalid_partners_data(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    partner2: Partner,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_partners_data = {
        **valid_input_data_standard,
        "partner_access": Program.SELECTED_PARTNERS_ACCESS,
        "partners": [  # missing user's partner on the list
            {
                "partner": str(partner2.id),
                "areas": [],
            },
        ],
    }

    response = authenticated_client.post(list_url, input_data_with_partners_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "partners" in response.json()
    assert response.json()["partners"][0] == "Please assign access to your partner before saving the Program."


def test_create_program_with_invalid_partners_data_and_partner_access(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    partner: Partner,
    partner2: Partner,
    area1: Area,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_partners_data = {
        **valid_input_data_standard,
        "partner_access": Program.ALL_PARTNERS_ACCESS,  # cannot specify partners_data with ALL_PARTNERS_ACCESS
        "partners": [
            {
                "partner": str(partner.id),
                "areas": [str(area1.id)],
            },
            {
                "partner": str(partner2.id),
                "areas": [],
            },
        ],
    }

    response = authenticated_client.post(list_url, input_data_with_partners_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "partners" in response.json()
    assert response.json()["partners"][0] == "You cannot specify partners for the chosen access type."


def test_create_program_with_pdu_fields(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    expected_response_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_pdu_fields = {
        **valid_input_data_standard,
        "pdu_fields": [
            {
                "label": "PDU Field 1",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 3,
                    "rounds_names": ["Round 1", "", "Round 2"],
                },
            },
            {
                "label": "PDU Field 2",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 2,
                    "rounds_names": ["", ""],
                },
            },
        ],
    }
    response = authenticated_client.post(list_url, input_data_with_pdu_fields)
    assert response.status_code == status.HTTP_201_CREATED
    program = Program.objects.get(pk=response.json()["id"])
    assert FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU, program=program).count() == 2
    pdu_field_1 = FlexibleAttribute.objects.get(
        type=FlexibleAttribute.PDU,
        program=program,
        name="pdu_field_1",
    )
    pdu_field_2 = FlexibleAttribute.objects.get(
        type=FlexibleAttribute.PDU,
        program=program,
        name="pdu_field_2",
    )
    assert response.json() == {
        **expected_response_standard,
        "pdu_fields": [
            {
                "id": str(pdu_field_1.id),
                "label": "PDU Field 1",
                "name": "pdu_field_1",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 3,
                    "rounds_names": ["Round 1", "", "Round 2"],
                },
            },
            {
                "id": str(pdu_field_2.id),
                "label": "PDU Field 2",
                "name": "pdu_field_2",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 2,
                    "rounds_names": ["", ""],
                },
            },
        ],
        "id": str(program.id),
        "programme_code": program.programme_code,
        "slug": program.slug,
        "version": program.version,
    }


def test_create_program_with_invalid_pdu_fields(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_invalid_pdu_fields = {
        **valid_input_data_standard,
        "pdu_fields": [
            {
                "label": "PDU Field 1",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 2,
                    "rounds_names": [
                        "Round 1",
                        "",
                        "Round 2",
                    ],  # Number of rounds does not match rounds_names length
                },
            },
            {
                "label": "PDU Field 2",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 2,
                    "rounds_names": ["", ""],
                },
            },
        ],
    }
    response = authenticated_client.post(list_url, input_data_with_invalid_pdu_fields)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU).count() == 0
    assert "Number of rounds does not match the number of round names." in response.json()


def test_create_program_with_invalid_pdu_fields_duplicated_names(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    input_data_with_invalid_pdu_fields = {
        **valid_input_data_standard,
        "pdu_fields": [
            {
                "label": "PDU Field 1",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 3,
                    "rounds_names": ["Round 1", "", "Round 2"],
                },
            },
            {
                "label": "PDU Field 1",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 2,
                    "rounds_names": ["", ""],
                },
            },
        ],
    }
    response = authenticated_client.post(list_url, input_data_with_invalid_pdu_fields)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU).count() == 0
    assert "Time Series Field names must be unique." in response.json()


def test_create_program_with_valid_pdu_fields_existing_field_name_in_different_program(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    list_url: str,
    valid_input_data_standard: dict,
    expected_response_standard: dict,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    # pdu data with field name that already exists in the database but in different program -> no fail
    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DATE,
        number_of_rounds=1,
        rounds_names=["Round 1"],
    )
    program = ProgramFactory(business_area=afghanistan, name="Test Program 1")
    FlexibleAttributeForPDUFactory(
        program=program,
        label="PDU Field 1",
        pdu_data=pdu_data,
    )
    input_data_with_valid_pdu_fields = {
        **valid_input_data_standard,
        "pdu_fields": [
            {
                "label": "PDU Field 1",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 3,
                    "rounds_names": ["Round 1", "", "Round 2"],
                },
            },
            {
                "label": "PDU Field 2",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 2,
                    "rounds_names": ["", ""],
                },
            },
        ],
    }
    response = authenticated_client.post(list_url, input_data_with_valid_pdu_fields)
    assert response.status_code == status.HTTP_201_CREATED
    program = Program.objects.get(pk=response.json()["id"])
    assert FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU, program=program).count() == 2
    pdu_field_1 = FlexibleAttribute.objects.get(
        type=FlexibleAttribute.PDU,
        program=program,
        name="pdu_field_1",
    )
    pdu_field_2 = FlexibleAttribute.objects.get(
        type=FlexibleAttribute.PDU,
        program=program,
        name="pdu_field_2",
    )
    assert response.json() == {
        **expected_response_standard,
        "pdu_fields": [
            {
                "id": str(pdu_field_1.id),
                "label": "PDU Field 1",
                "name": "pdu_field_1",
                "pdu_data": {
                    "subtype": PeriodicFieldData.STRING,
                    "number_of_rounds": 3,
                    "rounds_names": ["Round 1", "", "Round 2"],
                },
            },
            {
                "id": str(pdu_field_2.id),
                "label": "PDU Field 2",
                "name": "pdu_field_2",
                "pdu_data": {
                    "subtype": PeriodicFieldData.BOOL,
                    "number_of_rounds": 2,
                    "rounds_names": ["", ""],
                },
            },
        ],
        "id": str(program.id),
        "programme_code": program.programme_code,
        "slug": program.slug,
        "version": program.version,
    }
