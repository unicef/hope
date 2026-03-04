from datetime import datetime
from typing import Any, Callable

from django.utils import timezone
from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import BeneficiaryGroupFactory, BusinessAreaFactory, DataCollectingTypeFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import BusinessArea, DataCollectingType, Partner, Program, User

pytestmark = pytest.mark.django_db()


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", code="AFG")


@pytest.fixture
def ukraine() -> BusinessArea:
    return BusinessAreaFactory(slug="ukraine", name="Ukraine")


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
def social_dct() -> Any:
    return DataCollectingTypeFactory(
        label="Social",
        code="social",
        type=DataCollectingType.Type.SOCIAL,
    )


@pytest.fixture
def social_beneficiary_group() -> Any:
    return BeneficiaryGroupFactory(master_detail=False)


@pytest.fixture
def program_afghanistan1(afghanistan: BusinessArea, social_dct: Any, social_beneficiary_group: Any) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 1",
        data_collecting_type=social_dct,
        beneficiary_group=social_beneficiary_group,
    )


@pytest.fixture
def program_afghanistan2(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=afghanistan,
        status=Program.ACTIVE,
        name="program afghanistan 2",
    )


@pytest.fixture
def program_ukraine(ukraine: BusinessArea) -> Program:
    return ProgramFactory(business_area=ukraine, status=Program.ACTIVE)


@pytest.fixture
def country() -> Any:
    return CountryFactory()


@pytest.fixture
def admin_type(country: Any) -> Any:
    return AreaTypeFactory(country=country, area_level=1)


@pytest.fixture
def area1(admin_type: Any) -> Any:
    return AreaFactory(parent=None, p_code="AF01", area_type=admin_type)


@pytest.fixture
def area2(admin_type: Any) -> Any:
    return AreaFactory(parent=None, p_code="AF0101", area_type=admin_type)


@pytest.fixture
def grievance_tickets_setup(
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    program_afghanistan1: Program,
    program_afghanistan2: Program,
    program_ukraine: Program,
    user: User,
    user2: User,
    area1: Any,
    area2: Any,
    country: Any,
) -> dict:
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
    grievance_tickets = GrievanceTicket.objects.bulk_create(grievances_to_create)

    for gv_status, dates in created_at_dates_to_set.items():
        gts = GrievanceTicket.objects.filter(status=gv_status)
        for gt in gts:
            gt.created_at = dates.pop(0)
            gt.save(update_fields=("created_at",))

    individual1 = IndividualFactory(
        household=None,
        program=program_afghanistan1,
        business_area=afghanistan,
    )
    household1 = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        country=country,
        country_origin=country,
        program=program_afghanistan1,
        business_area=afghanistan,
        head_of_household=individual1,
    )
    individual1.household = household1
    individual1.save()

    individual2 = IndividualFactory(
        household=household1,
        program=program_afghanistan1,
        business_area=afghanistan,
    )

    TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance_tickets[0],
        golden_records_individual=individual1,
        possible_duplicate=individual2,
        score_min=100,
        score_max=150,
        extra_data={
            "golden_records": [
                {
                    "dob": "date_of_birth",
                    "full_name": "full_name",
                    "hit_id": str(individual1.pk),
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
                    "hit_id": str(individual2.pk),
                    "location": "location",
                    "proximity_to_score": "proximity_to_score",
                    "score": 2.0,
                    "duplicate": True,
                    "distinct": False,
                }
            ],
        },
    )

    # test fallback_individual_unicef_id_annotated
    sw_individual = IndividualFactory(
        household=None,
        program=program_afghanistan1,
        business_area=afghanistan,
    )
    sw_household = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        country=country,
        country_origin=country,
        program=program_afghanistan1,
        business_area=afghanistan,
        head_of_household=sw_individual,
    )
    sw_individual.household = sw_household
    sw_individual.save()

    TicketHouseholdDataUpdateDetailsFactory(
        ticket=grievance_tickets[2],
        household=sw_household,
        household_data={},
    )

    grievance_ticket_ukraine = GrievanceTicketFactory(
        business_area=ukraine,
        admin2=area1,
        language="Polish",
        consent=True,
        description="Non-sensitive ticket with program, in admin area 1, new, creator and owner",
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
        status=GrievanceTicket.STATUS_NEW,
        created_by=user,
        assigned_to=user,
    )
    grievance_ticket_ukraine.programs.add(program_ukraine)

    grievance_tickets[0].programs.add(program_afghanistan1)
    grievance_tickets[1].programs.add(program_afghanistan2)
    grievance_tickets[2].programs.add(program_afghanistan1)
    grievance_tickets[3].programs.add(program_afghanistan2)
    grievance_tickets[4].programs.add(program_afghanistan1)
    grievance_tickets[5].programs.add(program_afghanistan2)
    grievance_tickets[6].programs.add(program_afghanistan1)
    grievance_tickets[7].programs.add(program_afghanistan2)
    grievance_tickets[8].programs.add(program_afghanistan1)

    for grievance_ticket in grievance_tickets:
        grievance_ticket.refresh_from_db()

    for grievance_ticket in grievance_tickets[:-1]:
        grievance_ticket.linked_tickets.add(grievance_tickets[-1])

    return {
        "grievance_tickets": grievance_tickets,
        "grievance_ticket_ukraine": grievance_ticket_ukraine,
        "household1": household1,
        "individual1": individual1,
        "individual2": individual2,
    }


