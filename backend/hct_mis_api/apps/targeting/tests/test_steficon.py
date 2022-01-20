from unittest import TestCase
from uuid import uuid4

from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.targeting.celery_tasks import target_population_apply_steficon


class TestTargetingSteficon(TestCase):
    def setUp(self):
        super().setUp()
        rule, __ = Rule.objects.update_or_create(name="TestRule1", defaults={"definition": "result.value=999"})
        rule.commit(True, force=True)
        assert rule.latest  # sanity check
        self.target_population = TargetPopulationFactory(steficon_rule=rule.latest)
        hoh = IndividualFactory(household=None)
        households = [HouseholdFactory(head_of_household=hoh)]
        self.target_population.households.add(*households)

        assert self.target_population.selections.count() == 1  # sanity check

    def test_queue(self):
        target_population_apply_steficon(self.target_population.pk)

        entry = self.target_population.selections.first()
        self.target_population.refresh_from_db()
        assert (
            self.target_population.status == TargetPopulation.STATUS_STEFICON_COMPLETED
        ), self.target_population.status
        assert entry.vulnerability_score == 999, entry.vulnerability_score
