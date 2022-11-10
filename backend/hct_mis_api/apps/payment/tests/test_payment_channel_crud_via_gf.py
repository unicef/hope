from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household


class TestPaymentChannelCRUD(APITestCase):
    CREATE_GRIEVANCE_MUTATION = """\
mutation CreateGrievance($input: CreateGrievanceTicketInput!) {
  createGrievanceTicket(input: $input) {
    grievanceTickets {
      id
      __typename
    }
    __typename
  }
}
"""

    UPDATE_GRIEVANCE_MUTATION = """\
mutation GrievanceTicketStatusChange($grievanceTicketId: ID, $status: Int) {
  grievanceStatusChange(grievanceTicketId: $grievanceTicketId, status: $status) {
    grievanceTicket {
      id
      __typename
    }
    __typename
  }
}
"""

    APPROVE_INDIVIDUAL_DATA_CHANGE_MUTATION = """\
mutation ApproveIndividualDataChange(
    $grievanceTicketId: ID!,
    $individualApproveData: JSONString,
    $flexFieldsApproveData: JSONString,
    $approvedDocumentsToCreate: [Int],
    $approvedDocumentsToRemove: [Int],
    $approvedDocumentsToEdit: [Int],
    $approvedIdentitiesToCreate: [Int],
    $approvedIdentitiesToEdit: [Int],
    $approvedIdentitiesToRemove: [Int],
    $approvedPaymentChannelsToCreate: [Int],
    $approvedPaymentChannelsToEdit: [Int],
    $approvedPaymentChannelsToRemove: [Int]) {
  approveIndividualDataChange(
      grievanceTicketId: $grievanceTicketId,
      individualApproveData: $individualApproveData,
      flexFieldsApproveData: $flexFieldsApproveData,
      approvedDocumentsToCreate: $approvedDocumentsToCreate,
      approvedDocumentsToRemove: $approvedDocumentsToRemove,
      approvedDocumentsToEdit: $approvedDocumentsToEdit,
      approvedIdentitiesToCreate: $approvedIdentitiesToCreate,
      approvedIdentitiesToEdit: $approvedIdentitiesToEdit,
      approvedIdentitiesToRemove: $approvedIdentitiesToRemove,
      approvedPaymentChannelsToCreate: $approvedPaymentChannelsToCreate,
      approvedPaymentChannelsToEdit: $approvedPaymentChannelsToEdit,
      approvedPaymentChannelsToRemove: $approvedPaymentChannelsToRemove) {
    grievanceTicket {
      id
      __typename
    }
    __typename
  }
}
"""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.business_area = BusinessAreaFactory(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            slug="afghanistan",
            has_data_sharing_agreement=True,
        )
        cls.household, cls.individuals = create_household(
            household_args={"size": 1, "business_area": cls.business_area},
        )

        cls.create_user_role_with_permissions(
            cls.user,
            [
                Permissions.GRIEVANCES_CREATE,
                Permissions.GRIEVANCES_UPDATE,
                Permissions.GRIEVANCES_SET_IN_PROGRESS,
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
                Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
            ],
            cls.business_area,
        )

    def test_creating_payment_channel(self):
        assert self.individuals[0].payment_channels.count() == 0

        create_response = self.graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    "businessArea": self.business_area.slug,
                    "description": "description",
                    "assignedTo": encode_id_base64(self.user.id, "User"),
                    "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
                    "consent": True,
                    "language": "",
                    "area": "",
                    "issueType": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
                    "linkedTickets": [],
                    "extras": {
                        "issueType": {
                            "individualDataUpdateIssueTypeExtras": {
                                "individual": encode_id_base64(self.individuals[0].id, "Individual"),
                                "individualData": {
                                    "flexFields": {},
                                    "paymentChannels": [
                                        {"bankName": "Test", "bankAccountNumber": "Test", "type": "BANK_TRANSFER"}
                                    ],
                                },
                            }
                        }
                    },
                }
            },
        )
        encoded_grievance_ticket_id = create_response["data"]["createGrievanceTicket"]["grievanceTickets"][0]["id"]

        in_progress_response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={"grievanceTicketId": encoded_grievance_ticket_id, "status": GrievanceTicket.STATUS_IN_PROGRESS},
        )
        assert "errors" not in in_progress_response, in_progress_response

        approve_response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={"grievanceTicketId": encoded_grievance_ticket_id, "status": GrievanceTicket.STATUS_FOR_APPROVAL},
        )
        assert "errors" not in approve_response, approve_response

        approve_ind_data_change_response = self.graphql_request(
            request_string=self.APPROVE_INDIVIDUAL_DATA_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": encoded_grievance_ticket_id,
                "individualApproveData": "{}",
                "approvedDocumentsToCreate": [],
                "approvedDocumentsToRemove": [],
                "approvedDocumentsToEdit": [],
                "approvedIdentitiesToCreate": [],
                "approvedIdentitiesToRemove": [],
                "approvedIdentitiesToEdit": [],
                "approvedPaymentChannelsToCreate": [0],
                "approvedPaymentChannelsToRemove": [],
                "approvedPaymentChannelsToEdit": [],
                "flexFieldsApproveData": "{}",
            },
        )
        assert "errors" not in approve_ind_data_change_response, approve_ind_data_change_response

        close_response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={"grievanceTicketId": encoded_grievance_ticket_id, "status": GrievanceTicket.STATUS_CLOSED},
        )
        assert "errors" not in close_response, close_response

        self.individuals[0].refresh_from_db()
        assert self.individuals[0].payment_channels.count() == 1


# test
# TODO close_add_individual_grievance_ticket update payment channel
