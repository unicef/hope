import datetime as dt
import random

import factory
from account.fixtures import UserFactory
from core.models import CoreAttribute
from core.utils import JSONFactory
from factory import fuzzy
from household.fixtures import HouseholdFactory
from household.models import Individual, Household
from targeting.models import (
    TargetPopulation,
    TargetingCriteriaRuleFilter,
    TargetingCriteriaRule,
    TargetingCriteria,
)


def comparision_method_resolver(obj):
    core_fields = CoreAttribute.get_core_fields(Household)
    core_field_attrs = [
        attr for attr in core_fields if attr.get("name") == obj.field_name
    ]
    core_field_attr = core_field_attrs[0]
    if core_field_attr.get("type") == "INTEGER":
        return random.choice(
            [
                "EQUALS",
                "NOT_EQUALS",
                "RANGE",
                "NOT_IN_RANGE",
                "GREATER_THAN",
                "LESS_THAN",
            ]
        )

    if core_field_attr.get("type") == "SELECT_ONE":
        return random.choice(["EQUALS", "NOT_EQUALS",])


def arguments_resolver(obj):
    min = None
    max = None
    if obj.field_name == "years_in_school":
        min = random.randint(1, 4)
        max = random.randint(min, min + 5)
    if obj.field_name == "age":
        min = random.randint(1, 100)
        max = random.randint(min, random.randint(min+1,116))
    if obj.field_name == "family_size":
        min = random.randint(1, 5)
        max = random.randint(min, random.randint(min+1,10))
    if obj.field_name == "residence_status":
        return [random.choice([x[0] for x in Household.RESIDENCE_STATUS_CHOICE])]
    if (
        obj.comparision_method == "RANGE"
        or obj.comparision_method == "NOT_IN_RANGE"
    ):
        return [min, max]
    return [min]


class TargetingCriteriaRuleFilterFactory(factory.DjangoModelFactory):
    field_name = factory.fuzzy.FuzzyChoice(
        CoreAttribute.get_core_fields(Household),
        getter=lambda x: x.get("name"),
    )
    comparision_method = factory.LazyAttribute(comparision_method_resolver)
    arguments = factory.LazyAttribute(arguments_resolver)
    class Meta:
        model = TargetingCriteriaRuleFilter


class TargetingCriteriaRuleFactory(factory.DjangoModelFactory):

    class Meta:
        model = TargetingCriteriaRule


class TargetingCriteriaFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetingCriteria


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
    updated_at = factory.LazyAttribute(
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
