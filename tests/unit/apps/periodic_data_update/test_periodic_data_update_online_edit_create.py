"""Tests for PDU online edit create."""

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
    PaymentFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.models import BusinessArea, Payment, PDUOnlineEdit, PeriodicFieldData, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(name="Test Program", status=Program.ACTIVE, business_area=business_area)


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
def pdu_field_vaccination(program: Program) -> Any:
    pdu_data_vaccination = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL,
        number_of_rounds=5,
        rounds_names=[
            "January vaccination",
            "February vaccination",
            "March vaccination",
            "April vaccination",
            "May vaccination",
        ],
    )
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="Vaccination Records Update",
        pdu_data=pdu_data_vaccination,
    )


@pytest.fixture
def pdu_field_health(program: Program) -> Any:
    pdu_data_health = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL,
        number_of_rounds=5,
        rounds_names=["January", "February", "March", "April", "May"],
    )
    return FlexibleAttributeForPDUFactory(
        program=program,
        label="Health Records Update",
        pdu_data=pdu_data_health,
    )


@pytest.fixture
def individual1(
    business_area: BusinessArea, program: Program, pdu_field_vaccination: Any, pdu_field_health: Any
) -> Any:
    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
    )
    populate_pdu_with_null_values(program, individual.flex_fields)
    individual.save()
    return individual


@pytest.fixture
def household1(business_area: BusinessArea, program: Program, individual1: Any) -> Any:
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        head_of_household=individual1,
    )

    individual1.household = household
    individual1.save()
    return household


@pytest.fixture
def individual2(
    business_area: BusinessArea, program: Program, pdu_field_vaccination: Any, pdu_field_health: Any
) -> Any:
    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
    )
    populate_pdu_with_null_values(program, individual.flex_fields)
    individual.save()
    return individual


@pytest.fixture
def household2(business_area: BusinessArea, program: Program, individual2: Any) -> Any:
    household = HouseholdFactory(
        business_area=business_area,
        program=program,
        head_of_household=individual2,
    )
    household.head_of_household = individual2
    household.save()

    PaymentFactory(
        household=household,
        program=program,
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        collector=individual2,
    )

    return household


@pytest.fixture
def base_data(pdu_field_vaccination: Any, pdu_field_health: Any) -> dict:
    return {
        "rounds_data": [
            {
                "field": pdu_field_vaccination.name,
                "round": 2,
            },
            {
                "field": pdu_field_health.name,
                "round": 4,
            },
        ],
        "filters": {
            "received_assistance": True,
        },
    }


