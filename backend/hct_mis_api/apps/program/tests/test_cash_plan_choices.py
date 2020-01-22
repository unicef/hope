from account.fixtures import UserFactory
from core.base_test_case import APITestCase


class TestCashPlanChoices(APITestCase):

    QUERY_CASH_PLAN_STATUS_CHOICES = """
    query CashPlanStatusChoices {
        cashPlanStatusChoices{
            name
            value
        }
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()

    def test_status_choices_query(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_CASH_PLAN_STATUS_CHOICES,
            context={"user": self.user},
        )
