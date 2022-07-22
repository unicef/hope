from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.cash_assist_datahub.models import Session
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
)
from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
    PullFromDatahubTask,
)
from hct_mis_api.apps.household.fixtures import create_household


class TestRecalculatingCash(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_household_cash_received_update(self):
        household, _ = create_household(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": self.business_area,
                "total_cash_received": None,
                "total_cash_received_usd": None,
            },
        )

        self.assertIsNone(household.total_cash_received)
        self.assertIsNone(household.total_cash_received_usd)

        PullFromDatahubTask().execute()

        self.assertIsNotNone(household.total_cash_received)
        self.assertIsNotNone(household.total_cash_received_usd)
