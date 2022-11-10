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

    def test_creating_payment_channel(self):
        # create grievance
        # status change in progress
        # approve
        # approve ind data change
        # close

        variables = {
            "input": {
                "businessArea": "afghanistan",
                "description": "asd",
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
        }
        response = self.graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )
        print(response)

        assert False
