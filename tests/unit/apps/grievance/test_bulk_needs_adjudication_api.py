"""Tests for the bulk Needs Adjudication resolve+auto-close API action."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    TicketComplaintDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.household.const import UNIQUE
from hope.models import BusinessArea, User

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def program(business_area: BusinessArea) -> Any:
    return ProgramFactory(business_area=business_area, name="program afghanistan 1")


@pytest.fixture
def user() -> User:
    return UserFactory(partner=PartnerFactory(name="TestPartner"))


@pytest.fixture
def na_ticket(business_area: BusinessArea, program: Any, user: User) -> TicketNeedsAdjudicationDetails:
    golden = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    duplicate = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        created_by=user,
        status=GrievanceTicket.STATUS_NEW,
    )
    grievance.programs.set([program])
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(duplicate)
    return ticket_details


@pytest.fixture
def na_ticket_owned_by_user(business_area: BusinessArea, program: Any, user: User) -> TicketNeedsAdjudicationDetails:
    golden = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    duplicate = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        created_by=UserFactory(first_name="other"),
        assigned_to=user,
        status=GrievanceTicket.STATUS_NEW,
    )
    grievance.programs.set([program])
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=golden,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(duplicate)
    return ticket_details


@pytest.fixture
def bulk_na_url(business_area: BusinessArea) -> str:
    return reverse(
        "api:grievance:grievance-tickets-global-bulk-needs-adjudication",
        kwargs={"business_area_slug": business_area.slug},
    )


def test_bulk_needs_adjudication_marks_person_duplicate_and_closes(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket.golden_records_individual
    duplicate = na_ticket.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()
    golden.refresh_from_db()
    duplicate.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert golden.duplicate is True
    assert duplicate.deduplication_golden_record_status == UNIQUE


def test_bulk_needs_adjudication_not_duplicates_marks_both_distinct_and_closes(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket.golden_records_individual
    duplicate = na_ticket.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [],
                    "distinct_individual_ids": [str(golden.id), str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()
    golden.refresh_from_db()
    duplicate.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert golden.duplicate is False
    assert golden.deduplication_golden_record_status == UNIQUE
    assert duplicate.deduplication_golden_record_status == UNIQUE


def test_bulk_needs_adjudication_forbidden_without_approve_permission(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket.golden_records_individual
    duplicate = na_ticket.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_all_or_nothing_when_one_ticket_closed(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        whole_business_area_access=True,
    )
    closed_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_CLOSED,
    )
    golden = na_ticket.golden_records_individual
    duplicate = na_ticket.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                },
                {
                    "ticket_id": str(closed_ticket.id),
                    "duplicate_individual_ids": [],
                    "distinct_individual_ids": [str(duplicate.id)],
                },
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_rejects_individual_not_on_ticket(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Any,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        whole_business_area_access=True,
    )
    unrelated = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(unrelated.id)],
                    "distinct_individual_ids": [str(na_ticket.golden_records_individual.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_rejects_non_na_ticket(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        whole_business_area_access=True,
    )
    complaint = TicketComplaintDetailsFactory(
        ticket__business_area=business_area,
        ticket__status=GrievanceTicket.STATUS_FOR_APPROVAL,
    ).ticket

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(complaint.id),
                    "duplicate_individual_ids": [],
                    "distinct_individual_ids": [str(complaint.id)],
                }
            ]
        },
        format="json",
    )

    complaint.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert complaint.status == GrievanceTicket.STATUS_FOR_APPROVAL


def test_bulk_needs_adjudication_allowed_as_creator(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket.golden_records_individual
    duplicate = na_ticket.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_CLOSED


def test_bulk_needs_adjudication_forbidden_as_creator_when_not_creator(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_owned_by_user: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_owned_by_user.golden_records_individual
    duplicate = na_ticket_owned_by_user.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_owned_by_user.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket_owned_by_user.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert na_ticket_owned_by_user.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_allowed_as_owner(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_owned_by_user: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_owned_by_user.golden_records_individual
    duplicate = na_ticket_owned_by_user.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_owned_by_user.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket_owned_by_user.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket_owned_by_user.ticket.status == GrievanceTicket.STATUS_CLOSED


def test_bulk_needs_adjudication_forbidden_as_owner_when_not_owner(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket.golden_records_individual
    duplicate = na_ticket.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_rejects_empty_marks(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        whole_business_area_access=True,
    )

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [],
                    "distinct_individual_ids": [],
                }
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_rejects_overlapping_duplicate_and_distinct(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket.golden_records_individual

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(golden.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_rejects_empty_tickets_list(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE],
        business_area,
        whole_business_area_access=True,
    )

    client = api_client(user)
    response = client.post(bulk_na_url, {"tickets": []}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
