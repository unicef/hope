from typing import Any
from unittest.mock import patch

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory

APPROVE_NEEDS_ADJUDICATION_MUTATION = """
    mutation ApproveNeedsAdjudication(
      $grievanceTicketId: ID!
      $selectedIndividualId: ID
      $selectedIndividualIds: [ID]
    ) {
      approveNeedsAdjudication(
        grievanceTicketId: $grievanceTicketId
        selectedIndividualId: $selectedIndividualId
        selectedIndividualIds: $selectedIndividualIds
      ) {
        grievanceTicket {
          description
          status
          __typename
        }
        __typename
      }
    }
"""

GRIEVANCE_TICKET_STATUS_CHANGE = """
    mutation GrievanceTicketStatusChange($grievanceTicketId: ID, $status: Int) {
      grievanceStatusChange(
        grievanceTicketId: $grievanceTicketId
        status: $status
      ) {
        grievanceTicket {
          description
          status
          __typename
        }
        __typename
      }
    }
"""


class TestAdjudicationTicketPartnerPermission(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()

        cls.business_area = BusinessAreaFactory(slug="afghanistan")
        cls.program = ProgramFactory(business_area=cls.business_area)

        cls.grievance = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            description="GrievanceTicket",
        )
        cls.grievance.programs.add(cls.program)

        cls.area_type_level_1 = AreaTypeFactory(name="Province", area_level=1)
        cls.area_type_level_2 = AreaTypeFactory(name="District", area_level=2, parent=cls.area_type_level_1)

        cls.ghazni = AreaFactory(name="Ghazni", area_type=cls.area_type_level_1, p_code="area1")

        cls.doshi = AreaFactory(name="Doshi", area_type=cls.area_type_level_2, p_code="area2", parent=cls.ghazni)
        cls.burka = AreaFactory(name="Burka", area_type=cls.area_type_level_2, p_code="area3", parent=cls.ghazni)

        _, cls.individuals_1 = create_household(
            {"size": 1, "business_area": cls.business_area, "admin2": cls.doshi},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )

        cls.household_2, cls.individuals_2 = create_household(
            {"size": 1, "business_area": cls.business_area, "admin2": cls.burka},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )

        cls.ticket_details = TicketNeedsAdjudicationDetailsFactory(
            ticket=cls.grievance,
            golden_records_individual=cls.individuals_1[0],
            possible_duplicate=cls.individuals_2[0],
            is_multiple_duplicates_version=True,
            selected_individual=None,
        )

        cls.ticket_details.ticket = cls.grievance
        cls.ticket_details.save()

    def test_select_individual_when_partner_is_unicef(self) -> None:
        partner = PartnerFactory()

        self.user.partner = partner
        self.user.save()

        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=APPROVE_NEEDS_ADJUDICATION_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "grievanceTicketId": encode_id_base64(self.grievance.id, "GrievanceTicketNode"),
                "selectedIndividualIds": [
                    encode_id_base64(self.individuals_1[0].id, "IndividualNode")  # guy from doshi admin2
                ],
            },
        )

    def test_close_ticket_when_partner_is_unicef(self) -> None:
        partner = PartnerFactory()

        self.user.partner = partner
        self.user.save()

        self.ticket_details.selected_individuals.add(self.individuals_2[0])  # burka guy, but can be anyone

        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=GRIEVANCE_TICKET_STATUS_CHANGE,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"grievanceTicketId": encode_id_base64(self.grievance.id, "GrievanceTicketNode"), "status": 6},
        )

    def test_select_individual_when_partner_with_permission(self) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        partner.permissions = {str(self.business_area.id): {"programs": {str(self.program.id): [str(self.doshi.id)]}}}

        self.user.partner = partner
        self.user.save()

        self.ticket_details.selected_individuals.add(self.individuals_1[0])  # doshi guy

        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=APPROVE_NEEDS_ADJUDICATION_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "grievanceTicketId": encode_id_base64(self.grievance.id, "GrievanceTicketNode"),
                "selectedIndividualIds": [
                    encode_id_base64(self.individuals_1[0].id, "IndividualNode")  # guy from doshi admin2
                ],
            },
        )

    def test_close_ticket_when_partner_with_permission(self) -> None:
        partner = PartnerFactory()
        partner.permissions = {str(self.business_area.id): {"programs": {str(self.program.id): [str(self.doshi.id)]}}}

        self.user.partner = partner
        self.user.save()

        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=GRIEVANCE_TICKET_STATUS_CHANGE,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"grievanceTicketId": encode_id_base64(self.grievance.id, "GrievanceTicketNode"), "status": 6},
        )

    def test_select_individual_when_partner_does_not_have_permission(self) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        partner.permissions = {str(self.business_area.id): {"programs": {str(self.program.id): [str(self.doshi.id)]}}}

        self.user.partner = partner
        self.user.save()

        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=APPROVE_NEEDS_ADJUDICATION_MUTATION,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "grievanceTicketId": encode_id_base64(self.grievance.id, "GrievanceTicketNode"),
                "selectedIndividualIds": [
                    encode_id_base64(self.individuals_2[0].id, "IndividualNode")  # guy from burka admin2
                ],
            },
        )

    @patch(
        "hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services.mark_as_duplicate_individual_and_reassign_roles"
    )
    def test_close_ticket_when_partner_does_not_have_permission(self, mock: Any) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        partner.permissions = {str(self.business_area.id): {"programs": {str(self.program.id): [str(self.burka.id)]}}}

        self.ticket_details.selected_individuals.add(self.individuals_1[0])  # doshi guy, should fail

        self.user.partner = partner
        self.user.save()

        _, individuals_3 = create_household(
            {"size": 1, "business_area": self.business_area, "admin2": self.doshi},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )

        self.ticket_details.golden_records_individual = individuals_3[0]
        self.ticket_details.save()

        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
            ],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=GRIEVANCE_TICKET_STATUS_CHANGE,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"grievanceTicketId": encode_id_base64(self.grievance.id, "GrievanceTicketNode"), "status": 6},
        )
