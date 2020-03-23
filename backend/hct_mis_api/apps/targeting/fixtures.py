import datetime as dt
import random

import factory
from account.fixtures import UserFactory
from core.utils import JSONFactory
from factory import fuzzy
from household.fixtures import HouseholdFactory
from household.models import Individual
from targeting.models import TargetPopulation
from targeting.models import TargetRule


class TargetPopulationFactory(factory.DjangoModelFactory):

    class Meta:
        model = TargetPopulation

    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    created_by = factory.SubFactory(UserFactory)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True
    )
    last_edited_at = factory.LazyAttribute(
        lambda t: t.created_at + dt.timedelta(days=random.randint(60, 1000))
    )
    status = factory.fuzzy.FuzzyChoice(
        TargetPopulation.STATE_CHOICES, getter=lambda x: x[0],
    )

    @factory.post_generation
    def households(self, create, extracted, **kwargs):
        if not create:
            households = HouseholdFactory.create_batch(5)
            self.households.add(*households)

        if extracted:
            for household in extracted:
                self.households.add(household)

    @factory.post_generation
    def target_rules(self, create, extracted, **kwargs):
        if not create:
            target_rules = TargetRuleFactory.create_batch(5)
            self.target_rules.add(*target_rules)

        if extracted:
            for target_rule in extracted:
                self.target_rules.add(target_rule)


class TargetRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetRule

    flex_rules = factory.Dict(
        {
            "age_min": fuzzy.FuzzyInteger(1, 10),
            "age_max": fuzzy.FuzzyInteger(11, 120),
        },
        dict_factory=JSONFactory,
    )
    core_rules = factory.Dict(
        {
            "intake_group": factory.Faker(
                "sentence",
                nb_words=6,
                variable_nb_words=True,
                ext_word_list=None,
            ),
            "sex": fuzzy.FuzzyChoice(
                Individual.SEX_CHOICE, getter=lambda x: x[0]
            ),
            "num_individuals_min": fuzzy.FuzzyInteger(1, 2),
            "num_individuals_max": fuzzy.FuzzyInteger(3, 20),
        },
        dict_factory=JSONFactory,
    )
    target_population = factory.SubFactory(TargetPopulationFactory)
