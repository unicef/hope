from types import SimpleNamespace
from unittest.mock import patch

import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.validators import TargetingCriteriaRuleFilterInputValidator

pytestmark = pytest.mark.django_db


@pytest.fixture
def program():
    business_area = BusinessAreaFactory(slug="test-ba-tv")
    return ProgramFactory(business_area=business_area)


def test_validate_passes_when_field_type_in_supported_types(program):
    rule_filter = {
        "flex_field_classification": FlexFieldClassification.NOT_FLEX_FIELD,
        "field_name": "size",
        "comparison_method": "EQUALS",
        "arguments": [1],
    }

    attribute = SimpleNamespace(type="INTEGER", pdu_data=None)

    with patch.object(
        TargetingCriteriaRuleFilterInputValidator,
        "_resolve_attribute",
        return_value=attribute,
    ):
        TargetingCriteriaRuleFilterInputValidator.validate(rule_filter, program)
