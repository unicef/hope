"""Tests for Message ViewSet."""

import datetime
from typing import Any
from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

from django.urls import reverse
from django.utils import timezone
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CommunicationMessageFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import PaymentPlan, Program, Survey

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(code="0060", slug="afghanistan", name="Afghanistan", active=True)


@pytest.fixture
def partner(business_area):
    p = PartnerFactory(name="unittest")
    p.allowed_business_areas.add(business_area)
    return p


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner, first_name="Test", last_name="User")


@pytest.fixture
def superuser(partner):
    return UserFactory(partner=partner, first_name="Super", last_name="User", is_superuser=True)


@pytest.fixture
def authenticated_client(api_client, user):
    return api_client(user)


@pytest.fixture
def authenticated_superuser_client(api_client, superuser):
    return api_client(superuser)


@pytest.fixture
def program_active(business_area):
    program = ProgramFactory(
        name="Test Active Program",
        business_area=business_area,
        status=Program.ACTIVE,
    )
    ProgramCycleFactory(program=program)
    return program


@pytest.fixture
def program_finished(business_area):
    return ProgramFactory(
        name="Test Finished Program",
        business_area=business_area,
        status=Program.FINISHED,
    )


@pytest.fixture
def payment_plan(user, business_area, program_active):
    return PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )


@pytest.fixture
def rdi(program_active, business_area):
    return RegistrationDataImportFactory(program=program_active, business_area=business_area)


@pytest.fixture
def individual_hoh_1(program_active, business_area, rdi):
    birth_date_for_50yo = timezone.now().date() - datetime.timedelta(days=50 * 365)
    return IndividualFactory(
        household=None,
        birth_date=birth_date_for_50yo,
        sex="MALE",
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
        phone_no="+48600123450",
        phone_no_valid=True,
    )


@pytest.fixture
def individual_hoh_2(program_active, business_area, rdi):
    birth_date_for_50yo = timezone.now().date() - datetime.timedelta(days=50 * 365)
    return IndividualFactory(
        household=None,
        birth_date=birth_date_for_50yo,
        sex="MALE",
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
        phone_no="+48600123451",
        phone_no_valid=True,
    )


@pytest.fixture
def individual_hoh_3(program_active, business_area, rdi):
    birth_date_for_50yo = timezone.now().date() - datetime.timedelta(days=50 * 365)
    return IndividualFactory(
        household=None,
        birth_date=birth_date_for_50yo,
        sex="MALE",
        program=program_active,
        business_area=business_area,
        registration_data_import=rdi,
        phone_no="+48600123452",
        phone_no_valid=True,
    )


@pytest.fixture
def household_1(program_active, business_area, rdi, individual_hoh_1):
    return HouseholdFactory(
        program=program_active,
        head_of_household=individual_hoh_1,
        business_area=business_area,
        registration_data_import=rdi,
    )


@pytest.fixture
def household_2(program_active, business_area, rdi, individual_hoh_2):
    return HouseholdFactory(
        program=program_active,
        head_of_household=individual_hoh_2,
        business_area=business_area,
        registration_data_import=rdi,
    )


@pytest.fixture
def household_3(program_active, business_area, rdi, individual_hoh_3):
    return HouseholdFactory(
        program=program_active,
        head_of_household=individual_hoh_3,
        business_area=business_area,
        registration_data_import=rdi,
    )


@pytest.fixture
def payment_for_hh_1(payment_plan, program_active, business_area, household_1, individual_hoh_1):
    return PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=household_1,
        business_area=business_area,
        collector=individual_hoh_1,
    )


@pytest.fixture
def payment_for_hh_2(payment_plan, program_active, business_area, household_2, individual_hoh_2):
    return PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=household_2,
        business_area=business_area,
        collector=individual_hoh_2,
    )


@pytest.fixture
def payment_for_hh_3(payment_plan, program_active, business_area, household_3, individual_hoh_3):
    return PaymentFactory(
        parent=payment_plan,
        program=program_active,
        household=household_3,
        business_area=business_area,
        collector=individual_hoh_3,
    )


@pytest.fixture
def households(household_1, household_2, household_3, payment_for_hh_1, payment_for_hh_2, payment_for_hh_3):
    return [household_1, household_2, household_3]


@pytest.fixture
def msg_1(program_active, business_area, user):
    return CommunicationMessageFactory(
        program=program_active,
        business_area=business_area,
        title="MSG title",
        body="MSG body",
        created_by=user,
        sampling_type=Survey.SAMPLING_FULL_LIST,
        payment_plan=PaymentPlanFactory(
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=user,
            business_area=business_area,
            program_cycle=program_active.cycles.first(),
        ),
    )