@pytest.fixture
def url_create(business_area: BusinessArea, program: Program) -> str:
    return reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-list",
        kwargs={"business_area_slug": business_area.slug, "program_slug": program.slug},
    )


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_201_CREATED),
        ([Permissions.PROGRAMME_UPDATE], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_pdu_online_edit_permissions(
    permissions: list,
    expected_status: int,
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household1: Any,
    household2: Any,
    individual1: Any,
    individual2: Any,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    base_data: dict,
    url_create: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=permissions,
        business_area=business_area,
        program=program,
    )

    response = authenticated_client.post(url_create, data=base_data)
    assert response.status_code == expected_status


def test_create_pdu_online_edit_base(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household1: Any,
    household2: Any,
    individual1: Any,
    individual2: Any,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    base_data: dict,
    url_create: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_TEMPLATE_CREATE, Permissions.PDU_VIEW_LIST_AND_DETAILS],
        business_area=business_area,
        program=program,
    )
    response = authenticated_client.post(url_create, data=base_data)
    assert response.status_code == status.HTTP_201_CREATED

    assert PDUOnlineEdit.objects.count() == 1
    pdu_online_edit = PDUOnlineEdit.objects.first()
    assert pdu_online_edit.name is None
    assert pdu_online_edit.business_area == business_area
    assert pdu_online_edit.program == program
    assert pdu_online_edit.status == PDUOnlineEdit.Status.NEW
    assert pdu_online_edit.created_by == user
    assert pdu_online_edit.approved_by is None
    assert pdu_online_edit.approved_at is None
    assert pdu_online_edit.number_of_records == 1
    assert pdu_online_edit.authorized_users.count() == 0
    assert pdu_online_edit.edit_data == [
        {
            "individual_uuid": str(individual2.pk),
            "unicef_id": individual2.unicef_id,
            "first_name": individual2.given_name,
            "last_name": individual2.family_name,
            "pdu_fields": {
                pdu_field_vaccination.name: {
                    "field_name": pdu_field_vaccination.name,
                    "label": "Vaccination Records Update",
                    "round_number": 2,
                    "round_name": "February vaccination",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "is_editable": True,
                },
                pdu_field_health.name: {
                    "field_name": pdu_field_health.name,
                    "label": "Health Records Update",
                    "round_number": 4,
                    "round_name": "April",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "is_editable": True,
                },
            },
        }
    ]

    # check response
    response_json = response.json()
    assert response_json["id"] == pdu_online_edit.id
    assert response_json["name"] is None
    assert response_json["created_by"] == user.get_full_name()
    assert response_json["authorized_users"] == []

    # check data in detail view
    url_detail = reverse(
        "api:periodic-data-update:periodic-data-update-online-edits-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program.slug,
            "pk": pdu_online_edit.id,
        },
    )
    response_detail = authenticated_client.get(url_detail)
    assert response_detail.status_code == status.HTTP_200_OK
    response_json_detail = response_detail.json()
    assert response_json_detail["id"] == pdu_online_edit.id
    assert response_json_detail["name"] is None
    assert response_json_detail["number_of_records"] == 1
    assert response_json_detail["created_by"] == user.get_full_name()
    assert response_json_detail["created_at"] == f"{pdu_online_edit.created_at:%Y-%m-%dT%H:%M:%SZ}"
    assert response_json_detail["status"] == PDUOnlineEdit.Status.NEW
    assert response_json_detail["status_display"] == PDUOnlineEdit.Status.NEW.label
    assert response_json_detail["is_authorized"] is False
    assert response_json_detail["approved_by"] == ""
    assert response_json_detail["approved_at"] is None
    assert response_json_detail["edit_data"] == [
        {
            "individual_uuid": str(individual2.pk),
            "unicef_id": individual2.unicef_id,
            "first_name": individual2.given_name,
            "last_name": individual2.family_name,
            "pdu_fields": {
                "vaccination_records_update": {
                    "field_name": "vaccination_records_update",
                    "label": "Vaccination Records Update",
                    "round_number": 2,
                    "round_name": "February vaccination",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "is_editable": True,
                },
                "health_records_update": {
                    "field_name": "health_records_update",
                    "label": "Health Records Update",
                    "round_number": 4,
                    "round_name": "April",
                    "value": None,
                    "collection_date": None,
                    "subtype": PeriodicFieldData.DECIMAL,
                    "is_editable": True,
                },
            },
        }
    ]
    assert response_json_detail["authorized_users"] == []
    assert response_json_detail["sent_back_comment"] is None


def test_create_pdu_online_edit_with_name(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household1: Any,
    household2: Any,
    individual1: Any,
    individual2: Any,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    base_data: dict,
    url_create: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_TEMPLATE_CREATE],
        business_area=business_area,
        program=program,
    )
    data = {
        "name": "Test Online Edit",
        **base_data,
    }

    response = authenticated_client.post(url_create, data=data)
    assert response.status_code == status.HTTP_201_CREATED

    assert PDUOnlineEdit.objects.count() == 1
    pdu_online_edit = PDUOnlineEdit.objects.first()
    assert pdu_online_edit.name == "Test Online Edit"
    assert pdu_online_edit.status == PDUOnlineEdit.Status.NEW
    assert pdu_online_edit.number_of_records == 1


