from django.core.cache import cache

from extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough

FILTER_GRIEVANCE_BY_CROSS_AREA = """
query AllGrievanceTickets($isCrossArea: Boolean) {
  allGrievanceTicket(businessArea: "afghanistan", orderBy: "created_at", isCrossArea: $isCrossArea) {
    edges {
      node {
        status
        category
        admin
        language
        description
        consent
      }
    }
  }
}
"""


class TestCrossAreaFilter(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        partner_unicef = PartnerFactory(name="UNICEF")
        cls.user = UserFactory(partner=partner_unicef)

        RoleFactory(name="GRIEVANCES CROSS AREA FILTER", permissions=["GRIEVANCES_CROSS_AREA_FILTER"])
        # UserRole.objects.create(business_area=cls.business_area, user=cls.user, role=role)

        cls.admin_area1 = AreaFactory(name="Admin Area 1", level=2, p_code="AREA1")
        cls.admin_area2 = AreaFactory(name="Admin Area 2", level=2, p_code="AREA2")

        cls.program = ProgramFactory(business_area=cls.business_area, status=Program.ACTIVE)

        individual1_from_area1 = IndividualFactory(business_area=cls.business_area, household=None)
        individual2_from_area1 = IndividualFactory(business_area=cls.business_area, household=None)
        household1_from_area1 = HouseholdFactory(
            business_area=cls.business_area, admin2=cls.admin_area1, head_of_household=individual1_from_area1
        )
        individual1_from_area1.household = household1_from_area1
        individual1_from_area1.save()
        household2_from_area1 = HouseholdFactory(
            business_area=cls.business_area, admin2=cls.admin_area1, head_of_household=individual2_from_area1
        )
        individual2_from_area1.household = household2_from_area1
        individual2_from_area1.save()

        individual_from_area2 = IndividualFactory(business_area=cls.business_area, household=None)
        household_from_area2 = HouseholdFactory(
            business_area=cls.business_area, admin2=cls.admin_area2, head_of_household=individual_from_area2
        )
        individual_from_area2.household = household_from_area2
        individual_from_area2.save()

        grievance_ticket_cross_area = GrievanceTicketFactory(
            business_area=cls.business_area,
            language="Polish",
            consent=True,
            description="Cross Area Grievance",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            assigned_to=cls.user,
            admin2=cls.admin_area2,
        )
        grievance_ticket_cross_area.programs.set([cls.program])
        cls.needs_adjudication_ticket_cross_area = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1_from_area1,
            ticket=grievance_ticket_cross_area,
        )
        cls.needs_adjudication_ticket_cross_area.possible_duplicates.set([individual_from_area2])
        cls.needs_adjudication_ticket_cross_area.populate_cross_area_flag()

        grievance_ticket_same_area = GrievanceTicketFactory(
            business_area=cls.business_area,
            language="Polish",
            consent=True,
            description="Same Area Grievance",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            assigned_to=cls.user,
            admin2=cls.admin_area2,
        )
        grievance_ticket_same_area.programs.set([cls.program])
        cls.needs_adjudication_ticket_same_area = TicketNeedsAdjudicationDetailsFactory(
            golden_records_individual=individual1_from_area1,
            ticket=grievance_ticket_same_area,
        )
        cls.needs_adjudication_ticket_same_area.possible_duplicates.set([individual2_from_area1])
        cls.needs_adjudication_ticket_same_area.populate_cross_area_flag()

        # testing different access requirements
        cls.partner_without_area_restrictions = PartnerFactory(name="Partner without area restrictions")
        program_partner_through_without_area_restrictions = ProgramPartnerThrough.objects.create(
            program=cls.program, partner=cls.partner_without_area_restrictions
        )
        program_partner_through_without_area_restrictions.full_area_access = True
        program_partner_through_without_area_restrictions.save()
        cls.partner_with_area_restrictions = PartnerFactory(name="Partner with area restrictions")
        cls.update_partner_access_to_program(
            cls.partner_with_area_restrictions, cls.program, [cls.admin_area1, cls.admin_area2]
        )

    def test1_cross_area_filter_true_full_area_access_without_permission(self) -> None:
        cache.clear()
        user_without_permission = UserFactory(partner=self.partner_without_area_restrictions)
        self.create_user_role_with_permissions(
            user_without_permission,
            [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": user_without_permission,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": True},
        )

    def test1_cross_area_filter_true_full_area_access_with_permission(self) -> None:
        user_without_permission = UserFactory(partner=self.partner_without_area_restrictions)
        self.create_user_role_with_permissions(
            user_without_permission,
            [
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_CROSS_AREA_FILTER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": user_without_permission,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": True},
        )

    def test_cross_area_filter_true(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )

        self.needs_adjudication_ticket_cross_area.refresh_from_db()
        self.needs_adjudication_ticket_same_area.refresh_from_db()
        self.assertEqual(self.needs_adjudication_ticket_cross_area.is_cross_area, True)
        self.assertEqual(self.needs_adjudication_ticket_same_area.is_cross_area, False)

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": True},
        )

    def test_without_cross_area_filter(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE, Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": None},
        )

    def test_cross_area_filter_true_but_area_restrictions(self) -> None:
        cache.clear()
        user_with_area_restrictions = UserFactory(partner=self.partner_with_area_restrictions)
        self.create_user_role_with_permissions(
            user_with_area_restrictions,
            [
                Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_CROSS_AREA_FILTER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=FILTER_GRIEVANCE_BY_CROSS_AREA,
            context={
                "user": user_with_area_restrictions,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"isCrossArea": True},
        )
