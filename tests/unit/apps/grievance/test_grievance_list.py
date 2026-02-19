"""Tests for grievance ticket list views."""

from datetime import datetime
import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PartnerFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Area, BusinessArea, Country, Partner, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="AFG")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
    )


@pytest.fixture
def program_different(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def partner() -> Partner:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def user2(partner: Partner) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def country() -> Country:
    return CountryFactory()


@pytest.fixture
def admin_type(country: Country) -> Any:
    return AreaTypeFactory(country=country, area_level=1)


@pytest.fixture
def area1(admin_type: Any) -> Area:
    return AreaFactory(parent=None, p_code="AF01", area_type=admin_type)


@pytest.fixture
def area2(admin_type: Any) -> Area:
    return AreaFactory(parent=None, p_code="AF0101", area_type=admin_type)


@pytest.fixture
def grievance_tickets(
    afghanistan: BusinessArea,
    user: User,
    user2: User,
    area1: Area,
    area2: Area,
) -> list[GrievanceTicket]:
    created_at_dates_to_set = {
        GrievanceTicket.STATUS_NEW: [
            timezone.make_aware(datetime(year=2020, month=3, day=12)),
            timezone.make_aware(datetime(year=2020, month=3, day=13)),
            timezone.make_aware(datetime(year=2020, month=3, day=14)),
        ],
        GrievanceTicket.STATUS_ON_HOLD: [timezone.make_aware(datetime(year=2020, month=7, day=12))],
        GrievanceTicket.STATUS_IN_PROGRESS: [
            timezone.make_aware(datetime(year=2020, month=8, day=22)),
            timezone.make_aware(datetime(year=2020, month=8, day=23)),
            timezone.make_aware(datetime(year=2020, month=8, day=24)),
            timezone.make_aware(datetime(year=2020, month=8, day=25)),
        ],
        GrievanceTicket.STATUS_CLOSED: [
            timezone.make_aware(datetime(year=2020, month=8, day=26)),
        ],
    }

    grievances_to_create = (
        GrievanceTicket(
            business_area=afghanistan,
            admin2=area1,
            language="Polish",
            consent=True,
            description="Non-sensitive ticket with program, in admin area 1, new, creator and owner",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            status=GrievanceTicket.STATUS_NEW,
            created_by=user,
            assigned_to=user,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
        ),
        GrievanceTicket(
            business_area=afghanistan,
            admin2=area1,
            language="Polish",
            consent=True,
            description="Non-sensitive ticket with program, in admin area 1, new, creator",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            status=GrievanceTicket.STATUS_NEW,
            created_by=user,
            assigned_to=user2,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
        ),
        GrievanceTicket(
            business_area=afghanistan,
            admin2=area2,
            language="Polish",
            consent=True,
            description="Non-sensitive ticket with program, in admin area 1, owner",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            status=GrievanceTicket.STATUS_NEW,
            created_by=user2,
            assigned_to=user,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        ),
        GrievanceTicket(
            business_area=afghanistan,
            admin2=area2,
            language="English",
            consent=True,
            description="Sensitive ticket with program, in admin area 2, on hold, owner and creator",
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            status=GrievanceTicket.STATUS_ON_HOLD,
            created_by=user,
            assigned_to=user,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
        ),
        GrievanceTicket(
            business_area=afghanistan,
            admin2=area1,
            language="Polish, English",
            consent=True,
            description="Sensitive ticket with program, in admin area 2, in progress, owner",
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
            created_by=user2,
            assigned_to=user,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE,
        ),
        GrievanceTicket(
            business_area=afghanistan,
            admin2=area2,
            language="Polish, English",
            consent=True,
            description="Sensitive ticket with program, in admin area 2, in progress, creator",
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
            created_by=user,
            assigned_to=user2,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=GrievanceTicket.ISSUE_TYPE_HARASSMENT,
        ),
        GrievanceTicket(
            business_area=afghanistan,
            admin2=None,
            language="Polish, English",
            consent=True,
            description="Non-sensitive ticket with program, without admin area, creator and owner",
            category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
            created_by=user,
            assigned_to=user,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=None,
        ),
        GrievanceTicket(
            business_area=afghanistan,
            admin2=None,
            language="Polish, English",
            consent=True,
            description="Non-sensitive ticket without program, without admin area, creator and owner",
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
            created_by=user,
            assigned_to=user,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        ),
        GrievanceTicket(
            business_area=afghanistan,
            admin2=area1,
            language="Polish, English",
            consent=True,
            description="Non-sensitive ticket without program, in admin area 1, creator and owner",
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            status=GrievanceTicket.STATUS_CLOSED,
            created_by=user,
            assigned_to=user,
            user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            issue_type=None,
        ),
    )
    tickets = GrievanceTicket.objects.bulk_create(grievances_to_create)

    for gv_status, dates in created_at_dates_to_set.items():
        gts = GrievanceTicket.objects.filter(status=gv_status)
        for gt in gts:
            gt.created_at = dates.pop(0)
            gt.save(update_fields=("created_at",))

    return tickets


@pytest.fixture
def household_and_individuals(
    afghanistan: BusinessArea,
    program: Program,
    area1: Area,
    area2: Area,
    country: Country,
) -> tuple[Any, list[Any]]:
    individual1 = IndividualFactory(
        business_area=afghanistan,
        household=None,
    )
    household = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        country=country,
        country_origin=country,
        program=program,
        business_area=afghanistan,
        head_of_household=individual1,
    )
    individual2 = IndividualFactory(
        business_area=afghanistan,
        household=household,
    )
    individual1.household = household
    individual1.save()
    return household, [individual1, individual2]


