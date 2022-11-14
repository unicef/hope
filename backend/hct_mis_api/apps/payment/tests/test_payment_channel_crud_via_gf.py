from hct_mis_api.apps.payment.fixtures import DeliveryMechanismFactory
from hct_mis_api.apps.payment.models import GenericPayment
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    PaymentChannelFactory,
)
from hct_mis_api.apps.payment.models import PaymentChannel


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

        cls.delivery_mechanism_1 = DeliveryMechanismFactory(
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_MOBILE_MONEY
        )
        cls.delivery_mechanism_2 = DeliveryMechanismFactory(delivery_mechanism=GenericPayment.DELIVERY_TYPE_CHEQUE)

        assert cls.individuals[0].payment_channels.count() == 0

    def create_individual_data_update_ticket(self, extras):
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
                    "extras": {"issueType": {"individualDataUpdateIssueTypeExtras": extras}},
                }
            },
        )
        assert "errors" not in create_response, create_response["errors"]
        return create_response

    def set_ticket_to_in_progress(self, encoded_grievance_ticket_id):
        in_progress_response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={"grievanceTicketId": encoded_grievance_ticket_id, "status": GrievanceTicket.STATUS_IN_PROGRESS},
        )
        assert "errors" not in in_progress_response, in_progress_response["errors"]

    def approve_ticket(self, encoded_grievance_ticket_id):
        approve_response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={"grievanceTicketId": encoded_grievance_ticket_id, "status": GrievanceTicket.STATUS_FOR_APPROVAL},
        )
        assert "errors" not in approve_response, approve_response["errors"]

    def close_ticket(self, encoded_grievance_ticket_id):
        close_response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={"grievanceTicketId": encoded_grievance_ticket_id, "status": GrievanceTicket.STATUS_CLOSED},
        )
        assert "errors" not in close_response, close_response["errors"]

    def test_crud_payment_channel_via_data_update(self):
        create_response = self.create_individual_data_update_ticket(
            extras={
                "individual": encode_id_base64(self.individuals[0].id, "Individual"),
                "individualData": {
                    "flexFields": {},
                    "paymentChannels": [
                        {"deliveryMechanism": encode_id_base64(self.delivery_mechanism_1.id, "DeliveryMechanism")}
                    ],
                },
            }
        )
        encoded_grievance_ticket_id = create_response["data"]["createGrievanceTicket"]["grievanceTickets"][0]["id"]

        self.set_ticket_to_in_progress(encoded_grievance_ticket_id)
        self.approve_ticket(encoded_grievance_ticket_id)

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

        self.close_ticket(encoded_grievance_ticket_id)

        self.individuals[0].refresh_from_db()
        assert self.individuals[0].payment_channels.count() == 1

    def test_editing_payment_channel_via_data_update(self):
        payment_channel = PaymentChannelFactory(
            individual=self.individuals[0], delivery_mechanism=self.delivery_mechanism_1
        )
        self.individuals[0].payment_channels.set([payment_channel])
        assert self.individuals[0].payment_channels.count() == 1
        assert self.individuals[0].payment_channels.first().delivery_mechanism == self.delivery_mechanism_1

        create_response = self.create_individual_data_update_ticket(
            extras={
                "individual": encode_id_base64(self.individuals[0].id, "Individual"),
                "individualData": {
                    "flexFields": {},
                    "paymentChannelsToEdit": [
                        {
                            "id": encode_id_base64(payment_channel.id, "PaymentChannel"),
                            "deliveryMechanism": encode_id_base64(self.delivery_mechanism_2.id, "DeliveryMechanism"),
                        }
                    ],
                },
            }
        )
        encoded_grievance_ticket_id = create_response["data"]["createGrievanceTicket"]["grievanceTickets"][0]["id"]

        self.set_ticket_to_in_progress(encoded_grievance_ticket_id)
        self.approve_ticket(encoded_grievance_ticket_id)

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
                "approvedPaymentChannelsToCreate": [],
                "approvedPaymentChannelsToRemove": [],
                "approvedPaymentChannelsToEdit": [0],
                "flexFieldsApproveData": "{}",
            },
        )
        assert "errors" not in approve_ind_data_change_response, approve_ind_data_change_response

        self.close_ticket(encoded_grievance_ticket_id)

        self.individuals[0].refresh_from_db()
        assert self.individuals[0].payment_channels.count() == 1
        assert self.individuals[0].payment_channels.first().delivery_mechanism == self.delivery_mechanism_2

    def test_deleting_payment_channel_via_data_update(self):
        payment_channel = PaymentChannelFactory(
            individual=self.individuals[0], delivery_mechanism=self.delivery_mechanism_1
        )
        self.individuals[0].payment_channels.set([payment_channel])
        assert self.individuals[0].payment_channels.count() == 1
        assert self.individuals[0].payment_channels.first().delivery_mechanism == self.delivery_mechanism_1

        create_response = self.create_individual_data_update_ticket(
            extras={
                "individual": encode_id_base64(self.individuals[0].id, "Individual"),
                "individualData": {
                    "flexFields": {},
                    "paymentChannelsToRemove": [encode_id_base64(payment_channel.id, "PaymentChannel")],
                },
            }
        )
        encoded_grievance_ticket_id = create_response["data"]["createGrievanceTicket"]["grievanceTickets"][0]["id"]

        self.set_ticket_to_in_progress(encoded_grievance_ticket_id)
        self.approve_ticket(encoded_grievance_ticket_id)

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
                "approvedPaymentChannelsToCreate": [],
                "approvedPaymentChannelsToRemove": [0],
                "approvedPaymentChannelsToEdit": [],
                "flexFieldsApproveData": "{}",
            },
        )
        assert "errors" not in approve_ind_data_change_response, approve_ind_data_change_response

        self.close_ticket(encoded_grievance_ticket_id)

        self.individuals[0].refresh_from_db()
        assert self.individuals[0].payment_channels.count() == 0


# TODO: add individual with payment channel
