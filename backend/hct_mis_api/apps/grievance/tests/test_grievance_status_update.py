from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    AdminAreaFactory,
    AdminAreaLevelFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket


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

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="asdsdf334")
        AdminAreaFactory(title="City Example", admin_area_level=area_type, p_code="jghhrrr")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="asdsdf334")
        AreaFactory(name="City Example", area_type=area_type, p_code="jghhrrr")

        cls.grievance_ticket1 = GrievanceTicket.objects.create(
            description="Test",
            assigned_to=cls.user,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            consent=True,
            language="PL",
            created_by=cls.user,
            business_area=cls.business_area,
        )
        cls.grievance_ticket2 = GrievanceTicket.objects.create(
            description="Test",
            assigned_to=cls.user,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            consent=True,
            language="PL",
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            business_area=cls.business_area,
        )
        cls.grievance_ticket3 = GrievanceTicket.objects.create(
            description="Test",
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            consent=True,
            language="PL",
            status=GrievanceTicket.STATUS_NEW,
            created_by=cls.user,
            business_area=cls.business_area,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_grievance_status_change(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables = {
            "status": GrievanceTicket.STATUS_ASSIGNED,
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket1.id, "GrievanceTicketNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK, Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK],
            ),
            ("without_permission", []),
        ]
    )
    def test_grievance_status_change_fail(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables = {
            "status": GrievanceTicket.STATUS_CLOSED,
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket2.id, "GrievanceTicketNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE, Permissions.GRIEVANCE_ASSIGN],
            ),
            ("without_permission", []),
        ]
    )
    def test_grievance_assign_user(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables = {
            "status": GrievanceTicket.STATUS_ASSIGNED,
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket3.id, "GrievanceTicketNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )
