from datetime import datetime

from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.models import GrievanceTicket
from household.fixtures import HouseholdFactory, IndividualFactory
from program.fixtures import ProgramFactory


class TestGrievanceCreateDataChangeMutation(APITestCase):
    CREATE_DATA_CHANGE_GRIEVANCE_MUTATION = """
    mutation gtStatusChange($status:Int, $grievanceTicketId:ID){
      grievanceStatusChange(status:$status,grievanceTicketId:$grievanceTicketId){
            grievanceTicket{
          status
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(
            name="Admin type one",
            admin_level=2,
            business_area=self.business_area,
        )
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_type=area_type)
        self.grievance_ticket1 = GrievanceTicket.objects.create(
            description="Test",
            assigned_to=self.user,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            consent=True,
            language="PL",
            created_by=self.user,
            business_area=self.business_area
        )
        self.grievance_ticket2 = GrievanceTicket.objects.create(
            description="Test",
            assigned_to=self.user,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            consent=True,
            language="PL",
            status=GrievanceTicket.STATUS_NEW,
            created_by=self.user,
            business_area=self.business_area
        )

    def test_grievance_status_change(self):
        variables = {
            "status": GrievanceTicket.STATUS_ASSIGNED,
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket1.id, "GrievanceTicketNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

    def test_grievance_status_change_fail(self):
        variables = {
            "status": GrievanceTicket.STATUS_CLOSED,
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket2.id, "GrievanceTicketNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )


