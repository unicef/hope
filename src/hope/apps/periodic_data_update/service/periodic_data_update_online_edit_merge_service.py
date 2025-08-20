import datetime
from typing import Any

from rest_framework.exceptions import ValidationError
from django.db import transaction

from hope.apps.core.models import PeriodicFieldData
from hope.apps.household.models import Individual
from hope.apps.periodic_data_update.models import PDUOnlineEdit
from hope.apps.periodic_data_update.service.periodic_data_update_base_service import PDURoundValueMixin


class PDUOnlineEditMergeService(PDURoundValueMixin):
    def __init__(self, pdu_online_edit: PDUOnlineEdit):
        self.pdu_online_edit = pdu_online_edit

    def merge_edit_data(self) -> None:
        """Merge the data from the edit_data field into the individuals' flex_fields."""
        with transaction.atomic():
            individuals_to_update = []
            individual_ids = [item["individual_uuid"] for item in self.pdu_online_edit.edit_data]
            individuals = Individual.objects.in_bulk(individual_ids, field_name="id")

            for item in self.pdu_online_edit.edit_data:
                individual = individuals.get(item["individual_uuid"])
                if not individual:
                    raise ValidationError(f"Individual with UNICEF ID {item.get('individual_uuid')} not found.")

                for pdu_field_name, field_data in item.get("pdu_fields", {}).items():
                    value = field_data.get("value")
                    is_editable = field_data.get("is_editable")
                    if value is None or not is_editable:
                        continue

                    expected_type = field_data.get("subtype")
                    self._validate_value(value, expected_type, pdu_field_name)
                    self.set_round_value(
                        individual=individual,
                        pdu_field_name=pdu_field_name,
                        round_number=field_data["round_number"],
                        value=value,
                        collection_date=field_data["collection_date"],
                    )
                individuals_to_update.append(individual)

            if individuals_to_update:
                Individual.objects.bulk_update(individuals_to_update, ["flex_fields"])

    @staticmethod
    def _validate_value(value: Any, expected_type: str, field_name: str) -> None:
        if expected_type == PeriodicFieldData.BOOL and not isinstance(value, bool):
            raise ValidationError(f"Invalid type for field {field_name}. Expected boolean, got {type(value).__name__}.")
        if expected_type == PeriodicFieldData.DECIMAL and not isinstance(value, int | float):
            raise ValidationError(f"Invalid type for field {field_name}. Expected number, got {type(value).__name__}.")
        if expected_type == PeriodicFieldData.DATE:
            if not isinstance(value, str):
                raise ValidationError(
                    f"Invalid type for field {field_name}. Expected string for date, got {type(value).__name__}."
                )
            try:
                datetime.date.fromisoformat(value)
            except (TypeError, ValueError):
                raise ValidationError(f"Invalid date format for field {field_name}. Expected YYYY-MM-DD.")
        if expected_type == PeriodicFieldData.STRING and not isinstance(value, str):
            raise ValidationError(f"Invalid type for field {field_name}. Expected string, got {type(value).__name__}.")
