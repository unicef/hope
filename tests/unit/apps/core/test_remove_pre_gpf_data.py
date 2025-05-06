from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
)
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    PendingHousehold,
    PendingIndividual,
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
        assert Individual.all_objects.count() == 4
        assert PendingIndividual.all_objects.count() == 4
        assert Household.all_objects.count() == 4
        assert PendingHousehold.all_objects.count() == 4

        with mock.patch("sys.stdout", new=StringIO()):
            call_command("remove-pre-gpf-data")

        # check count after
        assert Individual.all_objects.count() == 2
        assert PendingIndividual.all_objects.count() == 2
        assert Household.all_objects.count() == 2
        assert PendingHousehold.all_objects.count() == 2
