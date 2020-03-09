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
        "date_time_this_year", before_now=True, after_now=False
    )
    last_edited_at = factory.Faker(
        "date_time_this_year", before_now=False, after_now=True
    )
    status = factory.fuzzy.FuzzyChoice(
        TargetPopulation.STATE_CHOICES, getter=lambda x: x[0],
    )
    total_households = factory.fuzzy.FuzzyInteger(5, 500)
    total_family_size = factory.fuzzy.FuzzyInteger(2, 20)

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
