from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.models import GrievanceTicket
from household.fixtures import create_household
from payment.fixtures import PaymentRecordFactory
from program.fixtures import ProgramFactory, CashPlanFactory


class TestGrievanceCreateComplaintTicketQuery(APITestCase):
    CREATE_GRIEVANCE_MUTATION = """
    mutation CreateGrievanceTicket($input: CreateGrievanceTicketInput!) {
      createGrievanceTicket(input: $input) {
        grievanceTickets{
          status
          category
          admin
          language
          description
          consent
          complaintTicketDetails {
            household {
              size
            }
            individual {
              fullName
            }
            paymentRecord {
              fullName
            }
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=self.business_area,)
        self.admin_area = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.household, self.individuals = create_household(
            {"size": 1, "business_area": self.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )
        program = ProgramFactory(business_area=self.business_area)
        cash_plan = CashPlanFactory(program=program, business_area=self.business_area)
        self.payment_record = PaymentRecordFactory(
            household=self.household,
            full_name=self.individuals[0].full_name,
            business_area=self.business_area,
            cash_plan=cash_plan,
        )

    def test_create_complaint_ticket(self):
        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                "admin": self.admin_area.title,
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "grievanceComplaintTicketExtras": {
                            "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                            "paymentRecord": self.id_to_base64(self.payment_record.id, "PaymentRecordNode"),
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION, context={"user": self.user}, variables=input_data,
        )

    def test_create_complaint_ticket_without_payment_record(self):
        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                "admin": self.admin_area.title,
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "grievanceComplaintTicketExtras": {
                            "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION, context={"user": self.user}, variables=input_data,
        )

    def test_create_complaint_ticket_without_household(self):
        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                "admin": self.admin_area.title,
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "grievanceComplaintTicketExtras": {
                            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                            "paymentRecord": self.id_to_base64(self.payment_record.id, "PaymentRecordNode"),
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION, context={"user": self.user}, variables=input_data,
        )

    def test_create_complaint_ticket_without_individual(self):
        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                "admin": self.admin_area.title,
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "grievanceComplaintTicketExtras": {
                            "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                            "paymentRecord": self.id_to_base64(self.payment_record.id, "PaymentRecordNode"),
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION, context={"user": self.user}, variables=input_data,
        )

    def test_create_complaint_ticket_without_extras(self):
        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                "admin": self.admin_area.title,
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION, context={"user": self.user}, variables=input_data,
        )
