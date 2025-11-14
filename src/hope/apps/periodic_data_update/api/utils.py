from typing import Any

from rest_framework import serializers

from hope.apps.core.models import FlexibleAttribute
from hope.apps.program.models import Program


def add_round_names_to_rounds_data(rounds_data: list[dict[str, Any]], program: Program) -> None:
    """Add round_name to each element in rounds_data by fetching it from FlexibleAttribute."""
    for round_data in rounds_data:
        field_name = round_data.get("field")
        round_number = round_data.get("round")

        try:
            flex_attribute = FlexibleAttribute.objects.select_related("pdu_data").get(name=field_name, program=program)
            round_index = round_number - 1
            round_data["round_name"] = flex_attribute.pdu_data.rounds_names[round_index]
        except FlexibleAttribute.DoesNotExist:
            raise serializers.ValidationError(
                {"rounds_data": f"Field '{field_name}' does not exist in the program '{program.name}'."}
            )
