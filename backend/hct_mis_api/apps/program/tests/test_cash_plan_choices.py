from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase


class TestCashPlanChoices(APITestCase):
    QUERY_CASH_PLAN_STATUS_CHOICES = """
    query CashPlanStatusChoices {
        cashPlanStatusChoices{
            name
            value
        }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()

    def test_status_choices_query(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_CASH_PLAN_STATUS_CHOICES,
            context={"user": self.user},
        )
