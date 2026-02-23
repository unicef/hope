from datetime import datetime, timezone
from typing import Any, Callable

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
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket

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
            kwargs={"business_area_slug": business_area.slug, "program_slug": program.slug},
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
