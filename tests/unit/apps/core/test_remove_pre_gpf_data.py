from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    PendingHousehold,
    PendingIndividual,
)
from tests.extras.test_utils.factories.account import BusinessAreaFactory
from tests.extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
)


class TestRemovePreGpfDataCommands(TestCase):
    def setUp(self) -> None:
        BusinessAreaFactory(name="Afghanistan")
        IndividualFactory(household=None)
        IndividualFactory(is_original=True, household=None)
        PendingIndividualFactory(household=None)
        PendingIndividualFactory(is_original=True, household=None)
        HouseholdFactory()
        HouseholdFactory(is_original=True)
        PendingHouseholdFactory()
        PendingHouseholdFactory(is_original=True)

    def test_remove_pre_gpf_data(self) -> None:
        # check count before
        self.assertEqual(Individual.all_objects.count(), 4)
        self.assertEqual(PendingIndividual.all_objects.count(), 4)
        self.assertEqual(Household.all_objects.count(), 4)
        self.assertEqual(PendingHousehold.all_objects.count(), 4)

        with mock.patch("sys.stdout", new=StringIO()):
            call_command("remove-pre-gpf-data")

        # check count after
        self.assertEqual(Individual.all_objects.count(), 2)
        self.assertEqual(PendingIndividual.all_objects.count(), 2)
        self.assertEqual(Household.all_objects.count(), 2)
        self.assertEqual(PendingHousehold.all_objects.count(), 2)
