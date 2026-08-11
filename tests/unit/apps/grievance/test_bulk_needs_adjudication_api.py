"""Tests for the bulk Needs Adjudication resolve+auto-close API action."""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AdminAreaLimitedToFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
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
def make_na_ticket(user: User) -> Callable:
    """Wire individuals into a Needs Adjudication ticket, in the programme they belong to."""

    def _make(
        golden: Any,
        *duplicates: Any,
        possible_duplicate: Any = None,
        is_multiple_duplicates_version: bool = True,
    ) -> TicketNeedsAdjudicationDetails:
        grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
            business_area=golden.business_area,
            created_by=user,
            status=GrievanceTicket.STATUS_NEW,
        )
        grievance.programs.set([golden.program])
        ticket_details = TicketNeedsAdjudicationDetailsFactory(
            ticket=grievance,
            golden_records_individual=golden,
            possible_duplicate=possible_duplicate,
            is_multiple_duplicates_version=is_multiple_duplicates_version,
            selected_individual=None,
        )
        if duplicates:
            ticket_details.possible_duplicates.add(*duplicates)
        return ticket_details

    return _make


@pytest.fixture
def na_ticket(business_area: BusinessArea, program: Any, make_na_ticket: Callable) -> TicketNeedsAdjudicationDetails:
    golden = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    duplicate = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    return make_na_ticket(golden, duplicate)


@pytest.fixture
def another_na_ticket(
    business_area: BusinessArea, program: Any, make_na_ticket: Callable
) -> TicketNeedsAdjudicationDetails:
    golden = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    duplicate = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    return make_na_ticket(golden, duplicate)


@pytest.fixture
def na_ticket_head_with_member(
    business_area: BusinessArea, program: Any, make_na_ticket: Callable
) -> TicketNeedsAdjudicationDetails:
    # golden heads a household with a second active member, so withdrawing it needs a handover
    golden_household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    IndividualFactory(household=golden_household, program=program, business_area=business_area)
    duplicate = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    return make_na_ticket(golden_household.head_of_household, duplicate)


@pytest.fixture
def na_ticket_primary_collector(
    business_area: BusinessArea, program: Any, make_na_ticket: Callable
) -> TicketNeedsAdjudicationDetails:
    # golden is a primary collector in a surviving household, so withdrawing it needs a handover
    golden_household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    golden = IndividualFactory(household=golden_household, program=program, business_area=business_area)
    IndividualRoleInHouseholdFactory(individual=golden, household=golden_household, role=ROLE_PRIMARY)
    IndividualFactory(household=golden_household, program=program, business_area=business_area)
    duplicate = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    return make_na_ticket(golden, duplicate)


@pytest.fixture
def na_ticket_alternate_collector(
    business_area: BusinessArea, program: Any, make_na_ticket: Callable
) -> TicketNeedsAdjudicationDetails:
    # golden is only an alternate collector; the household keeps its head and primary
    golden_household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    primary = IndividualFactory(household=golden_household, program=program, business_area=business_area)
    IndividualRoleInHouseholdFactory(individual=primary, household=golden_household, role=ROLE_PRIMARY)
    golden = IndividualFactory(household=golden_household, program=program, business_area=business_area)
    IndividualRoleInHouseholdFactory(individual=golden, household=golden_household, role=ROLE_ALTERNATE)
    duplicate = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    return make_na_ticket(golden, duplicate)


@pytest.fixture
def na_ticket_in_admin_area(
    business_area: BusinessArea, program: Any, make_na_ticket: Callable
) -> TicketNeedsAdjudicationDetails:
    area = AreaFactory(name="Area with the ticket", area_type=AreaTypeFactory(country=CountryFactory()))
    golden = HouseholdFactory(
        program=program, business_area=business_area, admin2=area, create_role=False
    ).head_of_household
    duplicate = HouseholdFactory(
        program=program, business_area=business_area, admin2=area, create_role=False
    ).head_of_household
    return make_na_ticket(golden, duplicate)


