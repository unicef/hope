import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    RuleFactory,
)
from hope.apps.steficon.forms import RuleForm
from hope.models import Rule

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        has_data_sharing_agreement=True,
    )


def test_clean_method(business_area):
    form_data = {
        "allowed_business_areas": [business_area],
        "definition": "result.value=0",
        "deprecated": False,
        "description": "Some text here",
        "enabled": True,
        "flags": None,
        "language": "python",
        "name": "Test 123",
        "security": 0,
        "type": "TARGETING",
    }

    form = RuleForm(data=form_data)
    assert form.is_valid()

    form_data_with_black = {
        "name": "Test",
        "definition": "result.value = 0",
        "language": "python",
        "description": "Some text here",
        "enabled": True,
        "deprecated": False,
        "security": 0,
        "type": "TARGETING",
        "allowed_business_areas": [business_area],
    }

    form_with_black = RuleForm(data=form_data_with_black)
    assert form_with_black.is_valid()

    cleaned_data = form_with_black.clean()
    assert cleaned_data.get("definition") != "result.value=0"


def test_clean_method_for_update_allowed_business_areas(business_area):
    rule = RuleFactory(
        name="Rule_1",
        type=Rule.TYPE_TARGETING,
        language="python",
        flags={"individual_data_needed": False},
    )

    assert rule.allowed_business_areas.count() == 0

    form_data = {"allowed_business_areas": [business_area]}

    form = RuleForm(instance=rule, initial=form_data)

    form.is_valid = lambda: True
    form.full_clean = lambda: None
    form.cleaned_data = form_data

    cleaned_data = form.clean()

    assert "allowed_business_areas" in cleaned_data

    form.save()
    rule.refresh_from_db()

    assert rule.allowed_business_areas.count() == 1
    assert rule.allowed_business_areas.first().slug == "afghanistan"
