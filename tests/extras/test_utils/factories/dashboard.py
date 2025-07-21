from typing import Callable, Dict, Optional

from django.db import transaction

import factory
import pytest

from tests.extras.test_utils.factories.account import BusinessAreaFactory
from tests.extras.test_utils.factories.geo import AreaFactory
from tests.extras.test_utils.factories.household import create_household
from hct_mis_api.apps.household.models import Household
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory


class ModifiedPaymentFactory(PaymentFactory):
    """
    A specialized factory for creating Payments that match the filtering logic
    in DashboardDataCache.refresh_data.
    """

    parent = factory.SubFactory(PaymentPlanFactory, status=factory.Iterator(["ACCEPTED", "FINISHED"]))
    status = factory.Iterator(["Transaction Successful", "Distribution Successful", "Partially Distributed", "Pending"])


@pytest.fixture()
@pytest.mark.django_db(databases=["default", "read_only"])
def populate_dashboard_cache() -> Callable[[BusinessAreaFactory, Optional[Dict]], Household]:
    """
    Fixture to populate the dashboard cache for a specific business area,
    verify creation in the default DB, and ensure readability in the read_only DB.
    """

    def _populate_dashboard_cache(
        afghanistan: BusinessAreaFactory, household_extra_args: Optional[Dict] = None
    ) -> Household:
        """
        Create household and related records
        """
        with transaction.atomic(using="default"):
            program = ProgramFactory(business_area=afghanistan)
            household, _ = create_household(
                household_args={
                    "business_area": afghanistan,
                    "size": 5,
                    "children_count": 2,
                    "female_age_group_0_5_disabled_count": 1,
                    "female_age_group_6_11_disabled_count": 1,
                    "male_age_group_60_disabled_count": 1,
                    "admin1": AreaFactory(name="Kabul", area_type__name="Province", area_type__area_level=1),
                    "program": program,
                    **(household_extra_args or {}),
                }
            )
            ModifiedPaymentFactory.create_batch(5, household=household, program=program)

        return household

    return _populate_dashboard_cache
