from django.core.management import call_command
from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    DocumentFactory,
    create_household_for_fixtures,
)
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.household.models import Document, Household, Individual
from hope.apps.household.services.household_withdraw import HouseholdWithdraw


class TestHouseholdWithdraw(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
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