def test_create_pdu_online_edit_with_authorized_users(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household1: Any,
    household2: Any,
    individual1: Any,
    individual2: Any,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    base_data: dict,
    url_create: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_TEMPLATE_CREATE],
        business_area=business_area,
        program=program,
    )

    # Create users with appropriate permissions
    partner_empty = PartnerFactory(name="EmptyPartner")
    user_can_approve = UserFactory(partner=partner_empty, first_name="Bob")
    create_user_role_with_permissions(
        user=user_can_approve,
        permissions=[Permissions.PDU_ONLINE_APPROVE],
        business_area=business_area,
        program=program,
    )

    user_can_all = UserFactory(partner=partner_empty, first_name="David")
    create_user_role_with_permissions(
        user=user_can_all,
        permissions=[
            Permissions.PDU_ONLINE_SAVE_DATA,
            Permissions.PDU_ONLINE_APPROVE,
            Permissions.PDU_ONLINE_MERGE,
        ],
        business_area=business_area,
        program=program,
    )

    can_merge_but_not_authorized = UserFactory(partner=partner_empty, first_name="Eve")
    create_user_role_with_permissions(
        user=can_merge_but_not_authorized,
        permissions=[Permissions.PDU_ONLINE_MERGE],
        business_area=business_area,
        program=program,
    )

    data = {
        "authorized_users": [user_can_approve.pk, user_can_all.pk],
        **base_data,
    }

    response = authenticated_client.post(url_create, data=data)
    assert response.status_code == status.HTTP_201_CREATED

    assert PDUOnlineEdit.objects.count() == 1
    pdu_online_edit = PDUOnlineEdit.objects.first()
    assert pdu_online_edit.authorized_users.count() == 2
    assert pdu_online_edit.authorized_users.filter(pk=user_can_approve.pk).exists()
    assert pdu_online_edit.authorized_users.filter(pk=user_can_all.pk).exists()
    assert not pdu_online_edit.authorized_users.filter(pk=can_merge_but_not_authorized.pk).exists()


def test_create_pdu_online_edit_duplicate_field(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household1: Any,
    household2: Any,
    individual1: Any,
    individual2: Any,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    url_create: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_TEMPLATE_CREATE],
        business_area=business_area,
        program=program,
    )
    data = {
        "rounds_data": [
            {
                "field": "vaccination_records_update",
                "round": 2,
                "round_name": "February vaccination",
            },
            {
                "field": "vaccination_records_update",
                "round": 4,
                "round_name": "April",
            },
        ],
        "filters": {
            "received_assistance": True,
        },
    }

    response = authenticated_client.post(url_create, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert response_json == {"rounds_data": ["Each Field can only be used once in the template."]}


def test_create_pdu_online_edit_field_is_editable_flag(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household1: Any,
    household2: Any,
    individual1: Any,
    individual2: Any,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    url_create: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_TEMPLATE_CREATE],
        business_area=business_area,
        program=program,
    )

    # individual already has a value for vaccination_records_update in round 2 - value should be
    # retrieved and is_editable should be False
    individual2.flex_fields["vaccination_records_update"]["2"]["value"] = 1.0
    individual2.save()

    data = {
        "rounds_data": [
            {
                "field": "vaccination_records_update",
                "round": 2,
                "round_name": "February vaccination",
            },
            {
                "field": "health_records_update",
                "round": 4,
                "round_name": "April",
            },
        ],
        "filters": {
            "received_assistance": True,
        },
    }

    response = authenticated_client.post(url_create, data=data)
    assert response.status_code == status.HTTP_201_CREATED

    pdu_online_edit = PDUOnlineEdit.objects.first()
    assert pdu_online_edit.edit_data[0]["pdu_fields"]["vaccination_records_update"]["value"] == 1.0
    assert pdu_online_edit.edit_data[0]["pdu_fields"]["vaccination_records_update"]["collection_date"] is None
    assert pdu_online_edit.edit_data[0]["pdu_fields"]["vaccination_records_update"]["is_editable"] is False

    assert pdu_online_edit.edit_data[0]["pdu_fields"]["health_records_update"]["value"] is None
    assert pdu_online_edit.edit_data[0]["pdu_fields"]["health_records_update"]["collection_date"] is None
    assert pdu_online_edit.edit_data[0]["pdu_fields"]["health_records_update"]["is_editable"] is True


def test_create_pdu_online_edit_with_covered_individual(
    authenticated_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Program,
    household1: Any,
    household2: Any,
    individual1: Any,
    individual2: Any,
    pdu_field_vaccination: Any,
    pdu_field_health: Any,
    url_create: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PDU_TEMPLATE_CREATE],
        business_area=business_area,
        program=program,
    )

    # individual already has values for all pdu fields used in the edit - should be excluded from the edit
    individual2.flex_fields["vaccination_records_update"]["2"]["value"] = 1.0
    individual2.save()

    data = {
        "rounds_data": [
            {
                "field": "vaccination_records_update",
                "round": 2,
                "round_name": "February vaccination",
            },
        ],
        "filters": {
            "received_assistance": True,
        },
    }

    response = authenticated_client.post(url_create, data=data)
    assert response.status_code == status.HTTP_201_CREATED

    pdu_online_edit = PDUOnlineEdit.objects.first()
    assert pdu_online_edit.number_of_records == 0