@pytest.fixture
def msg_2(program_active, business_area, user):
    return CommunicationMessageFactory(
        program=program_active,
        business_area=business_area,
        title="MSG title 2",
        body="MSG body 2",
        created_by=user,
        sampling_type=Survey.SAMPLING_RANDOM,
        payment_plan=PaymentPlanFactory(
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=user,
            business_area=business_area,
            program_cycle=program_active.cycles.first(),
        ),
    )


@pytest.fixture
def msg_3(program_finished, business_area, user):
    return CommunicationMessageFactory(
        program=program_finished,
        business_area=business_area,
        title="MSG title in different program",
        body="MSG body in different program",
        created_by=user,
        sampling_type=Survey.SAMPLING_RANDOM,
    )


@pytest.fixture
def msg_created_2021(program_active, business_area, user):
    msg = CommunicationMessageFactory(
        program=program_active,
        business_area=business_area,
        title="MSG 2021",
        body="MSG body 2021",
        created_by=user,
        sampling_type=Survey.SAMPLING_FULL_LIST,
    )
    msg.created_at = timezone.make_aware(datetime.datetime(year=2021, month=3, day=12))
    msg.save()
    return msg


@pytest.fixture
def msg_created_2020(program_active, business_area, user):
    msg = CommunicationMessageFactory(
        program=program_active,
        business_area=business_area,
        title="MSG 2020",
        body="MSG body 2020",
        created_by=user,
        sampling_type=Survey.SAMPLING_RANDOM,
    )
    msg.created_at = timezone.make_aware(datetime.datetime(year=2020, month=5, day=15))
    msg.save()
    return msg


@pytest.fixture
def payment_plan_empty(user, business_area, program_active):
    return PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )


@pytest.fixture
def rdi_empty(user, business_area, program_active):
    return RegistrationDataImportFactory(
        imported_by=user,
        business_area=business_area,
        program=program_active,
    )


@pytest.fixture
def url_list(business_area, program_active):
    return reverse(
        "api:accountability:messages-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )


@pytest.fixture
def url_count(business_area, program_active):
    return reverse(
        "api:accountability:messages-count",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )


@pytest.fixture
def url_details(business_area, program_active, msg_1):
    return reverse(
        "api:accountability:messages-detail",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
            "pk": str(msg_1.pk),
        },
    )


def test_msg_get_list_returns_data_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    msg_1,
    msg_2,
    url_list,
) -> None:
    permissions = [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST]
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_list)

    assert response.status_code == status.HTTP_200_OK
    response_results = response.json()["results"]
    assert len(response_results) == 2
    assert response_results[0]["id"] == str(msg_1.id)
    assert response_results[0]["unicef_id"] == str(msg_1.unicef_id)
    assert response_results[0]["title"] == msg_1.title
    assert response_results[0]["number_of_recipients"] == msg_1.number_of_recipients
    assert response_results[0]["created_by"] == f"{user.first_name} {user.last_name}"
    assert response_results[0]["created_at"] == f"{msg_1.created_at:%Y-%m-%dT%H:%M:%SZ}"
    assert response_results[1]["id"] == str(msg_2.id)
    assert response_results[1]["unicef_id"] == str(msg_2.unicef_id)
    assert response_results[1]["title"] == msg_2.title
    assert response_results[1]["number_of_recipients"] == msg_2.number_of_recipients
    assert response_results[1]["created_by"] == f"{user.first_name} {user.last_name}"
    assert response_results[1]["created_at"] == f"{msg_2.created_at:%Y-%m-%dT%H:%M:%SZ}"


def test_msg_get_list_returns_403_without_permission(
    authenticated_client,
    msg_1,
    msg_2,
    url_list,
) -> None:
    response = authenticated_client.get(url_list)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_msg_filter_by_program(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    msg_1,
    msg_2,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(url_list + "?" + urlencode({"program": str(program_active.pk)}))

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 2
    results_ids = [msg["id"] for msg in resp_data["results"]]
    assert str(msg_1.id) in results_ids
    assert str(msg_2.id) in results_ids


def test_msg_get_count_returns_data_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    msg_1,
    msg_2,
    url_count,
) -> None:
    permissions = [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST]
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_count)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert resp_data["count"] == 2


def test_msg_get_count_returns_403_without_permission(
    authenticated_client,
    msg_1,
    msg_2,
    url_count,
) -> None:
    response = authenticated_client.get(url_count)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_msg_details_returns_data_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    msg_1,
    url_details,
) -> None:
    permissions = [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS]
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_details)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert "id" in resp_data
    assert resp_data["body"] == "MSG body"
    assert resp_data["households"] is not None
    assert resp_data["payment_plan"] is not None
    assert resp_data["registration_data_import"] is None
    assert resp_data["sampling_type"] == Survey.SAMPLING_FULL_LIST
    assert resp_data["full_list_arguments"]["excluded_admin_areas"] == []
    assert resp_data["random_sampling_arguments"] is None
    assert resp_data["sample_size"] == 0
    assert resp_data["admin_url"] is None