@pytest.fixture
def needs_adjudication_details(
    grievance_tickets: list[GrievanceTicket],
    household_and_individuals: tuple[Any, list[Any]],
) -> Any:
    _, individuals = household_and_individuals
    return TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance_tickets[0],
        golden_records_individual=individuals[0],
        possible_duplicate=individuals[1],
        score_min=100,
        score_max=150,
        extra_data={
            "golden_records": [
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(individuals[0].pk),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": 1.2,
                    "duplicate": False,
                    "distinct": True,
                }
            ],
            "possible_duplicate": [
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(individuals[1].pk),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": 2.0,
                    "duplicate": True,
                    "distinct": False,
                }
            ],
        },
    )


@pytest.fixture
def grievance_ticket_different_program(
    afghanistan: BusinessArea,
    area1: Area,
    user: User,
    program_different: Program,
) -> GrievanceTicket:
    ticket = GrievanceTicketFactory(
        business_area=afghanistan,
        admin2=area1,
        language="Polish",
        consent=True,
        description="Non-sensitive ticket in different program, in admin area 1, new, creator and owner",
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        assigned_to=user,
    )
    ticket.programs.add(program_different)
    return ticket


@pytest.fixture
def setup_grievance_tickets(
    grievance_tickets: list[GrievanceTicket],
    program: Program,
    needs_adjudication_details: Any,
    grievance_ticket_different_program: GrievanceTicket,
) -> list[GrievanceTicket]:
    for grievance_ticket in grievance_tickets:
        grievance_ticket.programs.add(program)
        grievance_ticket.refresh_from_db()

    for grievance_ticket in grievance_tickets[:-1]:
        grievance_ticket.linked_tickets.add(grievance_tickets[-1])

    return grievance_tickets


@pytest.fixture
def list_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:grievance:grievance-tickets-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )


@pytest.fixture
def count_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:grievance:grievance-tickets-count",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )


@pytest.fixture
def api_client(user: User, api_client: Callable) -> Any:
    return api_client(user)


