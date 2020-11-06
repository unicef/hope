from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.fixtures import (
    GrievanceTicketFactory,
    GrievanceComplaintTicketFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory, SensitiveGrievanceTicketFactory,
)
from grievance.models import GrievanceTicket
from household.fixtures import create_household
from payment.fixtures import PaymentRecordFactory
from program.fixtures import ProgramFactory, CashPlanFactory


class TestAlreadyExistingFilterTickets(APITestCase):
    FILTER_EXISTING_GRIEVANCES_QUERY = """
    query ExistingGrievanceTickets(
      $businessArea: String!, 
      $category: String!, 
      $issueType: String, 
      $household: ID, 
      $individual: ID, 
      $paymentRecord: [ID]
    ) {
      existingGrievanceTickets(
        businessArea: $businessArea, 
        category: $category, 
        issueType: $issueType, 
        household: $household, 
        individual: $individual, 
        paymentRecord: $paymentRecord
      ) {
        edges {
          node {
            status
            category
            area
            sensitiveTicketDetails {
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
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=self.business_area)
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
        self.payment_record2 = PaymentRecordFactory(
            household=self.household,
            full_name=self.individuals[0].full_name,
            business_area=self.business_area,
            cash_plan=cash_plan,
        )
        GrievanceTicketFactory.create_batch(5)
        self.ticket = SensitiveGrievanceTicketWithoutExtrasFactory(
            household=self.household, individual=self.individuals[0], payment_record=self.payment_record
        )
        SensitiveGrievanceTicketWithoutExtrasFactory(household=self.household, individual=self.individuals[0])
        SensitiveGrievanceTicketWithoutExtrasFactory(
            household=self.household, individual=self.individuals[0], payment_record=self.payment_record2
        )
        GrievanceComplaintTicketFactory.create_batch(5)
        SensitiveGrievanceTicketFactory.create_batch(5)

    def test_filter_existing_tickets_by_payment_record(self):
        input_data = {
            "businessArea": "afghanistan",
            "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
            "issueType": str(self.ticket.ticket.issue_type),
            "household": self.ticket.household.id,
            "individual": self.ticket.individual.id,
            "paymentRecord": [self.payment_record.id],
        }

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY, context={"user": self.user}, variables=input_data,
        )

    def test_filter_existing_tickets_by_two_payment_records(self):
        input_data = {
            "businessArea": "afghanistan",
            "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
            "issueType": str(self.ticket.ticket.issue_type),
            "household": self.ticket.household.id,
            "individual": self.ticket.individual.id,
            "paymentRecord": [self.payment_record.id, self.payment_record2.id],
        }

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY, context={"user": self.user}, variables=input_data,
        )

    def test_filter_existing_tickets_by_household(self):
        input_data = {
            "businessArea": "afghanistan",
            "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
            "issueType": str(self.ticket.ticket.issue_type),
            "household": self.ticket.household.id,
            "individual": self.ticket.individual.id,
        }

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY, context={"user": self.user}, variables=input_data,
        )

    def test_filter_existing_tickets_by_individual(self):
        input_data = {
            "businessArea": "afghanistan",
            "category": str(GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE),
            "issueType": self.ticket.ticket.issue_type,
            "individual": self.ticket.individual.id,
        }

        self.snapshot_graphql_request(
            request_string=self.FILTER_EXISTING_GRIEVANCES_QUERY, context={"user": self.user}, variables=input_data,
        )