@pytest.fixture
def na_ticket_with_withdrawn_duplicate(
    business_area: BusinessArea, program: Any, make_na_ticket: Callable
) -> TicketNeedsAdjudicationDetails:
    golden = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    duplicate = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    duplicate.withdrawn = True
    duplicate.save()
    return make_na_ticket(golden, duplicate)


@pytest.fixture
def na_ticket_in_other_business_area(make_na_ticket: Callable) -> TicketNeedsAdjudicationDetails:
    other_business_area = BusinessAreaFactory(name="Ukraine", slug="ukraine", code="4410")
    other_program = ProgramFactory(business_area=other_business_area, name="program ukraine 1")
    golden = HouseholdFactory(
        program=other_program, business_area=other_business_area, create_role=False
    ).head_of_household
    duplicate = HouseholdFactory(
        program=other_program, business_area=other_business_area, create_role=False
    ).head_of_household
    return make_na_ticket(golden, duplicate)


@pytest.fixture
def na_ticket_two_duplicates_sharing_a_household(
    business_area: BusinessArea, program: Any, make_na_ticket: Callable
) -> TicketNeedsAdjudicationDetails:
    # both duplicates live in the household one of them collects for
    household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    collector = IndividualFactory(household=household, program=program, business_area=business_area)
    IndividualRoleInHouseholdFactory(individual=collector, household=household, role=ROLE_PRIMARY)
    second_duplicate = IndividualFactory(household=household, program=program, business_area=business_area)
    golden = HouseholdFactory(program=program, business_area=business_area, create_role=False).head_of_household
    return make_na_ticket(golden, collector, second_duplicate)


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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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


def test_bulk_needs_adjudication_skips_a_ticket_closed_by_someone_else(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        business_area,
        whole_business_area_access=True,
    )
    closed_ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_CLOSED,
    )
    closed_ticket.refresh_from_db()
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

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert [ticket["id"] for ticket in response.data["resolved"]] == [str(na_ticket.ticket.id)]
    assert [ticket["unicef_id"] for ticket in response.data["skipped_closed"]] == [closed_ticket.unicef_id]


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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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


