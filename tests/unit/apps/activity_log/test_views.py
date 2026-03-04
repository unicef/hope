from typing import Any
from urllib.parse import urlencode

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.activity_log.utils import create_diff
from hope.apps.grievance.models import GrievanceTicket
from hope.models import LogEntry, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def partner(db: Any) -> Any:
    return PartnerFactory(name="unittest")


@pytest.fixture
def user(partner: Any) -> Any:
    return UserFactory(partner=partner, first_name="Test", last_name="User")


@pytest.fixture
def partner_2(db: Any) -> Any:
    return PartnerFactory(name="Test_2")


@pytest.fixture
def user_without_perms(partner_2: Any) -> Any:
    return UserFactory(partner=partner_2)


@pytest.fixture
def program_1(business_area: Any) -> Any:
    return ProgramFactory(
        name="Program 1",
        business_area=business_area,
        pk="ad17c53d-11b0-4e9b-8407-2e034f03fd31",
    )


@pytest.fixture
def program_2(business_area: Any) -> Any:
    return ProgramFactory(
        name="Program 2",
        business_area=business_area,
        pk="c74612a1-212c-4148-be5b-4b41d20e623c",
    )


@pytest.fixture
def grievance_ticket(business_area: Any) -> Any:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
    )


@pytest.fixture
def log_entries(
    user: Any,
    user_without_perms: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    grievance_ticket: Any,
) -> dict:
    l1 = LogEntry.objects.create(
        action=LogEntry.UPDATE,
        content_object=program_1,
        user=user,
        business_area=business_area,
        object_repr=str(program_1),
        changes=create_diff(None, program_1, Program.ACTIVITY_LOG_MAPPING),
    )
    l1.programs.add(program_1)

    l2 = LogEntry.objects.create(
        action=LogEntry.CREATE,
        content_object=program_2,
        user=user,
        business_area=business_area,
        object_repr=str(program_2),
        changes=create_diff(None, program_2, Program.ACTIVITY_LOG_MAPPING),
    )
    l2.programs.add(program_2)

    l3 = LogEntry.objects.create(
        action=LogEntry.CREATE,
        content_object=program_1,
        user=user_without_perms,
        business_area=business_area,
        object_repr=str(program_1),
        changes=create_diff(None, program_1, Program.ACTIVITY_LOG_MAPPING),
    )
    l3.programs.add(program_1)

    l4 = LogEntry.objects.create(
        action=LogEntry.CREATE,
        content_object=grievance_ticket,
        user=None,
        business_area=business_area,
        object_repr=str(grievance_ticket),
        changes=create_diff(None, grievance_ticket, GrievanceTicket.ACTIVITY_LOG_MAPPING),
    )
    l4.programs.add(program_2)

    l5 = LogEntry.objects.create(
        action=LogEntry.CREATE,
        content_object=program_2,
        user=user_without_perms,
        business_area=None,
        object_repr=str(program_2),
        changes=create_diff(None, program_2, Program.ACTIVITY_LOG_MAPPING),
    )
    l5.programs.add(program_2)

    return {
        "l1": l1,
        "l2": l2,
        "l3": l3,
        "l4": l4,
        "l5": l5,
    }


