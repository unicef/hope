from typing import List

from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.periodic_data_update.utils import (
    field_label_to_field_name, populate_pdu_new_rounds_with_null_values)
from hct_mis_api.apps.program.models import Program


def add_pdu_fields(program: Program, label: str, subtype: str, rounds_names: List) -> None:
    flexible_attribute, _ = FlexibleAttribute.objects.get_or_create(
        label={"English(EN)": label},
        name=field_label_to_field_name(label),
        type=FlexibleAttribute.PDU,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        program=program,
    )
    flexible_attribute.pdu_data, _ = PeriodicFieldData.objects.get_or_create(
        subtype=subtype, number_of_rounds=len(rounds_names), rounds_names=rounds_names
    )
    flexible_attribute.save()
    populate_pdu_new_rounds_with_null_values(program)


def add_specific_fields_and_populate_round() -> None:
    program = Program.objects.get(id="dedece11-b654-4092-bd06-3ac4c9bdea95")
    pdu_field_data = {
        "program": program,
        "label": "valid for payment",
        "subtype": PeriodicFieldData.BOOL,
        "rounds_names": [
            "July 2024 Payment",
            "August 2024 Payment",
            "September 2024 Payment",
            "October 2024 Payment",
            "November 2024 Payment",
            "December 2024 Payment",
            "January 2025 Payment",
            "February 2025 Payment",
            "March 2025 Payment",
            "April 2025 Payment",
            "May 2025 Payment",
            "June 2025 Payment",
        ],
    }
    add_pdu_fields(**pdu_field_data)

    # populate 1st round
    individuals = []
    for ind in Individual.all_merge_status_objects.filter(program=program):
        ind.flex_fields[field_label_to_field_name(pdu_field_data["label"])]["1"]["value"] = True
        ind.flex_fields[field_label_to_field_name(pdu_field_data["label"])]["1"]["collection_date"] = "2024-07-31"
        individuals.append(ind)
    Individual.all_merge_status_objects.bulk_update(individuals, ["flex_fields"])