@freeze_time("2024-08-25 12:00:00")
def test_grievance_ticket_list_with_all_permissions(
    api_client: Any,
    list_url: str,
    count_url: str,
    user: User,
    afghanistan: BusinessArea,
    setup_grievance_tickets: list[GrievanceTicket],
    grievance_ticket_different_program: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
        ],
        afghanistan,
        whole_business_area_access=True,
    )

    response = api_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 9

    response_count = api_client.get(count_url)

    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 9

    result_ids = [result["id"] for result in response_results]
    assert str(grievance_ticket_different_program.id) not in result_ids

    for i, grievance_ticket in enumerate(reversed(setup_grievance_tickets)):
        grievance_ticket_result = response_results[i]
        assert grievance_ticket_result["id"] == str(grievance_ticket.id)
        assert grievance_ticket_result["unicef_id"] == grievance_ticket.unicef_id
        assert grievance_ticket_result["status"] == grievance_ticket.status
        assert grievance_ticket_result["programs"] == [
            {
                "id": str(grievance_ticket.programs.first().id),
                "programme_code": grievance_ticket.programs.first().programme_code,
                "slug": grievance_ticket.programs.first().slug,
                "name": grievance_ticket.programs.first().name,
                "status": grievance_ticket.programs.first().status,
                "screen_beneficiary": grievance_ticket.programs.first().screen_beneficiary,
            }
        ]
        household = getattr(getattr(grievance_ticket, "ticket_details", None), "household", None)
        if household:
            assert grievance_ticket_result["household_id"] == str(household.id)
            assert grievance_ticket_result["household_unicef_id"] == household.unicef_id
        assert grievance_ticket_result["assigned_to"] == {
            "id": str(grievance_ticket.assigned_to.id),
            "first_name": grievance_ticket.assigned_to.first_name,
            "last_name": grievance_ticket.assigned_to.last_name,
            "email": grievance_ticket.assigned_to.email,
            "username": grievance_ticket.assigned_to.username,
        }
        assert grievance_ticket_result["created_by"] == {
            "id": str(grievance_ticket.created_by.id),
            "first_name": grievance_ticket.created_by.first_name,
            "last_name": grievance_ticket.created_by.last_name,
            "email": grievance_ticket.created_by.email,
            "username": grievance_ticket.created_by.username,
        }
        assert grievance_ticket_result["user_modified"] == f"{grievance_ticket.user_modified:%Y-%m-%dT%H:%M:%SZ}"
        assert grievance_ticket_result["category"] == grievance_ticket.category
        assert grievance_ticket_result["issue_type"] == grievance_ticket.issue_type
        assert grievance_ticket_result["priority"] == grievance_ticket.priority
        assert grievance_ticket_result["urgency"] == grievance_ticket.urgency
        assert grievance_ticket_result["created_at"] == f"{grievance_ticket.created_at:%Y-%m-%dT%H:%M:%SZ}"

        # total_days
        if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
            delta = grievance_ticket.updated_at - grievance_ticket.created_at
        else:
            delta = timezone.now() - grievance_ticket.created_at
        expected_total_days = delta.days
        assert grievance_ticket_result["total_days"] == expected_total_days
        if grievance_ticket.target_id:
            assert grievance_ticket_result["target_id"] == grievance_ticket.target_id

        assert grievance_ticket_result["related_tickets"] == [
            {
                "id": str(linked_ticket.id),
                "unicef_id": linked_ticket.unicef_id,
            }
            for linked_ticket in grievance_ticket.linked_tickets.all()
        ]


@pytest.mark.parametrize(
    "permissions",
    [
        [],
        [Permissions.PROGRAMME_ACTIVATE],
    ],
)
def test_grievance_ticket_list_without_permissions(
    api_client: Any,
    list_url: str,
    count_url: str,
    user: User,
    afghanistan: BusinessArea,
    permissions: list,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        whole_business_area_access=True,
    )

    response = api_client.get(list_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response_count = api_client.get(count_url)
    assert response_count.status_code == status.HTTP_403_FORBIDDEN


def test_grievance_ticket_list_area_limits(
    api_client: Any,
    list_url: str,
    user: User,
    afghanistan: BusinessArea,
    partner: Partner,
    program: Program,
    area1: Area,
    setup_grievance_tickets: list[GrievanceTicket],
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
        ],
        afghanistan,
        whole_business_area_access=True,
    )
    set_admin_area_limits_in_program(partner, program, [area1])

    # Only grievance tickets with area1 should be returned.

    response = api_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 6

    result_ids = [result["id"] for result in response_results]
    assert str(setup_grievance_tickets[0].id) in result_ids  # area1
    assert str(setup_grievance_tickets[1].id) in result_ids  # area1
    assert str(setup_grievance_tickets[2].id) not in result_ids  # area2
    assert str(setup_grievance_tickets[3].id) not in result_ids  # area2
    assert str(setup_grievance_tickets[4].id) in result_ids  # area1
    assert str(setup_grievance_tickets[5].id) not in result_ids  # area2
    assert str(setup_grievance_tickets[6].id) in result_ids  # area None
    assert str(setup_grievance_tickets[7].id) in result_ids  # area None
    assert str(setup_grievance_tickets[8].id) in result_ids  # area1


