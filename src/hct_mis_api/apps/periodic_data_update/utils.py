import re

from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.program.models import Program


def field_label_to_field_name(input_string: str) -> str:
    """
    Convert a field label to a field name.
    Change " " into "_", remove special characters and convert to lowercase.
    """

    input_string = input_string.replace(" ", "_")
    input_string = re.sub(r"[^\w]", "", input_string)
    input_string = re.sub(r"__+", "_", input_string)
    input_string = input_string.strip("_")
    return input_string.lower()


def populate_pdu_with_null_values(program: Program, current_flex_fields: dict | None = None) -> dict:
    """
    Populate the PDU with null values for all the flexible attributes.
    """
    current_flex_fields = {} if current_flex_fields is None else current_flex_fields
    periodic_data_fields = FlexibleAttribute.objects.filter(program=program, type=FlexibleAttribute.PDU).values_list(
        "name", "pdu_data__number_of_rounds"
    )
    flex_fields_dict = {
        pdu_field[0]: {str(round_number): {"value": None} for round_number in range(1, pdu_field[1] + 1)}
        for pdu_field in periodic_data_fields
    }

    for field_name, rounds_dict in flex_fields_dict.items():
        if field_name not in current_flex_fields:
            current_flex_fields[field_name] = rounds_dict
        else:
            for round_number, round_data in rounds_dict.items():
                if round_number not in current_flex_fields[field_name]:
                    current_flex_fields[field_name][round_number] = round_data
    return current_flex_fields


def populate_pdu_new_rounds_with_null_values(program: Program) -> None:
    individuals = []
    for ind in Individual.all_merge_status_objects.filter(program=program):
        populate_pdu_with_null_values(program, ind.flex_fields)
        individuals.append(ind)
    Individual.all_merge_status_objects.bulk_update(individuals, ["flex_fields"])