def test_msg_details_returns_403_without_permission(
    authenticated_client,
    msg_1,
    url_details,
) -> None:
    response = authenticated_client.get(url_details)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_msg_details_admin_url(
    authenticated_superuser_client,
    msg_1,
    url_details,
) -> None:
    response = authenticated_superuser_client.get(url_details)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["admin_url"] == msg_1.admin_url


def test_create_new_message_returns_created_with_permission(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    households,
    url_list,
) -> None:
    permissions = [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE]
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    broadcast_message_mock = MagicMock(return_value=None)
    with (
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
            MagicMock(return_value=None),
        ),
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
            broadcast_message_mock,
        ),
    ):
        response = authenticated_client.post(
            url_list,
            {
                "title": "New Message for Active Program",
                "body": "Thank you for tests! Looks Good To Me!",
                "sampling_type": Survey.SAMPLING_FULL_LIST,
                "full_list_arguments": {"excluded_admin_areas": []},
                "random_sampling_arguments": None,
                "households": [str(households[0].pk)],
            },
            format="json",
        )
    assert response.status_code == status.HTTP_201_CREATED
    resp_data = response.json()
    assert "id" in resp_data
    assert resp_data["title"] == "New Message for Active Program"
    assert resp_data["body"] == "Thank you for tests! Looks Good To Me!"
    assert resp_data["sample_size"] == 1


def test_create_new_message_returns_403_without_permission(
    authenticated_client,
    households,
    url_list,
) -> None:
    broadcast_message_mock = MagicMock(return_value=None)
    with (
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
            MagicMock(return_value=None),
        ),
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
            broadcast_message_mock,
        ),
    ):
        response = authenticated_client.post(
            url_list,
            {
                "title": "New Message for Active Program",
                "body": "Thank you for tests! Looks Good To Me!",
                "sampling_type": Survey.SAMPLING_FULL_LIST,
                "full_list_arguments": {"excluded_admin_areas": []},
                "random_sampling_arguments": None,
                "households": [str(households[0].pk)],
            },
            format="json",
        )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_new_message_by_households_full_list(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    households,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    broadcast_message_mock = MagicMock(return_value=None)
    with (
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
            MagicMock(return_value=None),
        ),
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
            broadcast_message_mock,
        ),
    ):
        response = authenticated_client.post(
            url_list,
            {
                "title": "New Message 1 for Active Program",
                "body": "Thank you for tests! Looks Good To Me!",
                "sampling_type": Survey.SAMPLING_FULL_LIST,
                "full_list_arguments": {"excluded_admin_areas": []},
                "households": [str(hh.id) for hh in households],
            },
            format="json",
        )
    assert response.status_code == status.HTTP_201_CREATED
    resp_data = response.json()
    assert resp_data["sample_size"] == len(households)


def test_create_new_message_by_households_random(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    households,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    broadcast_message_mock = MagicMock(return_value=None)
    with (
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
            MagicMock(return_value=None),
        ),
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
            broadcast_message_mock,
        ),
    ):
        response = authenticated_client.post(
            url_list,
            {
                "title": "New Message 2 for Active Program",
                "body": "Thank you for tests! Looks Good To Me!",
                "sampling_type": Survey.SAMPLING_RANDOM,
                "random_sampling_arguments": {
                    "age": {"max": 80, "min": 15},
                    "sex": "MALE",
                    "margin_of_error": 20.0,
                    "confidence_interval": 0.9,
                    "excluded_admin_areas": [],
                },
                "households": [str(hh.id) for hh in households],
            },
            format="json",
        )
    assert response.status_code == status.HTTP_201_CREATED
    resp_data = response.json()
    assert resp_data["sample_size"] == 1


def test_create_new_message_by_target_population_full_list(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan,
    households,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    broadcast_message_mock = MagicMock(return_value=None)
    with (
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
            MagicMock(return_value=None),
        ),
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
            broadcast_message_mock,
        ),
    ):
        response = authenticated_client.post(
            url_list,
            {
                "title": "New Message 1 for Active Program",
                "body": "Thank you for tests! Looks Good To Me!",
                "sampling_type": Survey.SAMPLING_FULL_LIST,
                "full_list_arguments": {"excluded_admin_areas": []},
                "payment_plan": str(payment_plan.id),
            },
            format="json",
        )
    assert response.status_code == status.HTTP_201_CREATED
    resp_data = response.json()
    assert resp_data["sample_size"] == len(households)


