"""Tests for the bulk Needs Adjudication resolve+auto-close API action."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    TicketComplaintDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY, UNIQUE
from hope.models import BusinessArea, IndividualRoleInHousehold, User

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
def na_ticket_head_with_member(business_area: BusinessArea, program: Any, user: User) -> TicketNeedsAdjudicationDetails:
    # golden is head of a household with a second active member, so withdrawing it needs a head handover
    golden_household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    golden = golden_household.head_of_household
    IndividualFactory(household=golden_household, program=program, business_area=business_area)
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
def na_ticket_primary_collector(
    business_area: BusinessArea, program: Any, user: User
) -> TicketNeedsAdjudicationDetails:
    # golden is a primary collector in a surviving household, so withdrawing it needs a handover
    golden_household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    golden = IndividualFactory(household=golden_household, program=program, business_area=business_area)
    IndividualRoleInHouseholdFactory(individual=golden, household=golden_household, role=ROLE_PRIMARY)
    IndividualFactory(household=golden_household, program=program, business_area=business_area)
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
def na_ticket_alternate_collector(
    business_area: BusinessArea, program: Any, user: User
) -> TicketNeedsAdjudicationDetails:
    # golden is only an alternate collector; the household keeps its head and primary, so no handover is needed
    golden_household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    primary = IndividualFactory(household=golden_household, program=program, business_area=business_area)
    IndividualRoleInHouseholdFactory(individual=primary, household=golden_household, role=ROLE_PRIMARY)
    golden = IndividualFactory(household=golden_household, program=program, business_area=business_area)
    IndividualRoleInHouseholdFactory(individual=golden, household=golden_household, role=ROLE_ALTERNATE)
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
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
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
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
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


def test_bulk_needs_adjudication_forbidden_with_view_only_permission(
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
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
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
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
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
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
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
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
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
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
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
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
        business_area,
        whole_business_area_access=True,
    )

    client = api_client(user)
    response = client.post(bulk_na_url, {"tickets": []}, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_bulk_needs_adjudication_reassigns_head_and_closes(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_head_with_member: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_head_with_member.golden_records_individual
    duplicate = na_ticket_head_with_member.possible_duplicates.first()
    golden_household = golden.household
    member = golden_household.individuals.exclude(id=golden.id).first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_head_with_member.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                    "role_reassign_data": {
                        "HEAD": {
                            "role": "HEAD",
                            "household": str(golden_household.id),
                            "individual": str(golden.id),
                            "new_individual": str(member.id),
                        }
                    },
                }
            ]
        },
        format="json",
    )

    na_ticket_head_with_member.ticket.refresh_from_db()
    golden_household.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket_head_with_member.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert golden_household.head_of_household_id == member.id


def test_bulk_needs_adjudication_rejects_head_withdrawal_without_reassignment(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_head_with_member: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_head_with_member.golden_records_individual
    duplicate = na_ticket_head_with_member.possible_duplicates.first()
    golden_household = golden.household

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_head_with_member.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket_head_with_member.ticket.refresh_from_db()
    golden_household.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket_head_with_member.ticket.status == GrievanceTicket.STATUS_NEW
    assert golden_household.head_of_household_id == golden.id


def test_bulk_needs_adjudication_reassigns_primary_collector_and_closes(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_primary_collector: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_primary_collector.golden_records_individual
    duplicate = na_ticket_primary_collector.possible_duplicates.first()
    golden_household = golden.household
    replacement = golden_household.individuals.exclude(id=golden.id).first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_primary_collector.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                    "role_reassign_data": {
                        "PRIMARY": {
                            "role": ROLE_PRIMARY,
                            "household": str(golden_household.id),
                            "individual": str(golden.id),
                            "new_individual": str(replacement.id),
                        }
                    },
                }
            ]
        },
        format="json",
    )

    na_ticket_primary_collector.ticket.refresh_from_db()
    primary_role = IndividualRoleInHousehold.objects.get(household=golden_household, role=ROLE_PRIMARY)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket_primary_collector.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert primary_role.individual_id == replacement.id


def test_bulk_needs_adjudication_rejects_primary_collector_withdrawal_without_reassignment(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_primary_collector: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_primary_collector.golden_records_individual
    duplicate = na_ticket_primary_collector.possible_duplicates.first()
    golden_household = golden.household

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_primary_collector.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket_primary_collector.ticket.refresh_from_db()
    primary_role = IndividualRoleInHousehold.objects.get(household=golden_household, role=ROLE_PRIMARY)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket_primary_collector.ticket.status == GrievanceTicket.STATUS_NEW
    assert primary_role.individual_id == golden.id


def test_bulk_needs_adjudication_closes_alternate_collector_without_reassignment(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_alternate_collector: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_alternate_collector.golden_records_individual
    duplicate = na_ticket_alternate_collector.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_alternate_collector.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket_alternate_collector.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket_alternate_collector.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert IndividualRoleInHousehold.objects.filter(household=golden.household, role=ROLE_PRIMARY).exists()


def test_bulk_needs_adjudication_forbidden_without_manage_permission(
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

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_forbidden_when_manage_granted_in_another_program(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    other_program = ProgramFactory(business_area=business_area, name="program without the ticket")
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE],
        business_area,
        program=other_program,
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
