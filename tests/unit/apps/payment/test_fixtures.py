from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.household.fixtures import HouseholdFactory
from hct_mis_api.apps.payment.fixtures import (
    generate_delivery_mechanisms,
    generate_payment_plan,
    generate_reconciled_payment_plan,
    update_fsps,
)


class TestFixtures(TestCase):
    """Most of these fixtures are used in initdemo.py management command. Just checking if they don't crash."""

    def test_fixtures_functions(self) -> None:
        afg = create_afghanistan()
        UserFactory(username="root")
        DataCollectingTypeFactory(
            label="Full",
            code="full",
            weight=1,
            business_areas=[afg],
            type=DataCollectingType.Type.STANDARD.value,
        )
        HouseholdFactory()
        generate_delivery_mechanisms()
        generate_payment_plan()
        generate_reconciled_payment_plan()
        update_fsps()
