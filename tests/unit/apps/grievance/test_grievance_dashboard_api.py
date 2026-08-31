from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    GrievanceTicketFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.sql import joined_tables, statements_from
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def dashboard_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")
    user = UserFactory(first_name="Test", last_name="User")
    country = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    area_type = AreaTypeFactory(
        name="Admin type one",
        area_level=2,
        country=country,
    )
    admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="123aa123")
    program = ProgramFactory(name="Test Program", business_area=business_area)

    ticket_new = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        assigned_to=user,
        business_area=business_area,
        admin2=admin_area,
        consent=True,
        language="Polish, English",
        description="Just random description",
    )
    ticket_on_hold = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_ON_HOLD,
        created_by=user,
        assigned_to=user,
        business_area=business_area,
        admin2=admin_area,
        consent=True,
        language="Polish, English",
        description="Just random description",
    )
    ticket_in_progress = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_IN_PROGRESS,
        created_by=user,
        assigned_to=user,
        business_area=business_area,
        admin2=admin_area,
        consent=True,
        language="Polish, English",
        description="Just random description",
    )
    ticket_closed_user = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_CLOSED,
        created_by=user,
        assigned_to=user,
        business_area=business_area,
        admin2=admin_area,
        consent=True,
        language="Polish, English",
        description="Just random description",
    )
    ticket_closed_system_1 = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        status=GrievanceTicket.STATUS_CLOSED,
        created_by=user,
        assigned_to=user,
        business_area=business_area,
        admin2=admin_area,
        consent=True,
        language="Polish, English",
        description="Just random description",
    )
    ticket_closed_system_2 = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        status=GrievanceTicket.STATUS_CLOSED,
        created_by=user,
        assigned_to=user,
        business_area=business_area,
        admin2=admin_area,
        consent=True,
        language="Polish, English",
        description="Just random description",
    )

    GrievanceTicket.objects.filter(id=ticket_new.id).update(
        created_at=datetime(year=2020, month=3, day=12, tzinfo=timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    GrievanceTicket.objects.filter(id=ticket_on_hold.id).update(
        created_at=datetime(year=2020, month=7, day=12, tzinfo=timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    GrievanceTicket.objects.filter(id=ticket_in_progress.id).update(
        created_at=datetime(year=2020, month=8, day=22, tzinfo=timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    for ticket in [ticket_new, ticket_on_hold, ticket_in_progress]:
        ticket.programs.add(program)

    return {
        "user": user,
        "business_area": business_area,
        "program": program,
        "global_url": reverse(
            "api:grievance:grievance-tickets-global-dashboard",
            kwargs={"business_area_slug": business_area.slug},
        ),
        "program_url": reverse(
            "api:grievance:grievance-tickets-dashboard",
            kwargs={"business_area_slug": business_area.slug, "program_code": program.code},
        ),
        "tickets": [
            ticket_new,
            ticket_on_hold,
            ticket_in_progress,
            ticket_closed_user,
            ticket_closed_system_1,
            ticket_closed_system_2,
        ],
    }


@pytest.fixture
def authenticated_client(api_client: Callable, dashboard_context: dict[str, Any]) -> Any:
    return api_client(dashboard_context["user"])


@pytest.fixture
def finished_program(dashboard_context: dict[str, Any]) -> Any:
    return ProgramFactory(
        name="Finished Program",
        business_area=dashboard_context["business_area"],
        status=Program.FINISHED,
    )


@pytest.fixture
def finished_program_ticket(dashboard_context: dict[str, Any], finished_program: Any) -> Any:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        business_area=dashboard_context["business_area"],
    )
    ticket.programs.add(finished_program)
    return ticket


def test_global_dashboard_api_endpoint_with_permission(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )
    response = authenticated_client.get(dashboard_context["global_url"])
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "tickets_by_type" in data
    assert "tickets_by_status" in data
    assert "tickets_by_category" in data
    assert "tickets_by_location_and_category" in data

    tickets_by_type = data["tickets_by_type"]
    assert "user_generated_count" in tickets_by_type
    assert "system_generated_count" in tickets_by_type
    assert "closed_user_generated_count" in tickets_by_type
    assert "closed_system_generated_count" in tickets_by_type
    assert "user_generated_avg_resolution" in tickets_by_type
    assert "system_generated_avg_resolution" in tickets_by_type

    for chart_key in ["tickets_by_status", "tickets_by_category"]:
        chart_data = data[chart_key]
        assert "labels" in chart_data
        assert "datasets" in chart_data
        assert isinstance(chart_data["labels"], list)
        assert isinstance(chart_data["datasets"], list)

    detailed_chart = data["tickets_by_location_and_category"]
    assert "labels" in detailed_chart
    assert "datasets" in detailed_chart
    assert isinstance(detailed_chart["labels"], list)
    assert isinstance(detailed_chart["datasets"], list)


def test_global_dashboard_api_endpoint_without_permission(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )
    response = authenticated_client.get(dashboard_context["global_url"])
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_dashboard_data_accuracy(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    tickets_by_type = data["tickets_by_type"]
    assert tickets_by_type["user_generated_count"] == 4
    assert tickets_by_type["system_generated_count"] == 2
    assert tickets_by_type["closed_user_generated_count"] == 1
    assert tickets_by_type["closed_system_generated_count"] == 2


def test_program_dashboard_api_endpoint_with_permission(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        dashboard_context["program"],
    )
    response = authenticated_client.get(dashboard_context["program_url"])
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "tickets_by_type" in data
    assert "tickets_by_status" in data
    assert "tickets_by_category" in data
    assert "tickets_by_location_and_category" in data

    tickets_by_type = data["tickets_by_type"]
    assert "user_generated_count" in tickets_by_type
    assert "system_generated_count" in tickets_by_type
    assert "closed_user_generated_count" in tickets_by_type
    assert "closed_system_generated_count" in tickets_by_type
    assert "user_generated_avg_resolution" in tickets_by_type
    assert "system_generated_avg_resolution" in tickets_by_type


def test_program_dashboard_api_endpoint_without_permission(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [],
        dashboard_context["business_area"],
        dashboard_context["program"],
    )
    response = authenticated_client.get(dashboard_context["program_url"])
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_program_dashboard_filters_by_program(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        dashboard_context["program"],
    )

    response = authenticated_client.get(dashboard_context["program_url"])
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    tickets_by_type = data["tickets_by_type"]
    assert tickets_by_type["user_generated_count"] == 3
    assert tickets_by_type["system_generated_count"] == 0


def test_global_dashboard_excludes_finished_program_tickets(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    finished_program: Any,
    finished_program_ticket: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    global_response = authenticated_client.get(dashboard_context["global_url"])
    assert global_response.status_code == status.HTTP_200_OK
    assert global_response.json()["tickets_by_type"]["user_generated_count"] == 4

    finished_program_url = reverse(
        "api:grievance:grievance-tickets-dashboard",
        kwargs={
            "business_area_slug": dashboard_context["business_area"].slug,
            "program_code": finished_program.code,
        },
    )
    program_response = authenticated_client.get(finished_program_url)
    assert program_response.status_code == status.HTTP_200_OK
    assert program_response.json()["tickets_by_type"]["user_generated_count"] == 1


@pytest.fixture
def ticket_without_program(dashboard_context: dict[str, Any]) -> Any:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
        business_area=dashboard_context["business_area"],
    )


@pytest.fixture
def ticket_on_active_and_finished_programs(dashboard_context: dict[str, Any], finished_program: Any) -> Any:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
        business_area=dashboard_context["business_area"],
    )
    ticket.programs.add(dashboard_context["program"], finished_program)
    return ticket


def test_global_dashboard_counts_ticket_with_no_program(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    ticket_without_program: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["tickets_by_type"]["user_generated_count"] == 5


def test_global_dashboard_counts_ticket_once_when_on_active_and_finished_programs(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    ticket_on_active_and_finished_programs: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["tickets_by_type"]["user_generated_count"] == 5


def test_global_dashboard_queryset_joins_neither_business_area_nor_programs(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    with CaptureQueriesContext(connection) as captured:
        response = authenticated_client.get(dashboard_context["global_url"])
    assert response.status_code == status.HTTP_200_OK

    view = response.renderer_context["view"]
    assert joined_tables(view.get_dashboard_base_queryset()) == {"grievance_grievanceticket"}

    aggregates = statements_from(captured, "grievance_grievanceticket")
    assert len(aggregates) == 1
    for statement in aggregates:
        assert "core_businessarea" not in statement
        assert '"grievance_grievanceticket"."id" IN (SELECT' not in statement


def test_program_dashboard_queryset_joins_neither_business_area_nor_programs(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        dashboard_context["program"],
    )

    with CaptureQueriesContext(connection) as captured:
        response = authenticated_client.get(dashboard_context["program_url"])
    assert response.status_code == status.HTTP_200_OK

    view = response.renderer_context["view"]
    assert joined_tables(view.get_dashboard_base_queryset(view.program)) == {"grievance_grievanceticket"}

    aggregates = statements_from(captured, "grievance_grievanceticket")
    assert len(aggregates) == 1
    for statement in aggregates:
        assert "core_businessarea" not in statement
        assert "program_program" not in statement


def test_global_dashboard_issues_expected_number_of_queries(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
    django_assert_num_queries: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    with django_assert_num_queries(10):
        response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK


def test_program_dashboard_issues_expected_number_of_queries(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
    django_assert_num_queries: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        dashboard_context["program"],
    )

    with django_assert_num_queries(14):
        response = authenticated_client.get(dashboard_context["program_url"])

    assert response.status_code == status.HTTP_200_OK


@pytest.fixture
def closed_tickets_with_resolution_spans(dashboard_context: dict[str, Any]) -> None:
    opened = datetime(year=2021, month=1, day=1, tzinfo=timezone.utc)
    closed_user, closed_system_1, closed_system_2 = dashboard_context["tickets"][3:6]
    GrievanceTicket.objects.filter(id=closed_user.id).update(
        created_at=opened, updated_at=opened + timedelta(days=3, hours=13)
    )
    GrievanceTicket.objects.filter(id=closed_system_1.id).update(
        created_at=opened, updated_at=opened + timedelta(days=4)
    )
    GrievanceTicket.objects.filter(id=closed_system_2.id).update(
        created_at=opened, updated_at=opened + timedelta(days=7)
    )


@pytest.fixture
def second_area_sharing_a_name(dashboard_context: dict[str, Any]) -> Any:
    admin_area = dashboard_context["tickets"][0].admin2
    duplicate = AreaFactory(name=admin_area.name, area_type=admin_area.area_type, p_code="456bb456")
    GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
        business_area=dashboard_context["business_area"],
        admin2=duplicate,
    )
    return duplicate


@pytest.fixture
def ticket_without_admin_area(dashboard_context: dict[str, Any]) -> Any:
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
        business_area=dashboard_context["business_area"],
        admin2=None,
    )


@pytest.fixture
def two_referral_tickets(dashboard_context: dict[str, Any]) -> None:
    GrievanceTicketFactory.create_batch(
        2,
        category=GrievanceTicket.CATEGORY_REFERRAL,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
        business_area=dashboard_context["business_area"],
        admin2=dashboard_context["tickets"][0].admin2,
    )


def test_global_dashboard_runs_one_grouped_pass_over_the_tickets(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    with CaptureQueriesContext(connection) as captured:
        response = authenticated_client.get(dashboard_context["global_url"])
    assert response.status_code == status.HTTP_200_OK

    aggregates = statements_from(captured, "grievance_grievanceticket")
    assert len(aggregates) == 1
    assert "GROUP BY" in aggregates[0]
    assert "geo_area" not in aggregates[0]


def test_global_dashboard_averages_resolution_over_closed_tickets_only(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    closed_tickets_with_resolution_spans: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    tickets_by_type = response.json()["tickets_by_type"]
    assert tickets_by_type["user_generated_avg_resolution"] == 3.0
    assert tickets_by_type["system_generated_avg_resolution"] == 5.5


def test_global_dashboard_reports_zero_average_resolution_when_nothing_is_closed(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )
    GrievanceTicket.objects.filter(status=GrievanceTicket.STATUS_CLOSED).update(
        status=GrievanceTicket.STATUS_IN_PROGRESS
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    tickets_by_type = response.json()["tickets_by_type"]
    assert tickets_by_type["user_generated_avg_resolution"] == 0.0
    assert tickets_by_type["system_generated_avg_resolution"] == 0.0


def test_global_dashboard_counts_tickets_per_status(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["tickets_by_status"] == {
        "labels": ["Closed", "In Progress", "New", "On Hold"],
        "datasets": [{"data": [3, 1, 1, 1]}],
    }


def test_global_dashboard_orders_categories_by_count_then_label(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    two_referral_tickets: None,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    # "Needs Adjudication" and "Referral" both have 2, so the label decides
    assert response.json()["tickets_by_category"] == {
        "labels": ["Positive Feedback", "Needs Adjudication", "Referral", "Negative Feedback"],
        "datasets": [{"data": [3, 2, 2, 1]}],
    }


def test_global_dashboard_counts_tickets_per_area_and_category(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["tickets_by_location_and_category"] == {
        "labels": ["City Test"],
        "datasets": [
            {"label": "Data Change", "data": [0]},
            {"label": "Grievance Complaint", "data": [0]},
            {"label": "Needs Adjudication", "data": [2]},
            {"label": "Negative Feedback", "data": [1]},
            {"label": "Payment Verification", "data": [0]},
            {"label": "Positive Feedback", "data": [3]},
            {"label": "Referral", "data": [0]},
            {"label": "Sensitive Grievance", "data": [0]},
            {"label": "System Flagging", "data": [0]},
        ],
    }


def test_global_dashboard_merges_areas_sharing_a_name_into_one_location_label(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    second_area_sharing_a_name: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    chart = response.json()["tickets_by_location_and_category"]
    assert chart["labels"] == ["City Test"]
    assert {"label": "Positive Feedback", "data": [4]} in chart["datasets"]


def test_global_dashboard_omits_tickets_without_an_admin_area_from_the_location_chart(
    authenticated_client: Any,
    dashboard_context: dict[str, Any],
    ticket_without_admin_area: Any,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        dashboard_context["user"],
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        dashboard_context["business_area"],
        whole_business_area_access=True,
    )

    response = authenticated_client.get(dashboard_context["global_url"])

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    chart = data["tickets_by_location_and_category"]
    assert chart["labels"] == ["City Test"]
    assert {"label": "Referral", "data": [0]} in chart["datasets"]
    # the ticket is still counted everywhere the area is not the key
    assert data["tickets_by_type"]["user_generated_count"] == 5
