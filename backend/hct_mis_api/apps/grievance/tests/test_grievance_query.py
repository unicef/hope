from datetime import datetime
from typing import Any, List
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.core.management import call_command
from django.utils import timezone

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


@patch("hct_mis_api.apps.core.es_filters.ElasticSearchFilterSet.USE_ALL_FIELDS_AS_POSTGRES_DB", True)
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
        create_afghanistan()
        call_command("loadcountries")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)
        country = Country.objects.first()
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
        cls.partner.permissions = {
            str(cls.business_area.pk): {
                "programs": {str(cls.program.id): [str(cls.admin_area_1.pk), str(cls.admin_area_2.pk)]},
                "roles": ["e9e8c91a-c711-45b7-be8c-501c14d46330"],
            }
        }
        cls.partner_2.permissions = {
            str(cls.business_area.pk): {
                "programs": {str(cls.program.id): [str(cls.admin_area_1.pk), str(cls.admin_area_2.pk)]},
                "roles": ["e9e8c91a-c711-45b7-be8c-501c14d46330"],
            }
        }
        cls.partner.save()
        cls.partner_2.save()
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
                    "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
                    "status": GrievanceTicket.STATUS_NEW,
                    "created_by": cls.user,
                    "assigned_to": cls.user,
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
        )

        cls.grievance_tickets[0].programs.add(cls.program)
        cls.grievance_tickets[1].programs.add(cls.program)
        cls.grievance_tickets[2].programs.add(cls.program)
        cls.grievance_tickets[3].programs.add(cls.program)

        # user with unicef partner
        partner_unicef = PartnerFactory(name="UNICEF")
        cls.user_with_unicef_partner = UserFactory(partner=partner_unicef, username="unicef_user")

        # user without access to program
        partner_perms = {
            str(cls.business_area.pk): {
                "roles": [],
                "programs": {},
            }
        }
        partner = PartnerFactory(name="Partner Without Program", permissions=partner_perms)
        cls.user_without_program = UserFactory(partner=partner, username="user_without_program")

        # user with full area access
        partner_perms = {
            str(cls.business_area.pk): {
                "roles": [],
                "programs": {str(cls.program.pk): []},
            }
        }
        partner = PartnerFactory(name="Partner With Full Area Access", permissions=partner_perms)
        cls.user_with_full_area_access = UserFactory(partner=partner, username="user_with_full_area_access")

        # user with access to admin area 1
        partner_perms = {
            str(cls.business_area.pk): {
                "roles": [],
                "programs": {str(cls.program.pk): [str(cls.admin_area_1.pk)]},
            }
        }
        partner = PartnerFactory(name="Partner With Admin Area 1 Access", permissions=partner_perms)
        cls.user_with_admin_area_1_access = UserFactory(partner=partner, username="user_with_admin_area_1_access")

        # user with access to admin area 2
        partner_perms = {
            str(cls.business_area.pk): {
                "roles": [],
                "programs": {str(cls.program.pk): [str(cls.admin_area_2.pk)]},
            }
        }
        partner = PartnerFactory(name="Partner With Admin Area 2 Access", permissions=partner_perms)
        cls.user_with_admin_area_2_access = UserFactory(partner=partner, username="user_with_admin_area_2_access")

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

    @pytest.mark.skip(reason="This test has never worked")
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

    @pytest.mark.skip(reason="This test has never worked")
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

    @pytest.mark.skip(reason="This test has never worked")
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
