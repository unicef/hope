import datetime as dt

import factory
from account.fixtures import UserFactory
from factory import fuzzy
from household.fixtures import HouseholdFactory
from targeting.models import TargetFilter
from targeting.models import TargetPopulation


class TargetPopulationFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetPopulation

    name = factory.LazyAttribute(lambda: "sentence")
    created_by = factory.SubFactory(UserFactory)
    last_edited_at = fuzzy.FuzzyDateTime(dt.datetime.utcnow().astimezone())
    status = factory.fuzzy.FuzzyChoice(
        TargetPopulation.STATE_CHOICES,
        getter=lambda x: x[0],
    )
    households = factory.RelatedFactory(HouseholdFactory)


class TargetFilterFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetFilter

    intake_group = factory.LazyAttribute(lambda: "sentence")
    sex = factory.fuzzy.FuzzyChoice(
        TargetFilter.GENDER_CHOICES,
        getter=lambda x: x[0],
    )
    age_min = factory.LazyAttribute(lambda: 1)
    age_max = factory.LazyAttribute(lambda: 200)
    school_distance_min = factory.LazyAttribute(lambda: 1)
    school_distance_max = factory.LazyAttribute(lambda: 20)
    num_individuals_min = factory.LazyAttribute(lambda: 1)
    num_individuals_max = factory.LazyAttribute(lambda: 50)
    target_population = factory.SubFactory(TargetPopulationFactory)
