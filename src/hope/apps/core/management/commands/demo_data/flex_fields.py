from extras.test_utils.factories import (
    FlexibleAttributeChoiceFactory,
    FlexibleAttributeFactory,
    FlexibleAttributeGroupFactory,
)
from hope.models import FlexibleAttribute, Household, Program

HOUSEHOLD_FLEX_FIELDS = (
    ("hh_total_eligible_ind_h_f", FlexibleAttribute.INTEGER, "HH Total Eligible Individuals"),
    ("total_dwellers_h_f", FlexibleAttribute.INTEGER, "Total Dwellers"),
    ("living_situation_h_f", FlexibleAttribute.SELECT_ONE, "Living Situation"),
)
LIVING_SITUATION_CHOICES = (
    ("owner", "Owner"),
    ("renter", "Renter"),
    ("hosted", "Hosted"),
)


def generate_household_flex_fields() -> None:
    """Create household flex attributes and fill them in for Test Program households.

    Makes the "Additional Registration Information" section non-empty so household
    flex fields can be edited through data-change grievance tickets locally.
    """
    group = FlexibleAttributeGroupFactory(
        name="additional_registration_info_h",
        label={"English(EN)": "Additional Registration Information"},
    )
    attributes = {
        name: FlexibleAttributeFactory(
            name=name,
            type=field_type,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
            label={"English(EN)": label},
            group=group,
        )
        for name, field_type, label in HOUSEHOLD_FLEX_FIELDS
    }
    for name, label in LIVING_SITUATION_CHOICES:
        choice = FlexibleAttributeChoiceFactory(
            list_name="living_situation",
            name=name,
            label={"English(EN)": label},
        )
        choice.flex_attributes.add(attributes["living_situation_h_f"])

    program = Program.objects.get(business_area__slug="afghanistan", name="Test Program")
    for household in Household.objects.filter(program=program):
        household.flex_fields = {
            "hh_total_eligible_ind_h_f": 1,
            "total_dwellers_h_f": household.size or 1,
            "living_situation_h_f": "renter",
        }
        household.save(update_fields=["flex_fields"])
