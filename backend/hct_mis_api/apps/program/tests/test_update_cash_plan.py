from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from program.fixtures import CashPlanFactory
from program.models import CashPlan


class TestUpdateCashPlan(APITestCase):
    UPDATE_CASH_PLAN_MUTATION = """
    mutation UpdateCashPlan($cashPlanData: UpdateCashPlanInput) {
      updateCashPlan(cashPlanData: $cashPlanData) {
        cashPlan {
          name
          status
          fsp
          numberOfHouseholds
        }
      }
    }
    """

    def test_update_cash_plan_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.UPDATE_CASH_PLAN_MUTATION,
            variables={
                "cashPlanData": {
                    "id": "Q2FzaFBsYW5Ob2RlOjVmNmQyODFhLWEyYz"
                    "QtNDgzZC05NGY1LWFhYmY1M2I4MjVlMw==",
                    "programId": "UHJvZ3JhbU5vZGU6Y2U0Yzk4MDMtN"
                    "zUyMC00ZDYwLTliMGYtNDdiZWIyZjZkMTFm",
                    "name": "Test Cash Plan",
                    "startDate": "2020-12-16T13:15:32",
                    "endDate": "2023-10-23T15:00:32",
                    "disbursementDate": "2023-10-23T15:00:32",
                    "numberOfHouseholds": 514,
                    "coverageDuration": 45,
                    "coverageUnits": "Day(s)",
                    "targetPopulationId": "VGFyZ2V0UG9wdWxhdGlvbk"
                    "5vZGU6NTZlMDllMjAtYmRkN"
                    "i00ZWIzLWE1OTQtZjliYTc5MDRiMDRk",
                    "cashAssistId": "2b7f0db7-9010-4d1d-8b1f-19357b29c7b0",
                    "distributionModality": "363-39",
                    "fsp": "Hayes LLC",
                    "status": "STARTED",
                    "currency": "Indian Rupee",
                    "totalEntitledQuantity": 30000,
                    "totalDeliveredQuantity": 10000,
                    "totalUndeliveredQuantity": 20000,
                    "dispersionDate": "2023-10-22",
                }
            },
        )

    def test_update_cash_plan_authenticated(self):
        user = UserFactory.create()

        cash_plan = CashPlanFactory.create()

        self.snapshot_graphql_request(
            request_string=self.UPDATE_CASH_PLAN_MUTATION,
            context={"user": user},
            variables={
                "cashPlanData": {
                    "id": self.id_to_base64(cash_plan.id, "CashPlan"),
                    "name": "updated name",
                    "status": "STARTED",
                    "fsp": "updated fsp",
                    "numberOfHouseholds": 618,
                }
            },
        )

        updated_cash_plan = CashPlan.objects.get(id=cash_plan.id)

        assert updated_cash_plan.status == "STARTED"
        assert updated_cash_plan.name == "updated name"
