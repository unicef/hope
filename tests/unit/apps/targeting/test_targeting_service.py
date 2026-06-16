from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import Q
import pytest

from extras.test_utils.factories.household import HouseholdFactory

from hope.apps.core.field_attributes.fields_types import TYPE_SELECT_MANY
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.services.targeting_service import (
    TargetingCriteriaFilterBase,
    TargetingCriteriaQueryingBase,
    TargetingCriteriaRuleQueryingBase,
    TargetingIndividualRuleFilterBlockBase,
)
from hope.models import Household


@pytest.fixture
def household(db: None) -> Household:
    return HouseholdFactory()


class _Stub:
    """Object exposing a fixed get_criteria_string() / get_query()."""

    def __init__(self, criteria_string: str = "", query: Q | None = None) -> None:
        self._criteria_string = criteria_string
        self._query = query if query is not None else Q()
        self.field_name = "size"

    def get_criteria_string(self) -> str:
        return self._criteria_string

    def get_query(self) -> Q:
        return self._query


class _Filter(TargetingCriteriaFilterBase):
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


def test_querying_base_get_criteria_string_joins_rules_with_or() -> None:
    class _Querying(TargetingCriteriaQueryingBase):
        def get_rules(self) -> list:
            return [_Stub("A"), _Stub("B")]

    assert _Querying().get_criteria_string() == "A OR B"


def test_rule_querying_base_get_criteria_string_combines_household_and_individual() -> None:
    filters = [_Stub("size=2")]
    individuals_filters_blocks = [_Stub("age>1")]
    base = TargetingCriteriaRuleQueryingBase(
        filters=filters,
        individuals_filters_blocks=individuals_filters_blocks,
    )

    assert base.get_filters() is filters
    assert base.get_individuals_filters_blocks() is individuals_filters_blocks
    assert base.get_criteria_string() == "H(size=2) AND I(age>1)"


def test_rule_querying_base_get_criteria_string_household_only() -> None:
    base = TargetingCriteriaRuleQueryingBase(filters=[_Stub("size=2")], individuals_filters_blocks=[])

    assert base.get_criteria_string() == "H(size=2)"


def test_rule_querying_base_get_criteria_string_empty() -> None:
    base = TargetingCriteriaRuleQueryingBase(filters=[], individuals_filters_blocks=[])

    assert base.get_criteria_string() == ""


def test_individual_block_base_get_criteria_string() -> None:
    block = TargetingIndividualRuleFilterBlockBase(individual_block_filters=[_Stub("age>1")])

    assert block.get_individual_block_filters() == block.individual_block_filters
    assert block.get_criteria_string() == "(age>1)"


def test_individual_block_base_get_query_returns_empty_when_no_filters() -> None:
    block = TargetingIndividualRuleFilterBlockBase(individual_block_filters=[], target_only_hoh=None)

    assert block.get_query() == Q()


def test_individual_block_base_get_query_targets_heads_of_household(household: Household) -> None:
    block = TargetingIndividualRuleFilterBlockBase(
        individual_block_filters=[_Stub(query=Q(sex="MALE"))],
        target_only_hoh=[household],
    )

    query = block.get_query()

    # builds a Q(id__in=<household ids>) wrapper, restricted to heads of household
    assert isinstance(query, Q)
    assert query.children[0][0] == "id__in"
    # heading_household__isnull=False renders as a household join with IS NOT NULL
    inner_sql = str(query.children[0][1].query)
    assert '"household_household"."id" IS NOT NULL' in inner_sql


def test_filter_field_name_combined_with_round_number() -> None:
    assert _Filter(field_name="pdu", round_number=3).field_name_combined == "pdu__3"


def test_filter_field_name_combined_without_round_number() -> None:
    assert _Filter(field_name="size", round_number=0).field_name_combined == "size"


def test_filter_get_criteria_string() -> None:
    flt = _Filter(field_name="size", round_number=0, comparison_method="EQUALS", arguments=[2])

    assert flt.get_criteria_string() == "{size EQUALS (2)}"


def test_filter_str() -> None:
    assert str(_Filter(field_name="size", comparison_method="EQUALS", arguments=[2])) == "size EQUALS [2]"


def test_get_query_for_lookup_select_many_requires_at_least_one_argument() -> None:
    flt = _Filter(field_name="f", comparison_method="CONTAINS", arguments=[])

    with pytest.raises(ValidationError, match="at least 1 argument"):
        flt.get_query_for_lookup("lookup", {"type": TYPE_SELECT_MANY})


def test_get_query_for_lookup_select_many_single_argument_uses_contains() -> None:
    flt = _Filter(
        field_name="f",
        comparison_method="CONTAINS",
        arguments=["x"],
        flex_field_classification=FlexFieldClassification.NOT_FLEX_FIELD,
    )

    query = flt.get_query_for_lookup("lookup", {"type": TYPE_SELECT_MANY})

    assert query.children[0] == ("lookup__contains", "x")


def test_get_query_for_core_field_raises_when_no_matching_attribute() -> None:
    flt = _Filter(field_name="missing", get_core_fields=list)

    with pytest.raises(ValidationError, match="no Core Field Attributes"):
        flt.get_query_for_core_field()


def test_get_query_for_core_field_raises_when_attribute_has_no_lookup() -> None:
    flt = _Filter(
        field_name="size",
        get_core_fields=lambda: [{"name": "size", "get_query": None, "lookup": None}],
    )

    with pytest.raises(ValidationError, match="doesn't have get_query method or lookup field"):
        flt.get_query_for_core_field()
