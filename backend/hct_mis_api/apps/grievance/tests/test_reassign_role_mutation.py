from hct_mis_api.apps.account.fixtures import UserFactory
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
from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestRoleReassignMutation(APITestCase):
    REASSIGN_ROLE_MUTATION = """
    mutation ReassignRole(
      $grievanceTicketId: ID!, 
      $householdId: ID!, 
      $individualId: ID!, 
      $newIndividualId: ID,
      $role: String!
    ) {
      reassignRole(
        grievanceTicketId: $grievanceTicketId, 
        householdId: $householdId, 
        individualId: $individualId, 
        newIndividualId: $newIndividualId,
        role: $role
      ) {
        household {
          id
        }
        individual {
          id
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        cls.admin_area = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="sadf3223")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_new = AreaFactory(name="City Test", area_type=area_type, p_code="sadf3223")

        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first())

        cls.household = HouseholdFactory.build(id="b5cb9bb2-a4f3-49f0-a9c8-a2f260026054")
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.save()
        cls.household.programs.add(program_one)

        cls.individual = IndividualFactory(
            **{
                "id": "d4848d8e-4a1c-49e9-b1c0-1e994047164a",
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "household": None,
            },
        )

        cls.household.head_of_household = cls.individual
        cls.household.save()

        cls.individual.household = cls.household
        cls.individual.save()

        cls.household.refresh_from_db()
        cls.individual.refresh_from_db()

        cls.role = IndividualRoleInHousehold.objects.create(
            household=cls.household,
            individual=cls.individual,
            role=ROLE_PRIMARY,
        )

        cls.grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin2=cls.admin_area,
            admin2_new=cls.admin_area_new,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketDeleteIndividualDetailsFactory(
            ticket=cls.grievance_ticket,
            individual=cls.individual,
            approve_status=True,
        )

    def test_role_reassignment(self):
        variables = {
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
            "householdId": self.id_to_base64(self.household.id, "HouseholdNode"),
            "individualId": self.id_to_base64(self.individual.id, "IndividualNode"),
            "role": ROLE_PRIMARY,
        }
        self.graphql_request(
            request_string=self.REASSIGN_ROLE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

        self.grievance_ticket.refresh_from_db()
        ticket_details = self.grievance_ticket.delete_individual_ticket_details
        role_reassign_data = ticket_details.role_reassign_data

        expected_data = {
            str(self.role.id): {
                "role": "PRIMARY",
                "household": self.id_to_base64("b5cb9bb2-a4f3-49f0-a9c8-a2f260026054", "HouseholdNode"),
                "individual": self.id_to_base64("d4848d8e-4a1c-49e9-b1c0-1e994047164a", "IndividualNode"),
            }
        }
        self.assertEqual(role_reassign_data, expected_data)
