from datetime import datetime
from typing import Any, List

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

import pytest
from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from tests.extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
    TicketSensitiveDetails,
)
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestGrievanceQuery(APITestCase):
    ALL_GRIEVANCE_QUERY = """
    query AllGrievanceTickets {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at") {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    ALL_GRIEVANCE_QUERY_FOR_PROGRAM = """
    query AllGrievanceTickets($program: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at",  program: $program) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_ADMIN_AREA = """
    query AllGrievanceTickets($admin: ID) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", admin2: $admin) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_CREATED_AT = """
    query AllGrievanceTickets($createdAtRange: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", createdAtRange: $createdAtRange) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_STATUS = """
    query AllGrievanceTickets($status: [String]) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", status: $status) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    GRIEVANCE_QUERY = """
    query GrievanceTicket($id: ID!) {
      grievanceTicket(id: $id) {
        status
        category
        admin
        language
        description
        consent
        createdAt
      }
    }
    """

    FILTER_BY_CATEGORY = """
    query AllGrievanceTickets($category: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "-created_at", category: $category) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_ASSIGNED_TO = """
    query AllGrievanceTickets($assignedTo: ID) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", assignedTo: $assignedTo) {
        edges {
          node {
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    FILTER_BY_SCORE = """
    query AllGrievanceTickets($scoreMin: String, $scoreMax: String) {
      allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", scoreMax: $scoreMax, scoreMin: $scoreMin) {
        edges {
          node {
            needsAdjudicationTicketDetails {
              scoreMin
              scoreMax
              selectedDistinct {
                duplicate
              }
              extraData{
                goldenRecords {
                  fullName
                  score
                  duplicate
                  distinct
                }
                possibleDuplicate {
                  fullName
                  score
                  duplicate
                  distinct
                }
              }
            }
            status
            category
            admin
            language
            description
            consent
            createdAt
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)
        country = CountryFactory(name="Afghanistan")
        country.business_areas.set([cls.business_area])
        area_type = AreaTypeFactory(
            name="Admin type one",
            area_level=2,
            country=country,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="123aa123")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="sadasdasfd222")

        cls.partner = PartnerFactory(name="Partner1")
        cls.partner_2 = PartnerFactory(name="Partner2")
        # update partner perms
        role = RoleFactory(name="Partner Role", permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS])
        cls.update_partner_access_to_program(
            cls.partner,
            cls.program,
            [cls.admin_area_1, cls.admin_area_2],
        )
        cls.add_partner_role_in_business_area(
            cls.partner,
            cls.business_area,
            [role],
        )
        cls.update_partner_access_to_program(
            cls.partner_2,
            cls.program,
            [cls.admin_area_1, cls.admin_area_2],
        )
        cls.add_partner_role_in_business_area(
            cls.partner_2,
            cls.business_area,
            [role],
        )
        cls.user = UserFactory.create(partner=cls.partner)
        cls.user2 = UserFactory.create(partner=cls.partner_2)

        _, individuals = create_household({"size": 2})
        cls.individual_1 = individuals[0]
        cls.individual_2 = individuals[1]

        created_at_dates_to_set = {
            GrievanceTicket.STATUS_NEW: [timezone.make_aware(datetime(year=2020, month=3, day=12))],
            GrievanceTicket.STATUS_ON_HOLD: [timezone.make_aware(datetime(year=2020, month=7, day=12))],
            GrievanceTicket.STATUS_IN_PROGRESS: [
                timezone.make_aware(datetime(year=2020, month=8, day=22)),
                timezone.make_aware(datetime(year=2020, month=8, day=23)),
                timezone.make_aware(datetime(year=2020, month=8, day=24)),
                timezone.make_aware(datetime(year=2020, month=8, day=25)),
            ],
        }

        grievances_to_create = (
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_1,
                    "language": "Polish",
                    "consent": True,
                    "description": "Ticket with program, in admin area 1, new",
                    "category": GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                    "issue_type": GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_2,
                    "language": "English",
                    "consent": True,
                    "description": "Ticket with program, in admin area 2, on hold",
                    "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_ON_HOLD,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_2,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Ticket with program, in admin area 2, in progress",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": None,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Ticket with program, without admin area",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": None,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Ticket without program, without admin area",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
            GrievanceTicket(
                **{
                    "business_area": cls.business_area,
                    "admin2": cls.admin_area_1,
                    "language": "Polish, English",
                    "consent": True,
                    "description": "Ticket without program, in admin area 1",
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_IN_PROGRESS,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
                }
            ),
        )
        cls.grievance_tickets = GrievanceTicket.objects.bulk_create(grievances_to_create)

        for status, dates in created_at_dates_to_set.items():
            gts = GrievanceTicket.objects.filter(status=status)
            for gt in gts:
                gt.created_at = dates.pop(0)
                gt.save(update_fields=("created_at",))

        TicketNeedsAdjudicationDetails.objects.create(
            ticket=GrievanceTicket.objects.first(),
            golden_records_individual=cls.individual_1,
            possible_duplicate=cls.individual_2,
            score_min=100,
            score_max=150,
            extra_data={
                "golden_records": [
                    {
                        "dob": "date_of_birth",
                        "full_name": "full_name",
                        "hit_id": str(cls.individual_1.pk),
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
                        "hit_id": str(cls.individual_2.pk),
                        "location": "location",
                        "proximity_to_score": "proximity_to_score",
                        "score": 2.0,
                        "duplicate": True,
                        "distinct": False,
                    }
                ],
            },
        )

        cls.grievance_tickets[0].programs.add(cls.program)
        cls.grievance_tickets[1].programs.add(cls.program)
        cls.grievance_tickets[2].programs.add(cls.program)
        cls.grievance_tickets[3].programs.add(cls.program)

        # user with unicef partner
        partner_unicef = PartnerFactory(name="UNICEF")
        cls.user_with_unicef_partner = UserFactory(partner=partner_unicef, username="unicef_user")

        # user without access to program
        partner_without_program = PartnerFactory(name="Partner Without Program")
        cls.user_without_program = UserFactory(partner=partner_without_program, username="user_without_program")

        # user with full area access
        partner_with_full_area_access = PartnerFactory(name="Partner With Full Area Access")
        cls.update_partner_access_to_program(
            partner_with_full_area_access,
            cls.program,
            full_area_access=True,
        )
        cls.user_with_full_area_access = UserFactory(
            partner=partner_with_full_area_access, username="user_with_full_area_access"
        )

        # user with access to admin area 1
        partner_with_admin_area1_access = PartnerFactory(name="Partner With Admin Area 1 Access")
        cls.update_partner_access_to_program(
            partner_with_admin_area1_access,
            cls.program,
            [cls.admin_area_1],
        )
        cls.user_with_admin_area_1_access = UserFactory(
            partner=partner_with_admin_area1_access, username="user_with_admin_area_1_access"
        )

        # user with access to admin area 2
        partner_with_admin_area2_access = PartnerFactory(name="Partner With Admin Area 2 Access")
        cls.update_partner_access_to_program(
            partner_with_admin_area2_access,
            cls.program,
            [cls.admin_area_2],
        )
        cls.user_with_admin_area_2_access = UserFactory(
            partner=partner_with_admin_area2_access, username="user_with_admin_area_2_access"
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            ),
            ("without_permission", []),
        ]
    )
    def test_grievance_query_all(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)
        cache.clear()
        self.snapshot_graphql_request(
            request_string=self.ALL_GRIEVANCE_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR]),
            ("without_permission", []),
        ]
    )
    def test_grievance_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

        gt_id = GrievanceTicket.objects.get(description="Ticket with program, in admin area 2, in progress").id
        self.snapshot_graphql_request(
            request_string=self.GRIEVANCE_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(gt_id, "GrievanceTicketNode")},
        )

    def test_grievance_ticket_query_partner_access_detail_partner_unicef_for_program(self) -> None:
        # access to ticket detail of every program-related ticket in this BA (through specific Program)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_program(self.user_with_unicef_partner)

    def test_grievance_ticket_query_partner_access_detail_partner_unicef_for_all_programs(self) -> None:
        # access to ticket detail of every ticket in this BA (through All Programs)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_all_programs(self.user_with_unicef_partner)

    def test_grievance_ticket_query_partner_access_detail_partner_without_program_for_program(self) -> None:
        # no access to any ticket detail (through specific Program)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_program(self.user_without_program)

    def test_grievance_ticket_query_partner_access_detail_partner_without_program_for_all_programs(self) -> None:
        # access to ticket detail of non-program tickets (through All Programs)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_all_programs(self.user_without_program)

    def test_grievance_ticket_query_partner_access_detail_partner_with_full_area_access_for_program(self) -> None:
        # access to program-related ticket detail of tickets in this BA (through specific Program)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_program(self.user_with_full_area_access)

    def test_grievance_ticket_query_partner_access_detail_partner_with_full_area_access_for_all_programs(self) -> None:
        # access to ticket detail of every ticket in this BA (through All Programs)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_all_programs(
            self.user_with_full_area_access
        )

    def test_grievance_ticket_query_partner_access_detail_partner_with_admin_area_1_access_for_program(self) -> None:
        # access to program-related ticket detail of tickets without admin area or with admin_area_1
        # (through specific Program)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_program(self.user_with_admin_area_1_access)

    def test_grievance_ticket_query_partner_access_detail_partner_with_admin_area_1_access_for_all_programs(
        self,
    ) -> None:
        # access to ticket detail of non-program tickets or tickets without admin area or with admin_area_1
        # (through All Programs)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_all_programs(
            self.user_with_admin_area_1_access
        )

    def test_grievance_ticket_query_partner_access_detail_partner_with_admin_area_2_access_for_program(self) -> None:
        # access to program-related ticket detail of tickets without admin area or with admin_area_1
        # (through specific Program)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_program(self.user_with_admin_area_2_access)

    def test_grievance_ticket_query_partner_access_detail_partner_with_admin_area_2_access_for_all_programs(
        self,
    ) -> None:
        # access to ticket detail of non-program tickets or tickets without admin area or with admin_area_1
        # (through All Programs)
        self._test_grievance_ticket_query_partner_access_detail_for_user_for_all_programs(
            self.user_with_admin_area_2_access
        )

    def _test_grievance_ticket_query_partner_access_detail_for_user_for_program(self, user: User) -> None:
        self.create_user_role_with_permissions(
            user,
            [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            self.business_area,
        )
        for ticket in self.grievance_tickets:
            self.snapshot_graphql_request(
                request_string=self.GRIEVANCE_QUERY,
                context={
                    "user": user,
                    "headers": {
                        "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                        "Business-Area": self.business_area.slug,
                    },
                },
                variables={"id": self.id_to_base64(ticket.id, "GrievanceTicketNode")},
            )

    def _test_grievance_ticket_query_partner_access_detail_for_user_for_all_programs(self, user: User) -> None:
        self.create_user_role_with_permissions(
            user,
            [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
            self.business_area,
        )
        for ticket in self.grievance_tickets:
            self.snapshot_graphql_request(
                request_string=self.GRIEVANCE_QUERY,
                context={
                    "user": user,
                    "headers": {
                        "Program": "all",
                        "Business-Area": self.business_area.slug,
                    },
                },
                variables={"id": self.id_to_base64(ticket.id, "GrievanceTicketNode")},
            )

    @pytest.mark.skip(reason="This test has never worked with pytest")
    def test_grievance_ticket_query_partner_access_list_partner_unicef_for_program(self) -> None:
        # list of all program-related tickets in this BA (through specific Program)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_program(self.user_with_unicef_partner)

    def test_grievance_ticket_query_partner_access_list_partner_unicef_for_all_programs(self) -> None:
        # list of all tickets in this BA (through All Programs)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_all_programs(self.user_with_unicef_partner)

    def test_grievance_ticket_query_partner_access_list_partner_without_program_for_program(self) -> None:
        # permission denied (through specific Program)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_program(self.user_without_program)

    def test_grievance_ticket_query_partner_access_list_partner_without_program_for_all_programs(self) -> None:
        # list of non-program tickets (through All Programs)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_all_programs(self.user_without_program)

    @pytest.mark.skip(reason="This test has never worked with pytest")
    def test_grievance_ticket_query_partner_access_list_partner_with_full_area_access_for_program(self) -> None:
        # list of all program-related tickets in this BA (through specific Program)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_program(self.user_with_full_area_access)

    def test_grievance_ticket_query_partner_access_list_partner_with_full_area_access_for_all_programs(self) -> None:
        # list of all tickets in this BA (through All Programs)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_all_programs(self.user_with_full_area_access)

    def test_grievance_ticket_query_partner_access_list_partner_with_admin_area_1_access_for_program(self) -> None:
        # list of program-related tickets without admin area or with admin_area_1 (through specific Program)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_program(self.user_with_admin_area_1_access)

    def test_grievance_ticket_query_partner_access_list_partner_with_admin_area_1_access_for_all_programs(self) -> None:
        # list of tickets without program and tickets without admin area or with admin_area_1 (through All Programs)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_all_programs(
            self.user_with_admin_area_1_access
        )

    @pytest.mark.skip(reason="This test has never worked with pytest")
    def test_grievance_ticket_query_partner_access_list_partner_with_admin_area_2_access_for_program(self) -> None:
        # list of program-related tickets without admin area or with admin_area_2 (through specific Program)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_program(self.user_with_admin_area_2_access)

    def test_grievance_ticket_query_partner_access_list_partner_with_admin_area_2_access_for_all_programs(self) -> None:
        # list of tickets without program and tickets without admin area or with admin_area_2 (through All Programs)
        self._test_grievance_ticket_query_partner_access_list_for_user_for_all_programs(
            self.user_with_admin_area_2_access
        )

    def _test_grievance_ticket_query_partner_access_list_for_user_for_program(self, user: User) -> None:
        self.create_user_role_with_permissions(
            user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )
        self.snapshot_graphql_request(
            request_string=self.ALL_GRIEVANCE_QUERY_FOR_PROGRAM,
            context={
                "user": user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"program": self.id_to_base64(self.program.id, "ProgramNode")},
        )

    def _test_grievance_ticket_query_partner_access_list_for_user_for_all_programs(self, user: User) -> None:
        self.create_user_role_with_permissions(
            user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )
        cache.clear()
        self.snapshot_graphql_request(
            request_string=self.ALL_GRIEVANCE_QUERY,
            context={
                "user": user,
                "headers": {
                    "Program": "all",
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    def test_grievance_list_filtered_by_admin2(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ADMIN_AREA,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"admin": self.id_to_base64(self.admin_area_1.id, "GrievanceTicketNode")},
        )

    def test_grievance_list_filtered_by_created_at(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CREATED_AT,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"createdAtRange": '{"min": "2020-07-12", "max": "2020-09-12"}'},
        )

    def test_grievance_list_filtered_by_status(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_STATUS,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"status": [str(GrievanceTicket.STATUS_IN_PROGRESS)]},
        )

    @parameterized.expand(
        [
            (
                "category_positive_feedback",
                GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            ),
            (
                "category_negative_feedback",
                GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            ),
        ]
    )
    def test_grievance_list_filtered_by_category(self, _: Any, category: str) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_CATEGORY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"category": str(category)},
        )

    def test_grievance_list_filtered_by_assigned_to_correct_user(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ASSIGNED_TO,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"assignedTo": self.id_to_base64(self.user.id, "UserNode")},
        )

    def test_grievance_list_filtered_by_assigned_to_incorrect_user(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_ASSIGNED_TO,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"assignedTo": self.id_to_base64(self.user2.id, "UserNode")},
        )

    def test_grievance_list_filtered_by_score(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SCORE,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"scoreMin": 100, "scoreMax": 200},
        )

        self.snapshot_graphql_request(
            request_string=self.FILTER_BY_SCORE,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"scoreMin": 900, "scoreMax": 999},
        )

    def test_people_upd_individual_data_admin_area_title(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR],
            self.business_area,
            self.program,
        )
        AreaFactory(p_code="AAA333", name="Test_Name")
        AreaFactory(p_code="A22", name="Old_Name")
        individual_data = {"admin_area_title": {"value": "AAA333", "approve_status": True, "previous_value": "A22"}}
        ticket = GrievanceTicket.objects.first()
        TicketIndividualDataUpdateDetailsFactory(
            ticket=ticket, individual_data=individual_data, individual=self.individual_1
        )
        self.snapshot_graphql_request(
            request_string="""
                query GrievanceTicket($id: ID!) {
                  grievanceTicket(id: $id) {
                    individualDataUpdateTicketDetails{
                      individualData
                    }
                  }
                }
                """,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(str(ticket.id), "GrievanceTicketNode")},
        )


