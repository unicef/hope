from django.core.management import call_command

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
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketDeleteIndividualDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestWithdrawHousehold(APITestCase):
    STATUS_CHANGE_MUTATION = """
        mutation GrievanceStatusChange($grievanceTicketId: ID!, $status: Int) {
          grievanceStatusChange(grievanceTicketId: $grievanceTicketId, status: $status) {
            grievanceTicket {
              id
              addIndividualTicketDetails {
                individualData
              }
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")

        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.first()

        cls.area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        cls.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_level=cls.area_type, p_code="sfds323")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1_new = AreaFactory(name="City Test", area_type=area_type, p_code="sfds323")

        cls.program_one = ProgramFactory(
            name="Test program ONE",
            business_area=cls.business_area,
        )

    def test_withdraw_household_when_withdraw_last_individual_empty(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], self.business_area
        )

        household = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07")
        household.registration_data_import.imported_by.save()
        household.registration_data_import.save()
        household.programs.add(self.program_one)

        individual_data = {
            "id": "257f6f84-313c-43bd-8f0e-89b96c41a7d5",
            "full_name": "Test Example",
            "given_name": "Test",
            "family_name": "Example",
            "phone_no": "+18773523904",
            "birth_date": "1965-03-15",
            "household": household,
        }

        individual = IndividualFactory(**individual_data)

        household.head_of_household = individual
        household.save()

        ticket = GrievanceTicketFactory(
            id="a2a15944-f836-4764-8163-30e0c47ce3bb",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin2=self.admin_area_1,
            admin2_new=self.admin_area_1_new,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )

        TicketDeleteIndividualDetailsFactory(
            ticket=ticket,
            individual=individual,
            role_reassign_data={},
            approve_status=True,
        )

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )

        ind = Individual.objects.filter(id=individual.id).first()
        hh = Household.objects.filter(id=household.id).first()

        self.assertTrue(ind.withdrawn)
        self.assertTrue(hh.withdrawn)
