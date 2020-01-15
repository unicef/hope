from account.fixtures import UserFactory
from core.tests import APITestCase
from program.fixtures import CashPlanFactory
from program.models import CashPlan


class TestCashPlanQueries(APITestCase):

    QUERY_SINGLE_CASH_PLAN = """
    query CashPlan($id: ID!) {
      cashPlan(id: $id) {
        id
        name
        startDate
        endDate
        disbursementDate
        numberOfHouseholds
        createdDate
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
      }
    }
    """

    QUERY_ALL_CASH_PLANS = """
    query AllCashPlans {
      allCashPlans {
        edges {
          node {
            name
            startDate
            endDate
            disbursementDate
            numberOfHouseholds
            createdDate
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
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        CashPlanFactory.create_batch(10)

    def test_get_single_cash_plan(self):
        cash_plan = CashPlan.objects.first()

        self.snapshot_graphql_request(
            request_string=self.QUERY_SINGLE_CASH_PLAN,
            variables={'id': self.id_to_base64(
                cash_plan.id,
                'CashPlan',
                False,
            )},
            context={'user': self.user},
        )

    def test_get_all_cash_plans(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_ALL_CASH_PLANS,
            context={'user': self.user},
        )