class TestGrievanceNode(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.program = ProgramFactory(data_collecting_type__type=DataCollectingType.Type.STANDARD)
        cls.sw_program = ProgramFactory(data_collecting_type__type=DataCollectingType.Type.SOCIAL)
        cls.hh, individuals = create_household({"size": 1, "unicef_id": "HH-001-001"})
        cls.individual_1 = individuals[0]

        cls.grievance_sw_with_ind_in_details = GrievanceTicketFactory(
            household_unicef_id="HH-001-001",
        )
        cls.grievance_sw_with_ind_in_details.programs.set([cls.sw_program])
        cls.grievance_sw_without_ind_in_details = GrievanceTicketFactory(
            household_unicef_id=cls.hh.unicef_id,
        )
        cls.grievance_sw_without_ind_in_details.programs.set([cls.sw_program])
        cls.grievance_non_sw_program = GrievanceTicketFactory(
            household_unicef_id=cls.hh.unicef_id,
        )
        cls.grievance_non_sw_program.programs.set([cls.program])

    def test_get_target_id(self) -> None:
        TicketSensitiveDetails.objects.create(
            individual=self.individual_1,
            household=self.hh,
            ticket=self.grievance_sw_with_ind_in_details,
        )

        TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=self.individual_1, ticket=self.grievance_sw_without_ind_in_details
        )
        self.grievance_non_sw_program.refresh_from_db()
        self.grievance_sw_with_ind_in_details.refresh_from_db()
        self.grievance_sw_without_ind_in_details.refresh_from_db()

        # return HH_id
        self.assertEqual(self.grievance_non_sw_program.target_id, "HH-001-001")
        # return Ind_id
        self.assertEqual(self.grievance_sw_with_ind_in_details.target_id, self.individual_1.unicef_id)
        self.assertEqual(self.grievance_sw_without_ind_in_details.target_id, self.individual_1.unicef_id)
