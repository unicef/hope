from datetime import date
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
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    SanctionListIndividualFactory,
    TicketNeedsAdjudicationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Area, BusinessArea, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(
        name="Afghanistan", slug="afghanistan", code="0060", biometric_deduplication_threshold=33.33
    )


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def program_one(business_area: BusinessArea) -> Program:
    return ProgramFactory(name="Test program ONE", business_area=business_area)


@pytest.fixture
def admin_area_1() -> Area:
    afghanistan = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    area_type = AreaTypeFactory(name="Admin type one", country=afghanistan, area_level=2)
    return AreaFactory(name="City Test", area_type=area_type, p_code="sdfghjuytre2")


@pytest.fixture
def individuals(program_one: Program, business_area: BusinessArea) -> list[Any]:
    household = HouseholdFactory(business_area=business_area, program=program_one, create_role=False)
    individuals_to_create = [
        {
            "full_name": "Benjamin Butler",
            "given_name": "Benjamin",
            "family_name": "Butler",
            "phone_no": "(953)682-4596",
            "birth_date": date(1943, 7, 30),
            "unicef_id": "IND-123-123",
        },
        {
            "full_name": "Robin Ford",
            "given_name": "Robin",
            "family_name": "Ford",
            "phone_no": "+18663567905",
            "birth_date": date(1946, 2, 15),
            "unicef_id": "IND-222-222",
        },
    ]
    created_individuals = [
        IndividualFactory(
            household=household,
            business_area=business_area,
            program=program_one,
            registration_data_import=household.registration_data_import,
            **individual_data,
        )
        for individual_data in individuals_to_create
    ]
    household.head_of_household = created_individuals[0]
    household.save(update_fields=["head_of_household"])
    return created_individuals


@pytest.fixture
def grievance_context(
    user: User,
    business_area: BusinessArea,
    program_one: Program,
    admin_area_1: Area,
    individuals: list[Any],
) -> dict[str, Any]:
    sanction_list_individual = SanctionListIndividualFactory()

    system_flagging_grievance_ticket = GrievanceTicketFactory(
        description="system_flagging_grievance_ticket",
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        issue_type=None,
        admin2=admin_area_1,
        business_area=business_area,
        created_by=user,
    )
    system_flagging_grievance_ticket.programs.set([program_one])
    TicketSystemFlaggingDetailsFactory(
        ticket=system_flagging_grievance_ticket,
        golden_records_individual=individuals[0],
        sanction_list_individual=sanction_list_individual,
        approve_status=True,
    )

    needs_adjudication_grievance_ticket = GrievanceTicketFactory(
        description="needs_adjudication_grievance_ticket",
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        admin2=admin_area_1,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        created_by=user,
    )
    needs_adjudication_grievance_ticket.programs.set([program_one])
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=needs_adjudication_grievance_ticket,
        golden_records_individual=individuals[0],
        possible_duplicate=individuals[1],
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(*individuals)

    return {
        "user": user,
        "business_area": business_area,
        "program_one": program_one,
        "individuals": individuals,
        "system_flagging_grievance_ticket": system_flagging_grievance_ticket,
        "needs_adjudication_grievance_ticket": needs_adjudication_grievance_ticket,
    }


def test_approve_system_flagging(
    authenticated_client: Any,
    grievance_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    user = grievance_context["user"]
    business_area = grievance_context["business_area"]
    program_one = grievance_context["program_one"]
    grievance_ticket = grievance_context["system_flagging_grievance_ticket"]
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR],
        business_area,
        program_one,
    )

    response = authenticated_client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-status-update",
            kwargs={
                "business_area_slug": business_area.slug,
                "pk": str(grievance_ticket.id),
            },
        ),
        {
            "approve_status": False,
            "version": grievance_ticket.version,
        },
        format="json",
    )
    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_data
    assert resp_data["ticket_details"]["approve_status"] is False


def test_approve_needs_adjudication(
    authenticated_client: Any,
    grievance_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    user = grievance_context["user"]
    business_area = grievance_context["business_area"]
    program_one = grievance_context["program_one"]
    individuals = grievance_context["individuals"]
    grievance_ticket = grievance_context["needs_adjudication_grievance_ticket"]
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        program_one,
    )

    response = authenticated_client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
            kwargs={
                "business_area_slug": business_area.slug,
                "pk": str(grievance_ticket.id),
            },
        ),
        {
            "selected_individual_id": str(individuals[1].id),
            "version": grievance_ticket.version,
        },
        format="json",
    )
    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_data
    assert resp_data["ticket_details"]["selected_individual"]["unicef_id"] == individuals[1].unicef_id


def test_approve_needs_adjudication_should_allow_uncheck_selected_individual(
    authenticated_client: Any,
    grievance_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    user = grievance_context["user"]
    business_area = grievance_context["business_area"]
    program_one = grievance_context["program_one"]
    grievance_ticket = grievance_context["needs_adjudication_grievance_ticket"]
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        program_one,
    )

    response = authenticated_client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
            kwargs={
                "business_area_slug": business_area.slug,
                "pk": str(grievance_ticket.id),
            },
        ),
        {
            "selected_individual_id": None,
            "version": grievance_ticket.version,
        },
        format="json",
    )
    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_data
    assert resp_data["ticket_details"]["selected_individual"] is None


