from datetime import datetime
from typing import Any, Callable

from django.utils import timezone
from freezegun import freeze_time
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.old_factories.account import PartnerFactory, UserFactory
from extras.test_utils.old_factories.core import DataCollectingTypeFactory, create_afghanistan, create_ukraine
from extras.test_utils.old_factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.old_factories.grievance import (
    GrievanceComplaintTicketWithoutExtrasFactory,
    GrievanceTicketFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory,
    TicketDeleteHouseholdDetailsFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketPaymentVerificationDetailsFactory,
    TicketSystemFlaggingDetailsFactory,
)
from extras.test_utils.old_factories.household import create_household_and_individuals
from extras.test_utils.old_factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.old_factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.old_factories.sanction_list import SanctionListIndividualFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket, TicketHouseholdDataUpdateDetails, TicketNeedsAdjudicationDetails
from hope.models import DataCollectingType, Program

pytestmark = pytest.mark.django_db()


@freeze_time("2024-08-25 12:00:00")
class TestGrievanceTicketGlobalList:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.global_url_name = "api:grievance:grievance-tickets-global-list"
        self.global_count_url = "api:grievance:grievance-tickets-global-count"
        self.afghanistan = create_afghanistan()
        self.ukraine = create_ukraine()
        social_dct = DataCollectingTypeFactory(
            label="Social",
            code="social",
            type=DataCollectingType.Type.SOCIAL,
        )
        self.program_afghanistan1 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
            data_collecting_type=social_dct,
        )
        self.program_afghanistan2 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 2",
        )
        self.program_ukraine = ProgramFactory(business_area=self.ukraine, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.user2 = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        self.admin_type = AreaTypeFactory(country=self.country, area_level=1)
        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=self.admin_type)
        self.area2 = AreaFactory(parent=None, p_code="AF0101", area_type=self.admin_type)

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
                business_area=self.afghanistan,
                admin2=self.area1,
                language="Polish",
                consent=True,
                description="Non-sensitive ticket with program, in admin area 1, new, creator and owner",
                category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                status=GrievanceTicket.STATUS_NEW,
                created_by=self.user,
                assigned_to=self.user,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
                issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
            ),
            GrievanceTicket(
                business_area=self.afghanistan,
                admin2=self.area1,
                language="Polish",
                consent=True,
                description="Non-sensitive ticket with program, in admin area 1, new, creator",
                category=GrievanceTicket.CATEGORY_DATA_CHANGE,
                status=GrievanceTicket.STATUS_NEW,
                created_by=self.user,
                assigned_to=self.user2,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
                issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            ),
            GrievanceTicket(
                business_area=self.afghanistan,
                admin2=self.area2,
                language="Polish",
                consent=True,
                description="Non-sensitive ticket with program, in admin area 1, owner",
                category=GrievanceTicket.CATEGORY_DATA_CHANGE,
                status=GrievanceTicket.STATUS_NEW,
                created_by=self.user2,
                assigned_to=self.user,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
                issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            ),
            GrievanceTicket(
                business_area=self.afghanistan,
                admin2=self.area2,
                language="English",
                consent=True,
                description="Sensitive ticket with program, in admin area 2, on hold, owner and creator",
                category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                status=GrievanceTicket.STATUS_ON_HOLD,
                created_by=self.user,
                assigned_to=self.user,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
                issue_type=GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
            ),
            GrievanceTicket(
                business_area=self.afghanistan,
                admin2=self.area1,
                language="Polish, English",
                consent=True,
                description="Sensitive ticket with program, in admin area 2, in progress, owner",
                category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                status=GrievanceTicket.STATUS_IN_PROGRESS,
                created_by=self.user2,
                assigned_to=self.user,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
                issue_type=GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE,
            ),
            GrievanceTicket(
                business_area=self.afghanistan,
                admin2=self.area2,
                language="Polish, English",
                consent=True,
                description="Sensitive ticket with program, in admin area 2, in progress, creator",
                category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                status=GrievanceTicket.STATUS_IN_PROGRESS,
                created_by=self.user,
                assigned_to=self.user2,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
                issue_type=GrievanceTicket.ISSUE_TYPE_HARASSMENT,
            ),
            GrievanceTicket(
                business_area=self.afghanistan,
                admin2=None,
                language="Polish, English",
                consent=True,
                description="Non-sensitive ticket with program, without admin area, creator and owner",
                category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
                status=GrievanceTicket.STATUS_IN_PROGRESS,
                created_by=self.user,
                assigned_to=self.user,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            ),
            GrievanceTicket(
                business_area=self.afghanistan,
                admin2=None,
                language="Polish, English",
                consent=True,
                description="Non-sensitive ticket without program, without admin area, creator and owner",
                category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                status=GrievanceTicket.STATUS_IN_PROGRESS,
                created_by=self.user,
                assigned_to=self.user,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
                issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
            ),
            GrievanceTicket(
                business_area=self.afghanistan,
                admin2=self.area1,
                language="Polish, English",
                consent=True,
                description="Non-sensitive ticket without program, in admin area 1, creator and owner",
                category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
                status=GrievanceTicket.STATUS_CLOSED,
                created_by=self.user,
                assigned_to=self.user,
                user_modified=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            ),
        )
        self.grievance_tickets = GrievanceTicket.objects.bulk_create(grievances_to_create)

        for gv_status, dates in created_at_dates_to_set.items():
            gts = GrievanceTicket.objects.filter(status=gv_status)
            for gt in gts:
                gt.created_at = dates.pop(0)
                gt.save(update_fields=("created_at",))

        self.household1, self.individuals1 = create_household_and_individuals(
            household_data={
                "admin1": self.area1,
                "admin2": self.area2,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        TicketNeedsAdjudicationDetails.objects.create(
            ticket=self.grievance_tickets[0],
            golden_records_individual=self.individuals1[0],
            possible_duplicate=self.individuals1[1],
            score_min=100,
            score_max=150,
            extra_data={
                "golden_records": [
                    {
                        "dob": "date_of_birth",
                        "full_name": "full_name",
                        "hit_id": str(self.individuals1[0].pk),
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
                        "hit_id": str(self.individuals1[1].pk),
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
        TicketHouseholdDataUpdateDetails.objects.create(
            ticket=self.grievance_tickets[2],
            household=self.household1,
            household_data={},
        )

        self.grievance_ticket_ukraine = GrievanceTicketFactory(
            business_area=self.ukraine,
            admin2=self.area1,
            language="Polish",
            consent=True,
            description="Non-sensitive ticket with program, in admin area 1, new, creator and owner",
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            status=GrievanceTicket.STATUS_NEW,
            created_by=self.user,
            assigned_to=self.user,
        )
        self.grievance_ticket_ukraine.programs.add(self.program_ukraine)

        self.grievance_tickets[0].programs.add(self.program_afghanistan1)
        self.grievance_tickets[1].programs.add(self.program_afghanistan2)
        self.grievance_tickets[2].programs.add(self.program_afghanistan1)
        self.grievance_tickets[3].programs.add(self.program_afghanistan2)
        self.grievance_tickets[4].programs.add(self.program_afghanistan1)
        self.grievance_tickets[5].programs.add(self.program_afghanistan2)
        self.grievance_tickets[6].programs.add(self.program_afghanistan1)
        self.grievance_tickets[7].programs.add(self.program_afghanistan2)
        self.grievance_tickets[8].programs.add(self.program_afghanistan1)

        for grievance_ticket in self.grievance_tickets:
            grievance_ticket.refresh_from_db()

        for grievance_ticket in self.grievance_tickets[:-1]:
            grievance_ticket.linked_tickets.add(self.grievance_tickets[-1])

    def test_grievance_ticket_global_list_with_all_permissions(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 9

        response_count = self.api_client.get(
            reverse(
                self.global_count_url,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 9

        result_ids = [result["id"] for result in response_results]
        assert str(self.grievance_ticket_ukraine.id) not in result_ids

        for i, grievance_ticket in enumerate(reversed(self.grievance_tickets)):
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
            (Permissions.PROGRAMME_ACTIVATE,),
        ],
    )
    def test_grievance_ticket_global_list_without_permissions(
        self, permissions: list, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response_count = self.api_client.get(
            reverse(
                self.global_count_url,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response_count.status_code == status.HTTP_403_FORBIDDEN

    def test_grievance_ticket_global_list_check_non_program(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        GrievanceTicketFactory(
            description="Test 1",
            assigned_to=self.user,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            business_area=self.afghanistan,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 10

        response_count = self.api_client.get(
            reverse(
                self.global_count_url,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 10

    def test_grievance_ticket_global_list_area_limits(
        self,
        create_user_role_with_permissions: Any,
        set_admin_area_limits_in_program: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        set_admin_area_limits_in_program(self.partner, self.program_afghanistan1, [self.area1])
        set_admin_area_limits_in_program(self.partner, self.program_afghanistan2, [self.area2])

        # Only grievance tickets with area1 in program1 and area2 in program2 should be returned.

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 7

        result_ids = [result["id"] for result in response_results]
        assert str(self.grievance_tickets[0].id) in result_ids  # program1, area1
        assert str(self.grievance_tickets[1].id) not in result_ids  # program2, area1
        assert str(self.grievance_tickets[2].id) not in result_ids  # program1, area2
        assert str(self.grievance_tickets[3].id) in result_ids  # program2, area2
        assert str(self.grievance_tickets[4].id) in result_ids  # program1, area1
        assert str(self.grievance_tickets[5].id) in result_ids  # program2, area2
        assert str(self.grievance_tickets[6].id) in result_ids  # program1, area None
        assert str(self.grievance_tickets[7].id) in result_ids  # program2, area None
        assert str(self.grievance_tickets[8].id) in result_ids  # program1, area1

    def test_grievance_ticket_global_list_with_permissions_in_one_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            program=self.program_afghanistan1,
        )

        # Only grievance tickets in program1 should be returned.

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 5

        result_ids = [result["id"] for result in response_results]
        assert str(self.grievance_tickets[0].id) in result_ids
        assert str(self.grievance_tickets[1].id) not in result_ids
        assert str(self.grievance_tickets[2].id) in result_ids
        assert str(self.grievance_tickets[3].id) not in result_ids
        assert str(self.grievance_tickets[4].id) in result_ids
        assert str(self.grievance_tickets[5].id) not in result_ids
        assert str(self.grievance_tickets[6].id) in result_ids
        assert str(self.grievance_tickets[7].id) not in result_ids
        assert str(self.grievance_tickets[8].id) in result_ids

    @pytest.mark.parametrize(
        ("permissions", "program", "area_limit", "expected_tickets"),
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
        self,
        permissions: list,
        program: int,
        area_limit: bool,
        expected_tickets: list,
        create_user_role_with_permissions: Callable,
        set_admin_area_limits_in_program: Callable,
    ) -> None:
        program = self.program_afghanistan1 if program == 1 else self.program_afghanistan2
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=program,
        )
        if area_limit:
            set_admin_area_limits_in_program(self.partner, program, [self.area1])

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == len(expected_tickets)

        response_count = self.api_client.get(
            reverse(
                self.global_count_url,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == len(expected_tickets)

        result_ids = [result["id"] for result in response_results]
        for i in expected_tickets:
            assert str(self.grievance_tickets[i].id) in result_ids

    def test_all_edit_household_fields_attributes(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_CREATE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        url = "api:grievance-tickets:grievance-tickets-global-all-edit-household-fields-attributes"
        response = self.api_client.get(reverse(url, kwargs={"business_area_slug": self.afghanistan.slug}))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 39

    def test_all_edit_people_fields_attributes(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_CREATE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-all-edit-people-fields-attributes",
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 43

    def test_all_add_individuals_fields_attributes(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_CREATE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-all-add-individuals-fields-attributes",
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 30


class TestGrievanceTicketOfficeSearch:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.global_url_name = "api:grievance:grievance-tickets-global-list"
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program.cycles.first()

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.household1, self.individuals1 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.household2, self.individuals2 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.household3, self.individuals3 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.program_cycle = ProgramCycleFactory(program=self.program)
        self.payment_plan = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.program_cycle,
        )
        self.payment = PaymentFactory(
            parent=self.payment_plan,
            household=self.household1,
            head_of_household=self.individuals1[0],
            program=self.program,
        )

        self.complaint_ticket1 = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        )
        self.complaint_details1 = GrievanceComplaintTicketWithoutExtrasFactory(
            ticket=self.complaint_ticket1,
            household=self.household1,
            individual=self.individuals1[0],
            payment=None,
        )
        self.complaint_ticket1.programs.add(self.program)

        self.sensitive_ticket2 = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        )
        self.sensitive_details2 = SensitiveGrievanceTicketWithoutExtrasFactory(
            ticket=self.sensitive_ticket2,
            household=self.household2,
            individual=self.individuals2[0],
            payment=None,
        )
        self.complaint_ticket1.programs.add(self.program)

        self.complaint_ticket3 = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        )
        self.complaint_details3 = GrievanceComplaintTicketWithoutExtrasFactory(
            ticket=self.complaint_ticket3,
            household=self.household3,
            individual=self.individuals3[0],
            payment=self.payment,
        )
        self.complaint_ticket3.programs.add(self.program)

        self.needs_adjudication_ticket = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        )
        self.needs_adjudication_details = TicketNeedsAdjudicationDetails.objects.create(
            ticket=self.needs_adjudication_ticket,
            golden_records_individual=self.individuals1[0],
        )
        self.needs_adjudication_details.possible_duplicates.add(self.individuals2[1])
        self.needs_adjudication_ticket.programs.add(self.program)

        self.delete_individual_ticket = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
        )
        self.delete_individual_details = TicketDeleteIndividualDetailsFactory(
            ticket=self.delete_individual_ticket,
            individual=self.individuals3[1],
        )
        self.delete_individual_ticket.programs.add(self.program)

        self.household4, self.individuals4 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}],
        )

        self.delete_household_ticket = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
        )
        self.delete_household_details = TicketDeleteHouseholdDetailsFactory(
            ticket=self.delete_household_ticket,
            household=self.household4,
        )
        self.delete_household_ticket.programs.add(self.program)

        self.sanction_list_individual = SanctionListIndividualFactory()

        self.system_flagging_ticket = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        )
        self.system_flagging_details = TicketSystemFlaggingDetailsFactory(
            ticket=self.system_flagging_ticket,
            golden_records_individual=self.individuals1[1],
            sanction_list_individual=self.sanction_list_individual,
        )
        self.system_flagging_ticket.programs.add(self.program)

        self.household5, self.individuals5 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}],
        )

        self.payment_plan2 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.program_cycle,
        )
        self.payment2 = PaymentFactory(
            parent=self.payment_plan2,
            household=self.household5,
            head_of_household=self.individuals5[0],
            program=self.program,
        )
        PaymentVerificationSummaryFactory(payment_plan=self.payment_plan2)
        self.payment_verification_plan = PaymentVerificationPlanFactory(
            payment_plan=self.payment_plan2,
        )
        self.payment_verification = PaymentVerificationFactory(
            payment=self.payment2,
            payment_verification_plan=self.payment_verification_plan,
        )

        self.payment_verification_ticket = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
        )
        self.payment_verification_details = TicketPaymentVerificationDetailsFactory(
            ticket=self.payment_verification_ticket,
            payment_verification=self.payment_verification,
        )
        self.payment_verification_ticket.programs.add(self.program)

    def test_search_by_grievance_ticket_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        self.complaint_ticket1.refresh_from_db()
        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.complaint_ticket1.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.complaint_ticket1.id)

    def test_search_by_household_unicef_id_complaint_ticket(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household1.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.complaint_ticket1.id) in result_ids

    def test_search_by_household_unicef_id_sensitive_ticket(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household2.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.sensitive_ticket2.id)

    def test_search_by_individual_unicef_id_sensitive_ticket(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.individuals2[0].unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.sensitive_ticket2.id)

    def test_search_by_delete_individual_ticket_details(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.individuals3[1].unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.delete_individual_ticket.id)

    def test_search_by_delete_individual_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Search by household of the individual being deleted
        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household3.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.delete_individual_ticket.id) in result_ids

    def test_search_by_payment_verification_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.individuals5[0].unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment_verification_ticket.id)

    def test_search_by_payment_verification_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household5.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment_verification_ticket.id)

    def test_search_by_household_unicef_id_multiple_tickets(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household1.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.complaint_ticket1.id) in result_ids
        assert str(self.needs_adjudication_ticket.id) in result_ids
        assert str(self.system_flagging_ticket.id) in result_ids

    def test_search_by_individual_unicef_id_multiple_tickets(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.individuals1[0].unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.needs_adjudication_ticket.id) in result_ids
        assert str(self.complaint_ticket1.id) in result_ids

    def test_search_by_possible_duplicates_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.individuals2[1].unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.needs_adjudication_ticket.id)

    def test_search_by_needs_adjudication_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household1.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.needs_adjudication_ticket.id) in result_ids

    def test_search_by_payment_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        self.complaint_ticket3.refresh_from_db()
        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.payment.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.complaint_ticket3.id)

    def test_search_by_system_flagging_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.individuals1[1].unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.system_flagging_ticket.id)

    def test_search_by_system_flagging_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household1.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.system_flagging_ticket.id) in result_ids
        assert str(self.complaint_ticket1.id) in result_ids

    def test_search_by_delete_household_ticket(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household4.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.delete_household_ticket.id)

    def test_search_by_phone_number(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Update individual with phone number
        self.individuals1[0].phone_no = "+1234567890"
        self.individuals1[0].save()

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "+1234567890"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.complaint_ticket1.id) in result_ids
        assert str(self.needs_adjudication_ticket.id) in result_ids

    def test_search_by_phone_number_alternative(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Update individual with alternative phone number
        self.individuals2[0].phone_no_alternative = "+9876543210"
        self.individuals2[0].save()

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "+9876543210"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.sensitive_ticket2.id)

    def test_search_by_individual_name(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Update individual with specific name
        self.individuals3[0].full_name = "UniqueGrievanceName"
        self.individuals3[0].save()

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "UniqueGrievanceName"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.complaint_ticket3.id)

    def test_search_with_active_programs_filter(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        finished_program = ProgramFactory(business_area=self.afghanistan, status=Program.FINISHED)
        finished_household, finished_individuals = create_household_and_individuals(
            household_data={
                "program": finished_program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}],
        )

        finished_ticket = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
        )
        finished_ticket.programs.add(finished_program)
        GrievanceComplaintTicketWithoutExtrasFactory(
            ticket=finished_ticket,
            household=finished_household,
            individual=finished_individuals[0],
            payment=None,
        )

        # Set same phone number for both active and finished program individuals
        self.individuals1[0].phone_no = "+5557778888"
        self.individuals1[0].save()

        finished_individuals[0].phone_no = "+5557778888"
        finished_individuals[0].save()

        # First, search WITHOUT active_programs filter - should return 3 grievances (2 active, 1 finished)
        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "+5557778888", "active_programs_only": "false"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.complaint_ticket1.id) in result_ids
        assert str(self.needs_adjudication_ticket.id) in result_ids
        assert str(finished_ticket.id) in result_ids

        # Now search WITH active_programs_only filter - should only return active program grievances
        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "+5557778888", "active_programs_only": "true"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert str(self.complaint_ticket1.id) in result_ids
        assert str(self.needs_adjudication_ticket.id) in result_ids
