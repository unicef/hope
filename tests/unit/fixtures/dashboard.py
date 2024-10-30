from typing import Callable

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.dashboard.serializers import DashboardHouseholdSerializer
from hct_mis_api.apps.dashboard.services import DashboardDataCache
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentRecordFactory


@pytest.fixture()
def populate_dashboard_cache() -> Callable[[BusinessAreaFactory], None]:
    """
    Fixture to populate the dashboard cache for a specific business area.
    """

    def _populate_dashboard_cache(afghanistan: BusinessAreaFactory) -> None:
        household, individuals = create_household(household_args={"business_area": afghanistan})
        PaymentFactory.create_batch(5, household=household)
        PaymentRecordFactory.create_batch(3, household=household)
        serialized_data = DashboardHouseholdSerializer(household).data
        DashboardDataCache.store_data(afghanistan.slug, serialized_data)

    return _populate_dashboard_cache