@pytest.fixture
def url_list(business_area: Any) -> str:
    return reverse(
        "api:activity-logs:activity-logs-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def url_count(business_area: Any) -> str:
    return reverse(
        "api:activity-logs:activity-logs-count",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def url_choices(business_area: Any) -> str:
    return reverse(
        "api:activity-logs:activity-logs-log-entry-action-choices",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def url_list_per_program(business_area: Any, program_1: Any) -> str:
    return reverse(
        "api:activity-logs:activity-logs-per-program-list",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_1.slug,
        },
    )


@pytest.fixture
def url_count_per_program(business_area: Any, program_1: Any) -> str:
    return reverse(
        "api:activity-logs:activity-logs-per-program-count",
        kwargs={
            "business_area_slug": business_area.slug,
            "program_slug": program_1.slug,
        },
    )


@pytest.mark.enable_activity_log
def test_activity_logs_list_returns_correct_count_when_user_has_permission(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)
    response = client.get(url_list)

    assert response.status_code == status.HTTP_200_OK
    response_results = response.json()["results"]
    assert len(response_results) == 4


@pytest.mark.enable_activity_log
def test_activity_logs_list_returns_logs_in_correct_order(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)
    response = client.get(url_list)

    response_results = response.json()["results"]
    l1 = log_entries["l1"]
    l2 = log_entries["l2"]
    l3 = log_entries["l3"]
    l4 = log_entries["l4"]

    assert response_results[0]["object_id"] == str(l4.object_id)
    assert response_results[1]["object_id"] == str(l3.object_id)
    assert response_results[2]["object_id"] == str(l2.object_id)
    assert response_results[3]["object_id"] == str(l1.object_id)


@pytest.mark.enable_activity_log
def test_activity_logs_list_returns_log_with_correct_fields(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)
    response = client.get(url_list)

    response_results = response.json()["results"]
    l1 = log_entries["l1"]
    log_result = response_results[3]

    assert log_result["object_id"] == str(l1.object_id)
    assert log_result["action"] == l1.get_action_display()
    assert log_result["changes"] == l1.changes
    assert log_result["user"] == f"{l1.user.first_name} {l1.user.last_name}"
    assert log_result["object_repr"] == l1.object_repr
    assert log_result["content_type"] == l1.content_type.name
    assert log_result["timestamp"] == f"{l1.timestamp:%Y-%m-%dT%H:%M:%SZ}"


@pytest.mark.enable_activity_log
def test_activity_logs_list_returns_is_user_generated_for_grievance_ticket(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)
    response = client.get(url_list)

    response_results = response.json()["results"]
    l4 = log_entries["l4"]
    log_result = response_results[0]

    assert log_result["object_id"] == str(l4.object_id)
    expected_is_user_generated = l4.content_object.grievance_type_to_string() == "user"
    assert log_result["is_user_generated"] == expected_is_user_generated


@pytest.mark.enable_activity_log
def test_activity_logs_list_returns_correct_program_slugs(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)
    response = client.get(url_list)

    response_results = response.json()["results"]

    assert response_results[0]["program_slug"] is None
    assert response_results[1]["program_slug"] == program_1.slug
    assert response_results[2]["program_slug"] == program_2.slug
    assert response_results[3]["program_slug"] == program_1.slug


@pytest.mark.enable_activity_log
def test_activity_logs_list_returns_403_when_user_has_no_permission(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [], business_area, program_1)
    create_user_role_with_permissions(user, [], business_area, program_2)
    client = api_client(user)
    response = client.get(url_list)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.enable_activity_log
def test_activity_logs_count_returns_count_when_user_has_permission(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    url_count: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)
    response = client.get(url_count)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert resp_data["count"] == 4


@pytest.mark.enable_activity_log
def test_activity_logs_count_returns_403_when_user_has_no_permission(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    url_count: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [], business_area, program_1)
    create_user_role_with_permissions(user, [], business_area, program_2)
    client = api_client(user)
    response = client.get(url_count)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.enable_activity_log
def test_activity_logs_list_per_program_returns_correct_count(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    log_entries: dict,
    url_list_per_program: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    client = api_client(user)
    response = client.get(url_list_per_program)

    assert response.status_code == status.HTTP_200_OK
    response_results = response.json()["results"]
    assert len(response_results) == 2


@pytest.mark.enable_activity_log
def test_activity_logs_list_per_program_returns_logs_in_correct_order(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    log_entries: dict,
    url_list_per_program: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    client = api_client(user)
    response = client.get(url_list_per_program)

    response_results = response.json()["results"]
    l1 = log_entries["l1"]
    l3 = log_entries["l3"]

    assert response_results[0]["object_id"] == str(l3.object_id)
    assert response_results[1]["object_id"] == str(l1.object_id)


@pytest.mark.enable_activity_log
def test_activity_logs_list_per_program_returns_log_with_correct_fields(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    log_entries: dict,
    url_list_per_program: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    client = api_client(user)
    response = client.get(url_list_per_program)

    response_results = response.json()["results"]
    l1 = log_entries["l1"]
    log_result = response_results[1]

    assert log_result["object_id"] == str(l1.object_id)
    assert log_result["action"] == l1.get_action_display()
    assert log_result["changes"] == l1.changes
    assert log_result["user"] == f"{l1.user.first_name} {l1.user.last_name}"
    assert log_result["object_repr"] == l1.object_repr
    assert log_result["content_type"] == l1.content_type.name
    assert log_result["timestamp"] == f"{l1.timestamp:%Y-%m-%dT%H:%M:%SZ}"
    assert log_result["is_user_generated"] is None


@pytest.mark.enable_activity_log
def test_activity_logs_list_per_program_returns_403_when_user_has_no_permission(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    url_list_per_program: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [], business_area, program_1)
    client = api_client(user)
    response = client.get(url_list_per_program)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.enable_activity_log
def test_activity_logs_count_per_program_returns_count_when_user_has_permission(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    log_entries: dict,
    url_count_per_program: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    client = api_client(user)
    response = client.get(url_count_per_program)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert resp_data["count"] == 2


@pytest.mark.enable_activity_log
def test_activity_logs_count_per_program_returns_403_when_user_has_no_permission(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    url_count_per_program: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [], business_area, program_1)
    client = api_client(user)
    response = client.get(url_count_per_program)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.enable_activity_log
def test_activity_logs_filters_by_object_id(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)

    url = (
        reverse("api:activity-logs:activity-logs-list", kwargs={"business_area_slug": business_area.slug})
        + "?"
        + urlencode({"object_id": "c74612a1-212c-4148-be5b-4b41d20e623c"})
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    log = resp_data["results"][0]
    assert "object_id" in log
    assert log["object_id"] == "c74612a1-212c-4148-be5b-4b41d20e623c"
    assert log["object_repr"] == "Program 2"


@pytest.mark.enable_activity_log
def test_activity_logs_filters_by_user_id(
    api_client: Any,
    user: Any,
    user_without_perms: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    log_entries: dict,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)

    url = (
        reverse("api:activity-logs:activity-logs-list", kwargs={"business_area_slug": business_area.slug})
        + "?"
        + urlencode({"user_id": str(user_without_perms.pk)})
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    log = resp_data["results"][0]
    assert "object_id" in log
    assert log["object_id"] == "ad17c53d-11b0-4e9b-8407-2e034f03fd31"
    assert log["object_repr"] == "Program 1"
    assert log["user"] == f"{user_without_perms.first_name} {user_without_perms.last_name}"


@pytest.mark.enable_activity_log
def test_activity_logs_filters_by_module(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    grievance_ticket: Any,
    log_entries: dict,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)

    url = (
        reverse("api:activity-logs:activity-logs-list", kwargs={"business_area_slug": business_area.slug})
        + "?"
        + urlencode({"module": "grievanceticket"})
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 1
    log = resp_data["results"][0]
    assert "object_id" in log
    assert log["object_id"] == str(grievance_ticket.pk)
    assert log["object_repr"] == str(grievance_ticket)
    assert log["is_user_generated"] is True


@pytest.mark.enable_activity_log
def test_activity_logs_filters_by_program_id(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    program_2: Any,
    grievance_ticket: Any,
    log_entries: dict,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_2)
    client = api_client(user)

    url = (
        reverse("api:activity-logs:activity-logs-list", kwargs={"business_area_slug": business_area.slug})
        + "?"
        + urlencode({"program_id": str(program_2.pk)})
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data["results"]) == 2
    log = resp_data["results"][0]
    assert "object_id" in log
    assert log["object_id"] == str(grievance_ticket.pk)
    assert log["object_repr"] == str(grievance_ticket)
    assert log["is_user_generated"] is True


def test_activity_logs_choices_returns_action_choices(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    url_choices: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    client = api_client(user)
    response = client.get(url_choices)

    assert response.status_code == status.HTTP_200_OK
    resp_data = response.json()
    assert len(resp_data) == 4
    choice = resp_data[0]
    assert "name" in choice
    assert "value" in choice


@pytest.mark.enable_activity_log
def test_activity_logs_list_search_filters_by_action(
    api_client: Any,
    user: Any,
    business_area: Any,
    program_1: Any,
    log_entries: dict,
    url_list: str,
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(user, [Permissions.ACTIVITY_LOG_VIEW], business_area, program_1)
    client = api_client(user)
    response = client.get(url_list + "?limit=20&offset=0&search=upda")

    assert response.status_code == status.HTTP_200_OK
    response_results = response.json()["results"]
    assert len(response_results) == 1

    l1 = log_entries["l1"]
    log_result = response_results[0]
    assert log_result["object_id"] == str(l1.object_id)
    assert log_result["action"] == l1.get_action_display()
    assert log_result["changes"] == l1.changes
    assert log_result["user"] == (f"{l1.user.first_name} {l1.user.last_name}" if l1.user else "-")
    assert log_result["object_repr"] == l1.object_repr
    assert log_result["content_type"] == l1.content_type.name
    assert log_result["timestamp"] == f"{l1.timestamp:%Y-%m-%dT%H:%M:%SZ}"
