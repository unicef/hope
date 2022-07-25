from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
)
from hct_mis_api.apps.cash_assist_datahub.models import Session
from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
    PullFromDatahubTask,
)
from hct_mis_api.apps.household.fixtures import create_household


class TestRecalculatingCash(APITestCase):
    databases = "__all__"

    CREATE_PROGRAM_MUTATION = """
    mutation CreateProgram($programData: CreateProgramInput!) {
      createProgram(programData: $programData) {
        program {
          name
          status
          startDate
          endDate
          budget
          description
          frequencyOfPayments
          sector
          scope
          cashPlus
          populationGoal
          administrativeAreasOfImplementation
        }
        validationErrors
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.create_program_mutation_variables = {
            "programData": {
                "administrativeAreasOfImplementation": "",
                "budget": "0.00",
                "businessAreaSlug": "afghanistan",
                "cashPlus": True,
                "description": "",
                "endDate": "2022-07-26",
                "frequencyOfPayments": "ONE_OFF",
                "individualDataNeeded": False,
                "name": "newprogram",
                "populationGoal": 1,
                "scope": "UNICEF",
                "sector": "MULTI_PURPOSE",
                "startDate": "2022-07-25",
            }
        }

    def create_program(self):
        response = self.graphql_request(
            request_string=self.CREATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.create_program_mutation_variables,
        )
        self.assertTrue("data" in response)
        return response

    def create_targeting(self):
        pass

    def test_household_cash_received_update(self):
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CREATE], self.business_area)
        household, _ = create_household(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": self.business_area,
                "total_cash_received": None,
                "total_cash_received_usd": None,
            },
        )
        Session.objects.create(business_area=self.business_area.code, status=Session.STATUS_READY)

        self.create_program()
        self.create_targeting()

        self.assertIsNone(household.total_cash_received)
        self.assertIsNone(household.total_cash_received_usd)

        PullFromDatahubTask().execute()

        self.assertIsNotNone(household.total_cash_received)
        self.assertIsNotNone(household.total_cash_received_usd)
