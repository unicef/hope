from decimal import Decimal

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.celery_tasks import target_population_apply_steficon
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestTargetingSteficon(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        rule, __ = Rule.objects.update_or_create(
            name="TestRule1", defaults={"definition": "result.value=Decimal('1.3')"}
        )
        rule.commit(is_release=True, force=True)
        assert rule.latest  # sanity check
        cls.target_population = TargetPopulationFactory(steficon_rule=rule.latest, business_area=cls.business_area)
        if not cls.target_population.households.exists():
            hoh = IndividualFactory(household=None, business_area=cls.business_area)
            households = [HouseholdFactory(head_of_household=hoh)]
            cls.target_population.households.add(*households)

        assert cls.target_population.selections.count() == 1  # sanity check
        entry = cls.target_population.selections.first()
        assert entry.vulnerability_score is None

    def test_queue(self) -> None:
        target_population_apply_steficon(self.target_population.pk)

        entry = self.target_population.selections.first()
        entry.refresh_from_db()
        self.target_population.refresh_from_db()
        assert (
            self.target_population.status == TargetPopulation.STATUS_STEFICON_COMPLETED
        ), self.target_population.status
        assert entry.vulnerability_score == Decimal("1.3"), entry.vulnerability_score