def test_create_new_message_target_population_random(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan,
    households,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    broadcast_message_mock = MagicMock(return_value=None)
    with (
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__",
            MagicMock(return_value=None),
        ),
        patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.broadcast_message",
            broadcast_message_mock,
        ),
    ):
        response = authenticated_client.post(
            url_list,
            {
                "title": "New Message 2 for Active Program",
                "body": "Thank you for tests! Looks Good To Me!",
                "sampling_type": Survey.SAMPLING_RANDOM,
                "random_sampling_arguments": {
                    "age": {"max": 80, "min": 15},
                    "sex": "MALE",
                    "margin_of_error": 20.0,
                    "confidence_interval": 0.9,
                    "excluded_admin_areas": [],
                },
                "payment_plan": str(payment_plan.id),
            },
            format="json",
        )
    assert response.status_code == status.HTTP_201_CREATED
    resp_data = response.json()
    assert resp_data["sample_size"] == 1


def test_create_message_validation_error_payment_plan_no_recipients(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan_empty,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    response = authenticated_client.post(
        url_list,
        {
            "title": "Test Error",
            "body": "Thank you for tests!",
            "sampling_type": Survey.SAMPLING_FULL_LIST,
            "full_list_arguments": {"excluded_admin_areas": []},
            "payment_plan": str(payment_plan_empty.pk),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No recipients found for the given criteria" in response.json()


def test_create_message_validation_error_rdi_no_recipients(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    rdi_empty,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    response = authenticated_client.post(
        url_list,
        {
            "title": "Test Error",
            "body": "Thank you for tests!",
            "sampling_type": Survey.SAMPLING_FULL_LIST,
            "full_list_arguments": {"excluded_admin_areas": []},
            "random_sampling_arguments": None,
            "registration_data_import": str(rdi_empty.pk),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No recipients found for the given criteria" in response.json()


def test_create_message_invalid_request(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    households,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )

    response = authenticated_client.post(
        url_list,
        {
            "title": "Test Error",
            "body": "Thank you for tests!",
            "sampling_type": Survey.SAMPLING_RANDOM,
            "full_list_arguments": {"excluded_admin_areas": []},
            "random_sampling_arguments": {
                "age": {"max": 80, "min": 30},
                "sex": "MALE",
                "margin_of_error": 20.0,
                "confidence_interval": 0.9,
                "excluded_admin_areas": [],
            },
            "households": [str(households[0].pk)],
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert f"Must not provide full_list_arguments for {Survey.SAMPLING_RANDOM}" in response.json()


def test_sample_size(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    payment_plan,
    households,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    url = reverse(
        "api:accountability:messages-sample-size",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_active.slug,
        },
    )
    data = {
        "payment_plan": str(payment_plan.pk),
        "sampling_type": Survey.SAMPLING_RANDOM,
        "random_sampling_arguments": {
            "age": {"max": 80, "min": 15},
            "sex": "MALE",
            "margin_of_error": 20.0,
            "confidence_interval": 0.9,
            "excluded_admin_areas": [],
        },
    }

    response = authenticated_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {
        "number_of_recipients": 3,
        "sample_size": 1,
        "excluded_recipients_count": 0,
    }


def test_filter_messages_by_created_at(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    msg_created_2021,
    msg_created_2020,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(
        url_list,
        {
            "created_at_after": "2020-01-01",
            "created_at_before": "2020-12-31",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(msg_created_2020.id)


def test_filter_messages_by_title(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    msg_1,
    msg_2,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(url_list, {"title": "MSG title"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 2
    results_ids = [msg["id"] for msg in results]
    assert str(msg_1.id) in results_ids
    assert str(msg_2.id) in results_ids

    response = authenticated_client.get(url_list, {"title": "2"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    results_ids = [msg["id"] for msg in results]
    assert str(msg_2.id) in results_ids


def test_filter_messages_by_body(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    msg_1,
    msg_2,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(url_list, {"body": "MSG body"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 2
    results_ids = [msg["id"] for msg in results]
    assert str(msg_1.id) in results_ids
    assert str(msg_2.id) in results_ids

    response = authenticated_client.get(url_list, {"body": "2"})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    results_ids = [msg["id"] for msg in results]
    assert str(msg_2.id) in results_ids


def test_filter_messages_by_sampling_type(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    msg_1,
    msg_2,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
        business_area,
        whole_business_area_access=True,
    )
    response = authenticated_client.get(url_list, {"sampling_type": Survey.SAMPLING_FULL_LIST})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(msg_1.id)

    response = authenticated_client.get(url_list, {"sampling_type": Survey.SAMPLING_RANDOM})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == str(msg_2.id)
