"""Tests for Message ViewSet."""

import datetime
from typing import Any, List
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
def partner():
    return PartnerFactory(name="unittest")


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner, first_name="Test", last_name="User")


@pytest.fixture
def authenticated_client(api_client, user):
    return api_client(user)


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
def households(program_active, payment_plan, business_area):
    birth_date_for_50yo = timezone.now().date() - datetime.timedelta(days=50 * 365)
    rdi = RegistrationDataImportFactory(program=program_active, business_area=business_area)
    households = []
    for i in range(3):
        hoh = IndividualFactory(
            household=None,
            birth_date=birth_date_for_50yo,
            sex="MALE",
            program=program_active,
            business_area=business_area,
            registration_data_import=rdi,
            phone_no=f"+4860012345{i}",
            phone_no_valid=True,
        )
        hh = HouseholdFactory(
            program=program_active,
            head_of_household=hoh,
            business_area=business_area,
            registration_data_import=rdi,
        )
        PaymentFactory(
            parent=payment_plan,
            program=program_active,
            household=hh,
            business_area=business_area,
            collector=hoh,
        )
        households.append(hh)
    return households


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


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_msg_get_list(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    msg_1,
    msg_2,
    url_list,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_list)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        response_results = response.json()["results"]
        assert len(response_results) == 2
        for i, message in enumerate([msg_1, msg_2]):
            message_result = response_results[i]
            assert message_result["id"] == str(message.id)
            assert message_result["unicef_id"] == str(message.unicef_id)
            assert message_result["title"] == message.title
            assert message_result["number_of_recipients"] == message.number_of_recipients
            assert message_result["created_by"] == f"{user.first_name} {user.last_name}"
            assert message_result["created_at"] == f"{message.created_at:%Y-%m-%dT%H:%M:%SZ}"


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


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_msg_get_count(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    msg_1,
    msg_2,
    url_count,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_count)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        assert response.status_code == status.HTTP_200_OK
        resp_data = response.json()
        assert resp_data["count"] == 2


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS],
            status.HTTP_200_OK,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_msg_details(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    msg_1,
    url_details,
) -> None:
    create_user_role_with_permissions(user, permissions, business_area, program_active)
    response = authenticated_client.get(url_details)

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
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


def test_msg_details_admin_url(
    authenticated_client,
    user,
    msg_1,
    url_details,
) -> None:
    user.is_superuser = True
    user.save()
    response = authenticated_client.get(url_details)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["admin_url"] == msg_1.admin_url


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        (
            [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
            status.HTTP_201_CREATED,
        ),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_new_message(
    permissions: List,
    expected_status: int,
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    households,
    url_list,
) -> None:
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
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert response.status_code == status.HTTP_201_CREATED
        resp_data = response.json()
        assert "id" in resp_data
        assert resp_data["title"] == "New Message for Active Program"
        assert resp_data["body"] == "Thank you for tests! Looks Good To Me!"
        assert resp_data["sample_size"] == 1


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


def test_create_message_validation_error(
    create_user_role_with_permissions: Any,
    authenticated_client,
    user,
    business_area,
    program_active,
    url_list,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE],
        business_area,
        program_active,
    )
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=business_area,
        program_cycle=program_active.cycles.first(),
    )
    rdi = RegistrationDataImportFactory(imported_by=user, business_area=business_area, program=program_active)

    response = authenticated_client.post(
        url_list,
        {
            "title": "Test Error",
            "body": "Thank you for tests!",
            "sampling_type": Survey.SAMPLING_FULL_LIST,
            "full_list_arguments": {"excluded_admin_areas": []},
            "payment_plan": str(payment_plan.pk),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No recipients found for the given criteria" in response.json()

    response_2 = authenticated_client.post(
        url_list,
        {
            "title": "Test Error",
            "body": "Thank you for tests!",
            "sampling_type": Survey.SAMPLING_FULL_LIST,
            "full_list_arguments": {"excluded_admin_areas": []},
            "random_sampling_arguments": None,
            "registration_data_import": str(rdi.pk),
        },
        format="json",
    )
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert "No recipients found for the given criteria" in response_2.json()


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
    msg_1.created_at = timezone.make_aware(datetime.datetime(year=2021, month=3, day=12))
    msg_1.save()
    msg_2.created_at = timezone.make_aware(datetime.datetime(year=2020, month=5, day=15))
    msg_2.save()
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
    assert results[0]["id"] == str(msg_2.id)


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
