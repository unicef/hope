from datetime import datetime
from typing import Any, Callable

from django.utils import timezone

import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db()


@freeze_time("2024-08-25 12:00:00")
class TestGrievanceTicketGlobalList:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Callable) -> None:
        self.afghanistan = create_afghanistan()
        self.program_afghanistan1 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )
        self.program_afghanistan2 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.FINISHED,
            name="program afghanistan 2",
        )

        self.list_global_url = reverse(
            "api:grievance:grievance-tickets-global-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        self.list_url = reverse(
            "api:grievance:grievance-tickets-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_afghanistan1.slug},
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.user2 = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

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

        self.country = CountryFactory()
        self.admin_type = AreaTypeFactory(country=self.country, area_level=1)
        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=self.admin_type)
        self.area2 = AreaFactory(parent=None, p_code="AF0101", area_type=self.admin_type)
        self.area2_2 = AreaFactory(parent=None, p_code="AF010101", area_type=self.admin_type)
        self.area_other = AreaFactory(parent=None, p_code="AF02", area_type=self.admin_type)

        created_at_dates_to_set = [
            timezone.make_aware(datetime(year=2020, month=3, day=12)),
            timezone.make_aware(datetime(year=2020, month=3, day=13)),
            timezone.make_aware(datetime(year=2020, month=3, day=14)),
            timezone.make_aware(datetime(year=2020, month=7, day=12)),
            timezone.make_aware(datetime(year=2020, month=8, day=22)),
            timezone.make_aware(datetime(year=2020, month=8, day=23)),
            timezone.make_aware(datetime(year=2020, month=8, day=24)),
            timezone.make_aware(datetime(year=2020, month=8, day=25)),
            timezone.make_aware(datetime(year=2020, month=8, day=26)),
        ]

        grievances_to_create = (
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2,
                    "language": "Polish",
                    "consent": True,
                    "description": "Needs Adjudication ticket, not cross area",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2_2,
                    "language": "Polish",
                    "consent": True,
                    "description": "Needs Adjudication ticket, cross area",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_CLOSED,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2,
                    "language": "Polish",
                    "consent": True,
                    "description": "Non-sensitive ticket with program, in admin area 1, owner",
                    "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": self.user2,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2,
                    "language": "English",
                    "consent": True,
                    "description": "Sensitive ticket with program, in admin area 2, on hold, owner and creator",
                    "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                    "status": GrievanceTicket.STATUS_ON_HOLD,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_DATA_BREACH,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area1,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Sensitive ticket with program, in admin area 2, in progress, owner",
                    "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user2,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area2,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Sensitive ticket with program, in admin area 2, in progress, creator",
                    "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user,
                    "assigned_to": self.user2,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_HARASSMENT,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": None,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Non-sensitive ticket with program, without admin area, creator and owner",
                    "category": GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": None,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Non-sensitive ticket without program, without admin area, creator and owner",
                    "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                    "issue_type": GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": self.afghanistan,
                    "admin2": self.area1,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Non-sensitive ticket without program, in admin area 1, creator and owner",
                    "category": GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
                    "status": GrievanceTicket.STATUS_CLOSED,
                    "created_by": self.user,
                    "assigned_to": self.user,
                    "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
                }
            ),
        )
        self.grievance_tickets = GrievanceTicket.objects.bulk_create(grievances_to_create)

        for date in created_at_dates_to_set:
            gts = GrievanceTicket.objects.all()
            for gt in gts:
                gt.created_at = date
                gt.save(update_fields=("created_at",))

        self.household1, self.individuals1 = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        self.household2, self.individuals2 = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2_2,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.needs_adjudication_ticket_not_cross_area = TicketNeedsAdjudicationDetails.objects.create(
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
        self.needs_adjudication_ticket_cross_area = TicketNeedsAdjudicationDetails.objects.create(
            ticket=self.grievance_tickets[1],
            golden_records_individual=self.individuals1[0],
            possible_duplicate=self.individuals2[0],
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
                        "hit_id": str(self.individuals2[0].pk),
                        "location": "location",
                        "proximity_to_score": "proximity_to_score",
                        "score": 2.0,
                        "duplicate": True,
                        "distinct": False,
                    }
                ],
            },
        )
        self.needs_adjudication_ticket_not_cross_area.possible_duplicates.set([self.individuals1[1]])
        self.needs_adjudication_ticket_cross_area.possible_duplicates.set([self.individuals2[0]])
        self.needs_adjudication_ticket_cross_area.populate_cross_area_flag()
        self.needs_adjudication_ticket_not_cross_area.populate_cross_area_flag()

        self.grievance_tickets[0].programs.add(self.program_afghanistan1)
        self.grievance_tickets[1].programs.add(self.program_afghanistan1)
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

    @pytest.mark.parametrize(
        "filter_value, expected_count",
        [
            ("system", 4),
            ("user", 5),
            ("", 9),
        ],
    )
    def test_filter_grievance_type(
        self,
        filter_value: bool,
        expected_count: int,
    ) -> None:
        response = self.api_client.get(self.list_global_url, {"grievance_type": filter_value})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count

    @pytest.mark.parametrize(
        "filter_value, expected_count",
        [
            ("active", 7),
            ("", 9),
        ],
    )
    def test_filter_grievance_status(
        self,
        filter_value: bool,
        expected_count: int,
    ) -> None:
        response = self.api_client.get(self.list_global_url, {"grievance_status": filter_value})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count

    @pytest.mark.parametrize(
        "filter_value, expected_count",
        [
            (True, 6),
            (False, 3),
        ],
    )
    def test_filter_program_status(
        self,
        filter_value: bool,
        expected_count: int,
    ) -> None:
        response = self.api_client.get(self.list_global_url, {"is_active_program": filter_value})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == expected_count

    @pytest.mark.parametrize(
        "has_cross_area_filter_permission, has_full_area_access, filter_value, is_filtered_for_program, is_filtered_for_global",
        [
            (False, False, False, False, False),
            (False, False, True, False, False),
            (False, True, True, False, False),
            (True, False, False, False, False),
            (True, False, True, False, True),
            (True, True, True, True, True),
        ],
    )
    def test_filter_by_cross_area(
        self,
        has_cross_area_filter_permission: list,
        has_full_area_access: int,
        filter_value: bool,
        is_filtered_for_program: bool,
        is_filtered_for_global: bool,
        create_user_role_with_permissions: Callable,
        set_admin_area_limits_in_program: Callable,
    ) -> None:
        if has_cross_area_filter_permission:
            create_user_role_with_permissions(
                user=self.user,
                permissions=[Permissions.GRIEVANCES_CROSS_AREA_FILTER],
                business_area=self.afghanistan,
                whole_business_area_access=True,
            )
        if not has_full_area_access:
            set_admin_area_limits_in_program(
                self.partner, self.program_afghanistan1, [self.area1, self.area2, self.area2_2]
            )

        response_for_program = self.api_client.get(
            self.list_url, {"is_cross_area": filter_value, "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION}
        )
        response_for_global = self.api_client.get(
            self.list_global_url,
            {"is_cross_area": filter_value, "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION},
        )

        for response, is_filtered in [
            (response_for_program, is_filtered_for_program),
            (response_for_global, is_filtered_for_global),
        ]:
            assert response.status_code == status.HTTP_200_OK
            if is_filtered:
                assert len(response.data["results"]) == 1
                assert response.data["results"][0]["id"] == str(self.grievance_tickets[1].id)
            else:
                assert len(response.data["results"]) == 2
                assert response.data["results"][0]["id"] == str(self.grievance_tickets[0].id)
                assert response.data["results"][1]["id"] == str(self.grievance_tickets[1].id)
