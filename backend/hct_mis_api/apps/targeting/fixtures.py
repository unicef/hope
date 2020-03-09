import datetime as dt

import factory
from account.fixtures import UserFactory
from core.utils import JSONFactory
from factory import fuzzy
from household.fixtures import HouseholdFactory
from targeting.models import TargetPopulation
from targeting.models import TargetRule

_NOW_DT = dt.datetime.utcnow().astimezone()


def get_fuzzy_dates_from_now(delta_days, last_edited=0):
    """Creates a datetime from Fuzzy Date Time.
    args:
        delta_days: int, how many days to rewind from current timestamp.

    returns:
        FuzzyDateTime.
    """
    past_createstamp = _NOW_DT - dt.timedelta(days=delta_days)
    last_edited = past_createstamp + dt.timedelta(days=last_edited)
    return fuzzy.FuzzyDateTime(start_dt=past_createstamp, end_dt=last_edited)


class TargetPopulationFactory(factory.DjangoModelFactory):
    _DELTA_DAYS = 365
    _LAST_EDITED = 10

    class Meta:
        model = TargetPopulation

    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    created_by = factory.SubFactory(UserFactory)
    created_at = get_fuzzy_dates_from_now(_DELTA_DAYS, _LAST_EDITED)
    last_edited_at = get_fuzzy_dates_from_now(_DELTA_DAYS, _LAST_EDITED)
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
