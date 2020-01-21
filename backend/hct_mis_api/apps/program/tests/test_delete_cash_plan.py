from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from program.fixtures import CashPlanFactory


class TestDeleteCashPlan(APITestCase):
    DELETE_CASH_PLAN_MUTATION = """
    mutation DeleteCashPlan($cashPlanId: String!) {
      deleteCashPlan(cashPlanId: $cashPlanId) {
            ok
      }
    }
    """

    def test_delete_cash_plan_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.DELETE_CASH_PLAN_MUTATION,
            variables={
                'cashPlanId': 'Q2FzaFBsYW5Ob2RlOjAwZDJlOGVkLT'
                              'k4ZjMtNGEzOS1iYmVmLWZiOWFlMDVmMjk4YQ=='
            },
        )

    def test_delete_cash_plan_authenticated(self):
        user = UserFactory.create()
        cash_plan = CashPlanFactory.create()

        self.snapshot_graphql_request(
            request_string=self.DELETE_CASH_PLAN_MUTATION,
            context={'user': user},
            variables={
                'cashPlanId': self.id_to_base64(cash_plan.id, 'CashPlan')
            },
        )
