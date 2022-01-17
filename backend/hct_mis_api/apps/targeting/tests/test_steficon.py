from unittest import TestCase
from uuid import uuid4

from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.tasks import target_population_apply_steficon


class TestTargetingSteficon(TestCase):
    def setUp(self):
        super().setUp()
        rule, __ = Rule.objects.update_or_create(name="TestRule1", defaults={"definition": "result.value=999"})
        rule.commit(True)
        self.target_population = TargetPopulationFactory(steficon_rule=rule.latest)
        hoh = IndividualFactory(household=None)
        households = [HouseholdFactory(head_of_household=hoh)]
        self.target_population.households.add(*households)

    def test_queue(self):
        assert self.target_population.selections.count() == 1
        assert self.target_population.households.count() == 1
        target_population_apply_steficon(self.target_population.pk)
        entry = self.target_population.selections.first()
        assert entry.vulnerability_score == 999, entry.vulnerability_score
