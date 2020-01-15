from account.fixtures import UserFactory
from core.tests import APITestCase
from program.fixtures import ProgramFactory
from targeting.fixtures import TargetPopulationFactory


class TestCreateCashPlan(APITestCase):
    CREATE_CASH_PLAN_MUTATION = """
    mutation CreateCashPlan($cashPlanData: CreateCashPlanInput!) {
      createCashPlan(cashPlanData: $cashPlanData) {
        cashPlan {
          name
          startDate
          endDate
          disbursementDate
          numberOfHouseholds
          coverageDuration
          coverageUnits
          cashAssistId
          distributionModality
          fsp
          status
          currency
          totalEntitledQuantity
          totalDeliveredQuantity
          totalUndeliveredQuantity
          dispersionDate
          program {
            name
          }
          targetPopulation {
            name
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.program = ProgramFactory.create(name='Test program')
        self.target_population = TargetPopulationFactory.create(
            name='Test Target Population'
        )

    def test_create_cash_plan_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_CASH_PLAN_MUTATION,
            variables={
                'cashPlanData': {
                    'programId': '8615650c-78fa-405d-8a42-2ea1f1f3f7bd',
                    'name': 'Test Cash Plan',
                    'startDate': '2033-12-16T13:15:32',
                    'endDate': '2023-10-23T15:00:32',
                    'disbursementDate': '2023-10-23T15:00:32',
                    'numberOfHouseholds': 514,
                    'coverageDuration': 45,
                    'coverageUnits': 'Day(s)',
                    'targetPopulationId': '56e09e20-bdd6-4eb3'
                                          '-a594-f9ba7904b04d',
                    'cashAssistId': '2b7f0db7-9010-4d1d-8b1f-19357b29c7b0',
                    'distributionModality': '363-39',
                    'fsp': 'Hayes LLC',
                    'status': 'STARTED',
                    'currency': 'Indian Rupee',
                    'totalEntitledQuantity': 30000,
                    'totalDeliveredQuantity': 10000,
                    'totalUndeliveredQuantity': 20000,
                    'dispersionDate': '2023-10-22',
                }
            },
        )

    def test_create_cash_plan_invalid_dates_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_CASH_PLAN_MUTATION,
            context={'user': self.user},
            variables={
                'cashPlanData': {
                    'programId': self.id_to_base64(self.program.id, 'Program'),
                    'name': 'Test Cash Plan',
                    'startDate': '2033-12-16T13:15:32',
                    'endDate': '2023-10-23T15:00:32',
                    'disbursementDate': '2023-10-23T15:00:32',
                    'numberOfHouseholds': 514,
                    'coverageDuration': 45,
                    'coverageUnits': 'Day(s)',
                    'targetPopulationId': self.id_to_base64(
                        self.target_population.id,
                        'TargetPopulation',
                    ),
                    'cashAssistId': '2b7f0db7-9010-4d1d-8b1f-19357b29c7b0',
                    'distributionModality': '363-39',
                    'fsp': 'Hayes LLC',
                    'status': 'STARTED',
                    'currency': 'Indian Rupee',
                    'totalEntitledQuantity': 30000,
                    'totalDeliveredQuantity': 10000,
                    'totalUndeliveredQuantity': 20000,
                    'dispersionDate': '2023-10-22',
                }
            },
        )

    def test_create_cash_plan_valid_dates_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.CREATE_CASH_PLAN_MUTATION,
            context={'user': self.user},
            variables={
                'cashPlanData': {
                    'programId': self.id_to_base64(self.program.id, 'Program'),
                    'name': 'Test Cash Plan',
                    'startDate': '2020-12-16T13:15:32',
                    'endDate': '2023-10-23T15:00:32',
                    'disbursementDate': '2023-10-23T15:00:32',
                    'numberOfHouseholds': 514,
                    'coverageDuration': 45,
                    'coverageUnits': 'Day(s)',
                    'targetPopulationId': self.id_to_base64(
                        self.target_population.id,
                        'TargetPopulation',
                    ),
                    'cashAssistId': '2b7f0db7-9010-4d1d-8b1f-19357b29c7b0',
                    'distributionModality': '363-39',
                    'fsp': 'Hayes LLC',
                    'status': 'STARTED',
                    'currency': 'Indian Rupee',
                    'totalEntitledQuantity': 30000,
                    'totalDeliveredQuantity': 10000,
                    'totalUndeliveredQuantity': 20000,
                    'dispersionDate': '2023-10-22',
                }
            },
        )
