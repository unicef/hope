from typing import Callable

from django.db import transaction

import factory
import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class ModifiedPaymentFactory(PaymentFactory):
    """
    A specialized factory for creating Payments that match the filtering logic
    in DashboardDataCache.refresh_data.
    """

    parent = factory.SubFactory(PaymentPlanFactory, status=factory.Iterator(["ACCEPTED", "FINISHED"]))
    status = factory.Iterator(["Transaction Successful", "Distribution Successful", "Partially Distributed", "Pending"])


@pytest.fixture()
@pytest.mark.django_db(databases=["default", "read_only"])
def populate_dashboard_cache() -> Callable[[BusinessAreaFactory], Household]:
    """
    Fixture to populate the dashboard cache for a specific business area,
    verify creation in the default DB, and ensure readability in the read_only DB.
    """

    def _populate_dashboard_cache(afghanistan: BusinessAreaFactory) -> Household:
        """
        Create household and related records
        """
        with transaction.atomic(using="default"):
            program = ProgramFactory(business_area=afghanistan)

            household, _ = create_household(
                household_args={
                    "business_area": afghanistan,
                    "size": 14,
                    "female_age_group_0_5_disabled_count": 1,
                    "female_age_group_6_11_disabled_count": 0,
                    "female_age_group_12_17_disabled_count": 2,
                    "female_age_group_18_59_disabled_count": 2,
                    "female_age_group_60_disabled_count": 5,
                    "male_age_group_0_5_disabled_count": 0,
                    "male_age_group_6_11_disabled_count": 1,
                    "male_age_group_12_17_disabled_count": 2,
                    "male_age_group_18_59_disabled_count": 0,
                    "male_age_group_60_disabled_count": 1,
                    "admin1": AreaFactory(name="Kabul", area_type__name="Province", area_type__area_level=1),
                    "program": program,
                }
            )
            ModifiedPaymentFactory.create_batch(5, household=household, program=program)

        return household

    return _populate_dashboard_cache

