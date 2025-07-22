from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.grievance.models import GrievanceTicket

APPROVE_NEEDS_ADJUDICATION_MUTATION = """
    mutation ApproveNeedsAdjudication(
      $grievanceTicketId: ID!
      $selectedIndividualId: ID
      $duplicateIndividualIds: [ID]
      $clearIndividualIds: [ID]
    ) {
      approveNeedsAdjudication(
        grievanceTicketId: $grievanceTicketId
        selectedIndividualId: $selectedIndividualId
        duplicateIndividualIds: $duplicateIndividualIds
        clearIndividualIds: $clearIndividualIds
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
        super().setUpTestData()
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
            {"size": 1, "business_area": cls.business_area, "admin2": cls.doshi, "program": cls.program},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )

        _, cls.individuals_2 = create_household(
            {"size": 1, "business_area": cls.business_area, "admin2": cls.burka, "program": cls.program},
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
                "duplicateIndividualIds": [
                    encode_id_base64(self.individuals_1[0].id, "IndividualNode")  # guy from doshi admin2
                ],
            },
        )

    def test_close_ticket_when_partner_is_unicef(self) -> None:
        partner = PartnerFactory()

        self.user.partner = partner
        self.user.save()

        self.ticket_details.selected_individuals.add(self.individuals_2[0])  # burka guy, but can be anyone
        self.ticket_details.selected_distinct.add(self.individuals_1[0])

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
        self.update_partner_access_to_program(partner, self.program, [self.doshi])

        self.user.partner = partner
        self.user.save()

        self.individuals_1[0].program = self.program
        self.individuals_1[0].save()

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
                "duplicateIndividualIds": [
                    encode_id_base64(self.individuals_1[0].id, "IndividualNode")  # guy from doshi admin2
                ],
            },
        )

    def test_select_individual_when_partner_with_permission_with_selectedIndividualId(self) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        self.update_partner_access_to_program(partner, self.program, [self.doshi])

        self.user.partner = partner
        self.user.save()

        self.individuals_1[0].program = self.program
        self.individuals_1[0].save()

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
                "selectedIndividualId": encode_id_base64(
                    self.individuals_1[0].id, "IndividualNode"
                ),  # guy from doshi admin2
            },
        )

    def test_select_individual_when_partner_with_permission_with_selectedIndividualId_incorrect(self) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        self.update_partner_access_to_program(partner, self.program, [self.doshi])

        self.user.partner = partner
        self.user.save()

        self.individuals_1[0].program = self.program
        self.individuals_1[0].save()

        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
            ],
            self.business_area,
        )

        _, individuals = create_household(
            {"size": 1, "business_area": self.business_area, "admin2": self.doshi, "program": self.program},
            {"given_name": "Tester", "family_name": "Test", "middle_name": "", "full_name": "Tester Test"},
        )
        individuals[0].unicef_id = "IND-111"
        individuals[0].save()

        self.ticket_details.selected_individuals.add(self.individuals_1[0], individuals[0])  # doshi guy

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
                "selectedIndividualId": encode_id_base64(
                    individuals[0].id, "IndividualNode"
                ),  # individual that is not in the ticket
            },
        )

    def test_select_individual_when_partner_with_permission_with_selected_individual_and_selected_individuals(
        self,
    ) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        self.update_partner_access_to_program(partner, self.program, [self.doshi])

        self.user.partner = partner
        self.user.save()

        self.individuals_1[0].program = self.program
        self.individuals_1[0].save()

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
                "duplicateIndividualIds": [
                    encode_id_base64(self.individuals_1[0].id, "IndividualNode")  # guy from doshi admin2
                ],
                "selectedIndividualId": encode_id_base64(self.individuals_1[0].id, "IndividualNode"),
            },
        )

    def test_select_individual_when_partner_with_permission_and_no_selected_program(self) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        self.update_partner_access_to_program(partner, self.program, [self.doshi])

        self.user.partner = partner
        self.user.save()

        self.individuals_1[0].program = self.program
        self.individuals_1[0].save()

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
                    "Program": "all",
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "grievanceTicketId": encode_id_base64(self.grievance.id, "GrievanceTicketNode"),
                "duplicateIndividualIds": [
                    encode_id_base64(self.individuals_1[0].id, "IndividualNode")  # guy from doshi admin2
                ],
            },
        )

    def test_close_ticket_when_partner_with_permission(self) -> None:
        partner = PartnerFactory()
        self.update_partner_access_to_program(partner, self.program, [self.doshi])
        self.ticket_details.selected_distinct.add(self.individuals_1[0])
        self.ticket_details.selected_individuals.add(self.individuals_2[0])

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

    def test_close_ticket_when_partner_with_permission_and_no_selected_program(self) -> None:
        partner = PartnerFactory()
        self.update_partner_access_to_program(partner, self.program, [self.doshi])
        self.ticket_details.selected_distinct.add(self.individuals_2[0])
        self.ticket_details.selected_individuals.add(self.individuals_1[0])

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
                    "Program": "all",
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"grievanceTicketId": encode_id_base64(self.grievance.id, "GrievanceTicketNode"), "status": 6},
        )

    def test_select_individual_when_partner_does_not_have_permission(self) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        self.update_partner_access_to_program(partner, self.program, [self.doshi])

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
                "duplicateIndividualIds": [
                    encode_id_base64(self.individuals_2[0].id, "IndividualNode")  # guy from burka admin2
                ],
            },
        )

    def test_close_ticket_when_partner_does_not_have_permission(self) -> None:
        partner = PartnerFactory(name="NOT_UNICEF")
        self.update_partner_access_to_program(partner, self.program, [self.burka])
        self.user.partner = partner
        self.user.save()

        _, individuals_3 = create_household(
            {"size": 1, "business_area": self.business_area, "admin2": self.doshi},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )

        self.ticket_details.selected_individuals.add(self.individuals_1[0], individuals_3[0])  # doshi guy, should fail
        self.ticket_details.selected_distinct.add(self.individuals_2[0])
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