@freeze_time("2024-08-25 12:00:00")
def test_grievance_ticket_global_list_with_all_permissions(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    grievance_tickets_setup: dict,
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

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 9

    response_count = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-count",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 9

    grievance_tickets = grievance_tickets_setup["grievance_tickets"]
    grievance_ticket_ukraine = grievance_tickets_setup["grievance_ticket_ukraine"]

    result_ids = [result["id"] for result in response_results]
    assert str(grievance_ticket_ukraine.id) not in result_ids

    for i, grievance_ticket in enumerate(reversed(grievance_tickets)):
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


@freeze_time("2024-08-25 12:00:00")
@pytest.mark.parametrize(
    "permissions",
    [
        [],
        [Permissions.PROGRAMME_ACTIVATE],
    ],
)
def test_grievance_ticket_global_list_without_permissions(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    grievance_tickets_setup: dict,
    permissions: list,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        whole_business_area_access=True,
    )

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response_count = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-count",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response_count.status_code == status.HTTP_403_FORBIDDEN


@freeze_time("2024-08-25 12:00:00")
def test_grievance_ticket_global_list_check_non_program(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    grievance_tickets_setup: dict,
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
    GrievanceTicketFactory(
        description="Test 1",
        assigned_to=user,
        category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        issue_type=GrievanceTicket.ISSUE_TYPE_OTHER_COMPLAINT,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        business_area=afghanistan,
    )

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 10

    response_count = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-count",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 10


@freeze_time("2024-08-25 12:00:00")
def test_grievance_ticket_global_list_area_limits(
    api_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program_afghanistan1: Program,
    program_afghanistan2: Program,
    area1: Any,
    area2: Any,
    grievance_tickets_setup: dict,
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
    set_admin_area_limits_in_program(partner, program_afghanistan1, [area1])
    set_admin_area_limits_in_program(partner, program_afghanistan2, [area2])

    # Only grievance tickets with area1 in program1 and area2 in program2 should be returned.

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 7

    grievance_tickets = grievance_tickets_setup["grievance_tickets"]

    result_ids = [result["id"] for result in response_results]
    assert str(grievance_tickets[0].id) in result_ids  # program1, area1
    assert str(grievance_tickets[1].id) not in result_ids  # program2, area1
    assert str(grievance_tickets[2].id) not in result_ids  # program1, area2
    assert str(grievance_tickets[3].id) in result_ids  # program2, area2
    assert str(grievance_tickets[4].id) in result_ids  # program1, area1
    assert str(grievance_tickets[5].id) in result_ids  # program2, area2
    assert str(grievance_tickets[6].id) in result_ids  # program1, area None
    assert str(grievance_tickets[7].id) in result_ids  # program2, area None
    assert str(grievance_tickets[8].id) in result_ids  # program1, area1


@freeze_time("2024-08-25 12:00:00")
def test_grievance_ticket_global_list_with_permissions_in_one_program(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    program_afghanistan1: Program,
    grievance_tickets_setup: dict,
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
        program=program_afghanistan1,
    )

    # Only grievance tickets in program1 should be returned.

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 5

    grievance_tickets = grievance_tickets_setup["grievance_tickets"]

    result_ids = [result["id"] for result in response_results]
    assert str(grievance_tickets[0].id) in result_ids
    assert str(grievance_tickets[1].id) not in result_ids
    assert str(grievance_tickets[2].id) in result_ids
    assert str(grievance_tickets[3].id) not in result_ids
    assert str(grievance_tickets[4].id) in result_ids
    assert str(grievance_tickets[5].id) not in result_ids
    assert str(grievance_tickets[6].id) in result_ids
    assert str(grievance_tickets[7].id) not in result_ids
    assert str(grievance_tickets[8].id) in result_ids


@freeze_time("2024-08-25 12:00:00")
@pytest.mark.parametrize(
    ("permissions", "program_num", "area_limit", "expected_tickets"),
    [
        (
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            1,
            False,
            [0, 2, 6, 8],
        ),
        (
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR],
            1,
            False,
            [0, 6, 8],
        ),
        (
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER],
            1,
            False,
            [0, 2, 6, 8],
        ),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE], 1, False, [4]),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR], 1, False, []),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER], 1, False, [4]),
        (
            [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            ],
            1,
            False,
            [0, 2, 4, 6, 8],
        ),
        ([Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE], 2, False, [1, 7]),
        (
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR],
            2,
            False,
            [1, 7],
        ),
        (
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER],
            2,
            False,
            [7],
        ),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE], 2, False, [3, 5]),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR], 2, False, [3, 5]),
        ([Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER], 2, False, [3]),
        (
            [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            ],
            2,
            False,
            [1, 3, 5, 7],
        ),
        (
            [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            ],
            1,
            True,
            [0, 4, 6, 8],
        ),
        (
            [
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            ],
            2,
            True,
            [1, 7],
        ),
    ],
)
def test_grievance_ticket_global_list_based_on_permissions(
    api_client: Any,
    user: User,
    partner: Partner,
    afghanistan: BusinessArea,
    program_afghanistan1: Program,
    program_afghanistan2: Program,
    area1: Any,
    grievance_tickets_setup: dict,
    permissions: list,
    program_num: int,
    area_limit: bool,
    expected_tickets: list,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    program = program_afghanistan1 if program_num == 1 else program_afghanistan2
    create_user_role_with_permissions(
        user,
        permissions,
        afghanistan,
        program=program,
    )
    if area_limit:
        set_admin_area_limits_in_program(partner, program, [area1])

    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == len(expected_tickets)

    response_count = client.get(
        reverse(
            "api:grievance:grievance-tickets-global-count",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == len(expected_tickets)

    grievance_tickets = grievance_tickets_setup["grievance_tickets"]

    result_ids = [result["id"] for result in response_results]
    for i in expected_tickets:
        assert str(grievance_tickets[i].id) in result_ids


def test_all_edit_household_fields_attributes(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-all-edit-household-fields-attributes",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 39

    first_field = data[0]
    assert "id" in first_field
    assert "name" in first_field
    assert "type" in first_field
    assert "labels" in first_field
    assert "label_en" in first_field
    assert "hint" in first_field
    assert "choices" in first_field
    assert "associated_with" in first_field
    assert "is_flex_field" in first_field

    field_names = [field["name"] for field in data]
    assert "size" in field_names
    assert "residence_status" in field_names
    assert "country" in field_names

    assert all(field["associated_with"] == "Household" for field in data)


def test_all_edit_people_fields_attributes(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-all-edit-people-fields-attributes",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 43

    first_field = data[0]
    assert "id" in first_field
    assert "name" in first_field
    assert "type" in first_field
    assert "labels" in first_field
    assert "label_en" in first_field
    assert "hint" in first_field
    assert "choices" in first_field
    assert "associated_with" in first_field
    assert "is_flex_field" in first_field

    field_names = [field["name"] for field in data]
    assert "full_name" in field_names
    assert "birth_date" in field_names
    assert "sex" in field_names
    assert "relationship" in field_names


def test_all_add_individuals_fields_attributes(
    api_client: Any,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user,
        [Permissions.GRIEVANCES_CREATE],
        afghanistan,
        whole_business_area_access=True,
    )
    client = api_client(user)
    response = client.get(
        reverse(
            "api:grievance-tickets:grievance-tickets-global-all-add-individuals-fields-attributes",
            kwargs={"business_area_slug": afghanistan.slug},
        )
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 30

    first_field = data[0]
    assert "id" in first_field
    assert "name" in first_field
    assert "type" in first_field
    assert "labels" in first_field
    assert "label_en" in first_field
    assert "hint" in first_field
    assert "choices" in first_field
    assert "associated_with" in first_field
    assert "is_flex_field" in first_field

    field_names = [field["name"] for field in data]
    assert "full_name" in field_names
    assert "birth_date" in field_names
    assert "sex" in field_names
    assert "relationship" in field_names

    assert all(field["associated_with"] == "Individual" for field in data)
