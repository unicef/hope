import re

from rest_framework.exceptions import ValidationError

from hope.apps.core.models import FlexibleAttribute
from hope.apps.household.models import Individual
from hope.apps.periodic_data_update.models import PDUXlsxTemplate, PDUOnlineEdit
from hope.apps.program.models import Program


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

def update_rounds_covered_for_template(
        pdu_template: PDUXlsxTemplate | PDUOnlineEdit,
        rounds_data: list[dict]
    ) -> None:
    field_to_round_map = {item["field"]: item["round"] for item in rounds_data}
    field_names = field_to_round_map.keys()

    pdu_fields_to_update = FlexibleAttribute.objects.filter(
        program=pdu_template.program, name__in=field_names, pdu_data__isnull=False
    ).select_related("pdu_data")

    for field in pdu_fields_to_update:
        new_round = field_to_round_map.get(field.name)
        pdu_data = field.pdu_data
        if new_round <= pdu_data.rounds_covered:
            raise ValidationError(
                f"Template for round {new_round} of field '{(field.label.get("English(EN)") or field.name)}' has already been created."
            )
        pdu_data.rounds_covered = new_round
        pdu_data.save(update_fields=["rounds_covered"])
