from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
)
from hope.apps.core.utils import _apply_dict_fields, get_count_and_percentage, to_dict
from hope.apps.payment.utils import get_payment_delivered_quantity_status_and_value
from hope.models import Payment

# ============================================================================
# Pure function tests (no DB needed)
# ============================================================================


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (1, {"count": 1, "percentage": 100.0}),
        (0, {"count": 0, "percentage": 0.0}),
    ],
)
def test_get_count_and_percentage_without_total_uses_count_as_denominator(count, expected):
    assert get_count_and_percentage(count) == expected


@pytest.mark.parametrize(
    ("count", "total", "expected"),
    [
        (5, 1, {"count": 5, "percentage": 500.0}),
        (20, 20, {"count": 20, "percentage": 100.0}),
        (5, 25, {"count": 5, "percentage": 20.0}),
    ],
)
def test_get_count_and_percentage_with_total_calculates_correctly(count, total, expected):
    assert get_count_and_percentage(count, total) == expected


@pytest.mark.parametrize(
    ("delivered_quantity", "entitlement_quantity", "expected_status", "expected_value"),
    [
        (-1, Decimal("10.00"), Payment.STATUS_ERROR, None),
        (0, Decimal("10.00"), Payment.STATUS_NOT_DISTRIBUTED, 0),
        (5.00, Decimal("10.00"), Payment.STATUS_DISTRIBUTION_PARTIAL, Decimal("5.00")),
        (10.00, Decimal("10.00"), Payment.STATUS_DISTRIBUTION_SUCCESS, Decimal("10.00")),
    ],
)
def test_get_payment_delivered_quantity_status_and_value_returns_correct_status(
    delivered_quantity, entitlement_quantity, expected_status, expected_value
):
    result = get_payment_delivered_quantity_status_and_value(delivered_quantity, entitlement_quantity)
    assert result == (expected_status, expected_value)


@pytest.mark.parametrize(
    "invalid_quantity",
    [None, ""],
)
def test_get_payment_delivered_quantity_status_and_value_raises_for_invalid_input(invalid_quantity):
    with pytest.raises(Exception, match="Invalid delivered quantity"):
        get_payment_delivered_quantity_status_and_value(invalid_quantity, Decimal("10.00"))


def test_get_payment_delivered_quantity_status_and_value_raises_when_exceeds_entitlement():
    with pytest.raises(Exception, match="Invalid delivered quantity"):
        get_payment_delivered_quantity_status_and_value(20.00, Decimal("10.00"))


# ============================================================================
# _apply_dict_fields tests (no DB needed)
# ============================================================================


def test_apply_dict_fields_skips_nonexistent_attribute():
    """When instance lacks the attribute, data should remain unchanged."""
    data = {}
    instance = MagicMock(spec=[])  # no attributes at all
    _apply_dict_fields(data, instance, {"missing_field": ["name"]})
    assert data == {}


def test_apply_dict_fields_single_object_produces_dict():
    """When the field is a single object (no .db), data[key] should be a dict."""
    related_obj = MagicMock()
    related_obj.full_name = "John Doe"

    instance = MagicMock()
    instance.related = related_obj
    # Ensure the related object does NOT have a .db attribute (single object, not a manager)
    del related_obj.db

    data = {}
    _apply_dict_fields(data, instance, {"related": ["full_name"]})
    assert data["related"] == {"full_name": "John Doe"}


def test_apply_dict_fields_queryset_produces_list():
    """When the field has .db (queryset manager), data[key] should be a list of dicts."""
    child1 = MagicMock()
    child1.name = "Alice"
    child2 = MagicMock()
    child2.name = "Bob"

    manager = MagicMock()
    manager.db = "default"  # has .db attribute, simulating a manager
    manager.all.return_value = [child1, child2]

    instance = MagicMock()
    instance.children = manager

    data = {}
    _apply_dict_fields(data, instance, {"children": ["name"]})
    assert data["children"] == [{"name": "Alice"}, {"name": "Bob"}]


def test_apply_dict_fields_queryset_empty_nested_not_appended():
    """When nested fields don't resolve, empty dicts should not be appended to the list."""
    obj_with_no_matching_attr = MagicMock(spec=[])  # no attributes

    manager = MagicMock()
    manager.db = "default"
    manager.all.return_value = [obj_with_no_matching_attr]

    instance = MagicMock()
    instance.items = manager

    data = {}
    _apply_dict_fields(data, instance, {"items": ["nonexistent_field"]})
    assert data["items"] == []


def test_apply_dict_fields_single_object_empty_nested_still_sets_key():
    """For single objects, even if nested fields don't resolve, data[key] should be set to empty dict."""
    related_obj = MagicMock(spec=[])  # no attributes
    del related_obj.db  # ensure it's treated as single object

    instance = MagicMock()
    instance.related = related_obj

    data = {}
    _apply_dict_fields(data, instance, {"related": ["nonexistent"]})
    assert data["related"] == {}


# ============================================================================
# to_dict tests (need DB)
# ============================================================================


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def household_with_individuals(business_area, program):
    household = HouseholdFactory(business_area=business_area, program=program)
    rdi = household.registration_data_import
    IndividualFactory(business_area=business_area, program=program, household=household, registration_data_import=rdi)
    IndividualFactory(business_area=business_area, program=program, household=household, registration_data_import=rdi)
    return household


@pytest.fixture
def individual_with_household(business_area, program):
    household = HouseholdFactory(business_area=business_area, program=program)
    rdi = household.registration_data_import
    return IndividualFactory(
        business_area=business_area, program=program, household=household, registration_data_import=rdi
    )


@pytest.mark.django_db
def test_to_dict_includes_nested_fields_for_related_objects(household_with_individuals):
    result = to_dict(
        household_with_individuals,
        fields=["id"],
        dict_fields={"individuals": ["full_name", "birth_date"]},
    )

    assert "individuals" in result
    assert len(result["individuals"]) >= 2
    assert all("full_name" in ind for ind in result["individuals"])


@pytest.mark.django_db
def test_to_dict_resolves_dotted_field_paths(individual_with_household):
    result = to_dict(
        individual_with_household,
        fields=["id"],
        dict_fields={"household": ["program.name"]},
    )

    assert "household" in result
    assert "name" in result["household"]
