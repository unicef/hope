import pytest

from extras.test_utils.factories import BusinessAreaFactory, HouseholdFactory, ProgramFactory
from hope.apps.core.management.commands.demo_data.flex_fields import generate_household_flex_fields
from hope.apps.core.utils import serialize_flex_attributes
from hope.models import FlexibleAttribute, Household


@pytest.fixture
def test_program(db):
    business_area = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    return ProgramFactory(business_area=business_area, name="Test Program")


def test_generate_household_flex_fields_creates_household_attributes(test_program):
    generate_household_flex_fields()

    households_flex_fields = serialize_flex_attributes()["households"]
    assert set(households_flex_fields) == {
        "hh_total_eligible_ind_h_f",
        "total_dwellers_h_f",
        "living_situation_h_f",
    }
    assert households_flex_fields["hh_total_eligible_ind_h_f"]["type"] == FlexibleAttribute.INTEGER
    assert households_flex_fields["hh_total_eligible_ind_h_f"]["label"] == {
        "English(EN)": "HH Total Eligible Individuals"
    }
    assert {c["value"] for c in households_flex_fields["living_situation_h_f"]["choices"]} == {
        "owner",
        "renter",
        "hosted",
    }
    assert not serialize_flex_attributes()["individuals"]


def test_generate_household_flex_fields_fills_test_program_households(test_program):
    in_program = HouseholdFactory(program=test_program, business_area=test_program.business_area, size=3)
    other_program = ProgramFactory(business_area=test_program.business_area, name="Other Program")
    outside_program = HouseholdFactory(program=other_program, business_area=test_program.business_area)

    generate_household_flex_fields()

    assert Household.objects.get(pk=in_program.pk).flex_fields == {
        "hh_total_eligible_ind_h_f": 1,
        "total_dwellers_h_f": 3,
        "living_situation_h_f": "renter",
    }
    assert Household.objects.get(pk=outside_program.pk).flex_fields == {}