def test_bulk_needs_adjudication_forbidden_without_close_permission(
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
        [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK],
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


def test_bulk_needs_adjudication_forbidden_when_granted_in_another_program(
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
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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


def test_bulk_needs_adjudication_multipart_request_reassigns_head_and_closes(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_head_with_member: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_head_with_member.golden_records_individual
    duplicate = na_ticket_head_with_member.possible_duplicates.first()
    golden_household = golden.household
    member = golden_household.individuals.exclude(id=golden.id).first()
    reassign_key = f"head-{golden_household.id}"

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets[0].ticket_id": str(na_ticket_head_with_member.ticket.id),
            "tickets[0].duplicate_individual_ids[0]": str(golden.id),
            "tickets[0].distinct_individual_ids[0]": str(duplicate.id),
            f"tickets[0].role_reassign_data.{reassign_key}.role": "HEAD",
            f"tickets[0].role_reassign_data.{reassign_key}.household": str(golden_household.id),
            f"tickets[0].role_reassign_data.{reassign_key}.individual": str(golden.id),
            f"tickets[0].role_reassign_data.{reassign_key}.new_individual": str(member.id),
        },
        format="multipart",
    )

    na_ticket_head_with_member.ticket.refresh_from_db()
    golden_household.refresh_from_db()
    golden.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket_head_with_member.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert golden.duplicate is True
    assert golden_household.head_of_household_id == member.id


def test_bulk_needs_adjudication_rejects_the_same_ticket_twice_in_one_request(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
                },
                {
                    "ticket_id": str(na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(duplicate.id)],
                    "distinct_individual_ids": [str(golden.id)],
                },
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_forbidden_for_an_individual_outside_the_partner_areas(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    program: Any,
    na_ticket_in_admin_area: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        business_area,
        program=program,
    )
    other_area = AreaFactory(name="Area the partner is limited to", area_type=AreaTypeFactory(country=CountryFactory()))
    AdminAreaLimitedToFactory(partner=user.partner, program=program, areas=[other_area])
    golden = na_ticket_in_admin_area.golden_records_individual
    duplicate = na_ticket_in_admin_area.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_in_admin_area.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket_in_admin_area.ticket.refresh_from_db()
    golden.refresh_from_db()

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert na_ticket_in_admin_area.ticket.status == GrievanceTicket.STATUS_NEW
    assert golden.duplicate is False


def test_bulk_needs_adjudication_rejects_marking_a_withdrawn_individual(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_with_withdrawn_duplicate: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_with_withdrawn_duplicate.golden_records_individual
    withdrawn = na_ticket_with_withdrawn_duplicate.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_with_withdrawn_duplicate.ticket.id),
                    "duplicate_individual_ids": [str(withdrawn.id)],
                    "distinct_individual_ids": [str(golden.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket_with_withdrawn_duplicate.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket_with_withdrawn_duplicate.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_response_carries_ids_only(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
    assert response.data == {
        "resolved": [{"id": str(na_ticket.ticket.id), "unicef_id": na_ticket.ticket.unicef_id}],
        "skipped_closed": [],
    }


def test_bulk_needs_adjudication_closes_two_tickets_in_one_call(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket: TicketNeedsAdjudicationDetails,
    another_na_ticket: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
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
                    "duplicate_individual_ids": [str(na_ticket.golden_records_individual.id)],
                    "distinct_individual_ids": [str(na_ticket.possible_duplicates.first().id)],
                },
                {
                    "ticket_id": str(another_na_ticket.ticket.id),
                    "duplicate_individual_ids": [str(another_na_ticket.golden_records_individual.id)],
                    "distinct_individual_ids": [str(another_na_ticket.possible_duplicates.first().id)],
                },
            ]
        },
        format="json",
    )

    na_ticket.ticket.refresh_from_db()
    another_na_ticket.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert na_ticket.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert another_na_ticket.ticket.status == GrievanceTicket.STATUS_CLOSED
    assert len(response.data["resolved"]) == 2


def test_bulk_needs_adjudication_rejects_a_ticket_from_another_business_area(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_in_other_business_area: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_in_other_business_area.golden_records_individual
    duplicate = na_ticket_in_other_business_area.possible_duplicates.first()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_in_other_business_area.ticket.id),
                    "duplicate_individual_ids": [str(golden.id)],
                    "distinct_individual_ids": [str(duplicate.id)],
                }
            ]
        },
        format="json",
    )

    na_ticket_in_other_business_area.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket_in_other_business_area.ticket.status == GrievanceTicket.STATUS_NEW


def test_bulk_needs_adjudication_rejects_reassigning_a_role_to_another_duplicate(
    api_client: Any,
    user: User,
    business_area: BusinessArea,
    na_ticket_two_duplicates_sharing_a_household: TicketNeedsAdjudicationDetails,
    bulk_na_url: str,
    create_user_role_with_permissions: Callable,
) -> None:
    # Handing the collector role to somebody this same batch withdraws would leave the household
    # represented by a duplicate.
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        business_area,
        whole_business_area_access=True,
    )
    golden = na_ticket_two_duplicates_sharing_a_household.golden_records_individual
    collector = IndividualRoleInHousehold.objects.get(role=ROLE_PRIMARY).individual
    other_duplicate = na_ticket_two_duplicates_sharing_a_household.possible_duplicates.exclude(id=collector.id).get()

    client = api_client(user)
    response = client.post(
        bulk_na_url,
        {
            "tickets": [
                {
                    "ticket_id": str(na_ticket_two_duplicates_sharing_a_household.ticket.id),
                    "duplicate_individual_ids": [str(collector.id), str(other_duplicate.id)],
                    "distinct_individual_ids": [str(golden.id)],
                    "role_reassign_data": {
                        "PRIMARY": {
                            "role": "PRIMARY",
                            "household": str(collector.household.id),
                            "individual": str(collector.id),
                            "new_individual": str(other_duplicate.id),
                        }
                    },
                }
            ]
        },
        format="json",
    )

    na_ticket_two_duplicates_sharing_a_household.ticket.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert na_ticket_two_duplicates_sharing_a_household.ticket.status == GrievanceTicket.STATUS_NEW
