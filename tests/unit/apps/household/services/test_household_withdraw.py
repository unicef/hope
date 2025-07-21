from django.conf import settings
from django.test import TestCase

from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import (
    DocumentFactory,
    create_household_for_fixtures,
)
from hct_mis_api.apps.household.models import Document, Household, Individual
from hct_mis_api.apps.household.services.household_withdraw import HouseholdWithdraw
from tests.extras.test_utils.factories.program import ProgramFactory


class TestHouseholdWithdraw(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()

    def test_withdraw(self) -> None:
        _, individuals = create_household_for_fixtures({"size": 5})
        for individual in individuals:
            DocumentFactory.create_batch(2, individual=individual, status=Document.STATUS_VALID)
            DocumentFactory.create_batch(3, individual=individual, status=Document.STATUS_NEED_INVESTIGATION)

        household, individuals = create_household_for_fixtures({"size": 5})
        household.program = ProgramFactory()
        for individual in individuals:
            DocumentFactory.create_batch(2, individual=individual, status=Document.STATUS_VALID)
            DocumentFactory.create_batch(3, individual=individual, status=Document.STATUS_NEED_INVESTIGATION)

        self.assertEqual(Household.objects.filter(withdrawn=True).count(), 0)
        self.assertEqual(Individual.objects.filter(withdrawn=True).count(), 0)
        self.assertEqual(Document.objects.filter(status=Document.STATUS_NEED_INVESTIGATION).count(), 30)

        service = HouseholdWithdraw(household)
        service.withdraw()

        self.assertEqual(Household.objects.filter(withdrawn=True).count(), 1)
        self.assertEqual(Individual.objects.filter(withdrawn=True).count(), 5)
        self.assertEqual(Document.objects.filter(status=Document.STATUS_INVALID).count(), 25)