def test_approve_needs_adjudication_allows_multiple_selected_individuals_without_permission(
    authenticated_client: Any,
    grievance_context: dict[str, Any],
) -> None:
    business_area = grievance_context["business_area"]
    individuals = grievance_context["individuals"]
    grievance_ticket = grievance_context["needs_adjudication_grievance_ticket"]
    response = authenticated_client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
            kwargs={
                "business_area_slug": business_area.slug,
                "pk": str(grievance_ticket.id),
            },
        ),
        {
            "duplicate_individual_ids": [str(individuals[0].id), str(individuals[1].id)],
            "version": grievance_ticket.version,
        },
        format="json",
    )
    resp_data = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert resp_data["detail"] == "You do not have permission to perform this action."


def test_approve_needs_adjudication_allows_multiple_selected_individuals_with_permission(
    authenticated_client: Any,
    grievance_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    user = grievance_context["user"]
    business_area = grievance_context["business_area"]
    program_one = grievance_context["program_one"]
    individuals = grievance_context["individuals"]
    grievance_ticket = grievance_context["needs_adjudication_grievance_ticket"]
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        program_one,
    )

    response = authenticated_client.post(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
            kwargs={
                "business_area_slug": business_area.slug,
                "pk": str(grievance_ticket.id),
            },
        ),
        {
            "duplicate_individual_ids": [str(individuals[0].id), str(individuals[1].id)],
            "version": grievance_ticket.version,
        },
        format="json",
    )
    resp_data = response.json()
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert len(resp_data["ticket_details"]["possible_duplicates"]) == 2
    selected_individuals_ids = [item["id"] for item in resp_data["ticket_details"]["possible_duplicates"]]
    assert str(individuals[0].id) in selected_individuals_ids
    assert str(individuals[1].id) in selected_individuals_ids


def test_approve_needs_adjudication_new_input_fields(
    authenticated_client: Any,
    grievance_context: dict[str, Any],
    create_user_role_with_permissions: Callable,
) -> None:
    user = grievance_context["user"]
    business_area = grievance_context["business_area"]
    program_one = grievance_context["program_one"]
    individuals = grievance_context["individuals"]
    grievance_ticket = grievance_context["needs_adjudication_grievance_ticket"]
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        program_one,
    )

    url = reverse(
        "api:grievance-tickets:grievance-tickets-global-approve-needs-adjudication",
        kwargs={
            "business_area_slug": business_area.slug,
            "pk": str(grievance_ticket.id),
        },
    )

    grievance_ticket.refresh_from_db()
    assert grievance_ticket.ticket_details.selected_distinct.count() == 0
    assert grievance_ticket.ticket_details.selected_individuals.count() == 0

    resp_1 = authenticated_client.post(
        url,
        {
            "duplicate_individual_ids": [str(individuals[1].id)],
            "distinct_individual_ids": [str(individuals[0].id)],
            "version": grievance_ticket.version,
        },
        format="json",
    )
    assert resp_1.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only one option for duplicate or distinct or clear individuals is available" in resp_1.json()

    grievance_ticket.status = GrievanceTicket.STATUS_ASSIGNED
    grievance_ticket.save(update_fields=["status"])
    resp_2 = authenticated_client.post(
        url,
        {
            "duplicate_individual_ids": [str(individuals[1].id)],
            "version": grievance_ticket.version,
        },
        format="json",
    )
    assert resp_2.status_code == status.HTTP_400_BAD_REQUEST
    assert "A user can not flag individuals when a ticket is not in the 'For Approval' status" in resp_2.json()

    grievance_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
    grievance_ticket.save(update_fields=["status"])
    resp_3 = authenticated_client.post(
        url,
        {
            "duplicate_individual_ids": [str(individuals[1].id)],
            "version": grievance_ticket.version,
        },
        format="json",
    )
    assert resp_3.status_code == status.HTTP_202_ACCEPTED
    resp_data = resp_3.json()
    assert "id" in resp_data
    assert resp_data["ticket_details"]["selected_duplicates"][0]["unicef_id"] == individuals[1].unicef_id

    resp_4 = authenticated_client.post(
        url,
        {
            "distinct_individual_ids": [str(individuals[0].id)],
            "version": grievance_ticket.version,
        },
        format="json",
    )
    assert resp_4.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_4.json()

    grievance_ticket.refresh_from_db()
    assert grievance_ticket.ticket_details.selected_distinct.count() == 1
    assert grievance_ticket.ticket_details.selected_individuals.count() == 1

    resp_5 = authenticated_client.post(
        url,
        {
            "clear_individual_ids": [str(individuals[0].id)],
            "version": grievance_ticket.version,
        },
        format="json",
    )
    assert resp_5.status_code == status.HTTP_202_ACCEPTED
    assert "id" in resp_5.json()

    grievance_ticket.refresh_from_db()
    assert grievance_ticket.ticket_details.selected_distinct.count() == 0
    assert grievance_ticket.ticket_details.selected_individuals.count() == 1
