import datetime as dt

import factory
from account.fixtures import UserFactory
from core.utils import JSONFactory
from factory import fuzzy
from household.fixtures import HouseholdFactory
from targeting.models import TargetPopulation
from targeting.models import TargetRule


class TargetPopulationFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetPopulation

    name = "sentence"
    created_by = factory.SubFactory(UserFactory)
    last_edited_at = fuzzy.FuzzyDateTime(dt.datetime.utcnow().astimezone())
    status = factory.fuzzy.FuzzyChoice(
        TargetPopulation.STATE_CHOICES, getter=lambda x: x[0],
    )
    total_households = 10
    total_family_size = 20

    @factory.post_generation
    def households(self, create, extracted, **kwargs):
        if not create:
            self.households.add(HouseholdFactory())

        if extracted:
            for household in extracted:
                self.households.add(household)


class TargetRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetRule

    flex_rules = factory.Dict(
        {"age_min": 1, "age_max": 25,}, dict_factory=JSONFactory
    )
    core_rules = factory.Dict(
        {
            "intake_group": "registration import name",
            "sex": "Male",
            "num_individuals_min": 1,
            "num_individuals_max": 5,
        },
        dict_factory=JSONFactory,
    )
    target_population = factory.SubFactory(TargetPopulationFactory)
