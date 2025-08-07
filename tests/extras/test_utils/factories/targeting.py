import random
import typing
from typing import Any, List, Optional, Union

import factory
from factory.django import DjangoModelFactory

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import Scope
from hope.apps.household.models import RESIDENCE_STATUS_CHOICE
from hope.apps.targeting.models import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
)


def comparison_method_resolver(obj: Any) -> Optional[Union[List[str], str]]:
    core_fields = FieldFactory.from_scope(Scope.GLOBAL)
    core_field_attrs = [attr for attr in core_fields if attr.get("name") == obj.field_name]
    core_field_attr = core_field_attrs[0]
    if core_field_attr.get("type") == "INTEGER":
        return random.choice(["EQUALS", "NOT_EQUALS", "RANGE", "NOT_IN_RANGE", "GREATER_THAN", "LESS_THAN"])

    if core_field_attr.get("type") == "SELECT_ONE":
        return random.choice(["EQUALS", "NOT_EQUALS"])
    if core_field_attr.get("type") == "STRING":
        return "CONTAINS"
    return None


@typing.no_type_check
def arguments_resolver(obj: Any) -> Union[int, Optional[List[int]]]:
    minimum = None
    maximum = None
    if obj.field_name == "age":
        minimum = random.randint(1, 100)
        maximum = random.randint(minimum, random.randint(minimum + 1, 116))
    if obj.field_name == "size":
        minimum = random.randint(1, 5)
        maximum = random.randint(minimum, random.randint(minimum + 1, 10))
    if obj.field_name == "residence_status":
        return [random.choice([x[0] for x in RESIDENCE_STATUS_CHOICE])]
    if obj.comparison_method == "RANGE" or obj.comparison_method == "NOT_IN_RANGE":
        return [minimum, maximum]
    return [minimum]


class TargetingCriteriaRuleFilterFactory(DjangoModelFactory):
    field_name = factory.fuzzy.FuzzyChoice(
        ["size", "residence_status"],
    )
    comparison_method = factory.LazyAttribute(comparison_method_resolver)
    arguments = factory.LazyAttribute(arguments_resolver)

    class Meta:
        model = TargetingCriteriaRuleFilter


class TargetingCriteriaRuleFactory(DjangoModelFactory):
    class Meta:
        model = TargetingCriteriaRule
