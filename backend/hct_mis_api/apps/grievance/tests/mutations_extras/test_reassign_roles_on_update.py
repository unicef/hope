from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import AdminAreaFactory, AdminAreaLevelFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketDeleteIndividualDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.mutations_extras.utils import reassign_roles_on_update
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    HEAD,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestReassignRolesOnUpdate(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=self.business_area,
        )
        self.admin_area = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="sadf3223")
        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first())

        self.household = HouseholdFactory.build(id="b5cb9bb2-a4f3-49f0-a9c8-a2f260026054")
        self.household.registration_data_import.imported_by.save()
        self.household.registration_data_import.save()
        self.household.programs.add(program_one)

        self.individual = IndividualFactory(
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

        self.household.head_of_household = self.individual
        self.household.save()

        self.individual.household = self.household
        self.individual.save()

        self.household.refresh_from_db()
        self.individual.refresh_from_db()

        self.role = IndividualRoleInHousehold.objects.create(
            household=self.household,
            individual=self.individual,
            role=ROLE_PRIMARY,
        )

        self.grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin2=self.admin_area,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketDeleteIndividualDetailsFactory(
            ticket=self.grievance_ticket,
            individual=self.individual,
            approve_status=True,
        )

    def test_reassign_role_to_another_individual(self):
        individual = IndividualFactory(household=None)

        individual.household = self.household
        individual.save()

        role_reassign_data = {
            "HEAD": {
                "role": "HEAD",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(individual.id, "IndividualNode"),
            },
            self.role.id: {
                "role": "PRIMARY",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(individual.id, "IndividualNode"),
            },
        }

        reassign_roles_on_update(self.individual, role_reassign_data, None, False)

        individual.refresh_from_db()
        self.household.refresh_from_db()

        self.assertEqual(self.household.head_of_household, individual)
        self.assertEqual(individual.relationship, HEAD)
        role = IndividualRoleInHousehold.objects.get(household=self.household, individual=individual).role
        self.assertEqual(role, ROLE_PRIMARY)