def test_grievance_ticket_list_with_all_permissions_in_program(
    api_client: Any,
    list_url: str,
    count_url: str,
    user: User,
    afghanistan: BusinessArea,
    program: Program,
    setup_grievance_tickets: list[GrievanceTicket],
    grievance_ticket_different_program: GrievanceTicket,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
        ],
        afghanistan,
        program=program,
    )

    response = api_client.get(list_url)
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 9

    response_count = api_client.get(count_url)
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 9

    result_ids = [result["id"] for result in response_results]
    assert str(grievance_ticket_different_program.id) not in result_ids


@pytest.mark.parametrize(
    ("permissions", "area_limit", "expected_tickets"),
    [
        (
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            False,
            [0, 1, 2, 6, 7, 8],
        ),
        (
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR],
            False,
            [0, 1, 6, 7, 8],
        ),
        (
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER],
            False,
            [0, 2, 6, 7, 8],
        ),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE], False, [3, 4, 5]),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR], False, [3, 5]),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER], False, [3, 4]),
        (
            [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            ],
            False,
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
        ),
        (
            [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            ],
            True,
            [0, 1, 4, 6, 7, 8],
        ),
    ],
)
def test_grievance_ticket_list_based_on_permissions(
    api_client: Any,
    list_url: str,
    count_url: str,
    user: User,
    afghanistan: BusinessArea,
    partner: Partner,
    program: Program,
    area1: Area,
    permissions: list,
    area_limit: bool,
    expected_tickets: list,
    setup_grievance_tickets: list[GrievanceTicket],
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        program=program,
    )
    if area_limit:
        set_admin_area_limits_in_program(partner, program, [area1])

    response = api_client.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == len(expected_tickets)

    response_count = api_client.get(count_url)

    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == len(expected_tickets)

    result_ids = [result["id"] for result in response_results]
    for i in expected_tickets:
        assert str(setup_grievance_tickets[i].id) in result_ids


def test_grievance_ticket_list_caching(
    api_client: Any,
    list_url: str,
    user: User,
    afghanistan: BusinessArea,
    partner: Partner,
    program: Program,
    area1: Area,
    setup_grievance_tickets: list[GrievanceTicket],
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
        ],
        afghanistan,
        whole_business_area_access=True,
    )

    with CaptureQueriesContext(connection) as ctx:
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 9
        assert len(ctx.captured_queries) == 47

    # no change - use cache
    with CaptureQueriesContext(connection) as ctx:
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second_call = response.headers["etag"]
        assert etag == etag_second_call
        assert len(ctx.captured_queries) == 10

    ticket = setup_grievance_tickets[0]
    ticket.priority = 1
    ticket.save()
    with CaptureQueriesContext(connection) as ctx:
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_third_call = response.headers["etag"]
        assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
        assert etag_third_call not in [etag, etag_second_call]
        # 5 queries are saved because of cached permissions calculations
        assert len(ctx.captured_queries) == 42

    set_admin_area_limits_in_program(partner, program, [area1])
    with CaptureQueriesContext(connection) as ctx:
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_changed_areas = response.headers["etag"]
        assert len(response.json()["results"]) == 6
        assert json.loads(cache.get(etag_changed_areas)[0].decode("utf8")) == response.json()
        assert etag_changed_areas not in [etag, etag_second_call, etag_third_call]
        assert len(ctx.captured_queries) == 39

    ticket.delete()
    with CaptureQueriesContext(connection) as ctx:
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fourth_call = response.headers["etag"]
        assert len(response.json()["results"]) == 5
        assert etag_fourth_call not in [
            etag,
            etag_second_call,
            etag_third_call,
            etag_changed_areas,
        ]
        assert len(ctx.captured_queries) == 35

    # no change - use cache
    with CaptureQueriesContext(connection) as ctx:
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fifth_call = response.headers["etag"]
        assert etag_fifth_call == etag_fourth_call
        assert len(ctx.captured_queries) == 10
