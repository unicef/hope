from unittest.mock import MagicMock, patch

import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.validators import TargetingCriteriaRuleFilterInputValidator
from hope.models import Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def program():
    business_area = BusinessAreaFactory(slug="test-ba")
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rule_filter_for_core_field():
    return {
        "flex_field_classification": FlexFieldClassification.NOT_FLEX_FIELD,
        "field_name": "size",
        "comparison_method": "EQUAL",
        "arguments": [1],
    }


def test_validate_raises_type_error_when_supported_types_is_not_a_list(program, rule_filter_for_core_field):
    mock_comparison_attribute = {
        "arguments": 1,
        "supported_types": "STRING",  # not a list
    }
    mock_attribute = MagicMock()
    mock_attribute.get = MagicMock(return_value=None)
    type(mock_attribute).__getitem__ = MagicMock(return_value=None)

    with (
        patch.object(
            TargetingCriteriaRuleFilterInputValidator,
            "_resolve_attribute",
            return_value={"type": "STRING", "name": "size"},
        ),
        patch(
            "hope.apps.targeting.validators.TargetingCriteriaRuleFilter.COMPARISON_ATTRIBUTES",
            {"EQUAL": mock_comparison_attribute},
        ),
    ):
        with pytest.raises(TypeError, match="Expected list for supported_types, got str"):
            TargetingCriteriaRuleFilterInputValidator.validate(rule_filter_for_core_field, program)
