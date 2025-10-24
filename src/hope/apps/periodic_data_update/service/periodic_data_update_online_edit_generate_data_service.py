from rest_framework.exceptions import ValidationError

from hope.apps.core.models import FlexibleAttribute
from hope.apps.periodic_data_update.service.periodic_data_update_base_service import (
    PDUDataExtractionService,
    PDURoundValueMixin,
)
from hope.apps.program.models import Program


class PDUOnlineEditGenerateDataService(PDUDataExtractionService, PDURoundValueMixin):
    def __init__(self, program: Program, filters: dict, rounds_data: list):
        super().__init__(program=program, filters=filters)
        self.rounds_data = rounds_data

    def generate_edit_data(self) -> list:
        """Generate the initial structure for the edit_data field."""
        field_names = {rd["field"] for rd in self.rounds_data}
        pdu_fields_data = {
            pdu_field.name: {
                "subtype": pdu_field.pdu_data.subtype,
                "label": pdu_field.label.get("English(EN)", ""),
            }
            for pdu_field in FlexibleAttribute.objects.filter(
                program=self.program, name__in=field_names, type=FlexibleAttribute.PDU
            )
        }

        individuals = self._get_individuals_queryset()
        edit_data = []

        for individual in individuals:
            pdu_fields = {}
            is_individual_allowed = False
            for round_info in self.rounds_data:
                pdu_field_name = round_info["field"]
                field_data = pdu_fields_data.get(pdu_field_name)
                if not field_data:
                    raise ValidationError(
                        f"PDU field '{pdu_field_name}' not found in flexible attributes for program "
                        f"'{self.program.name}'."
                    )

                round_number = round_info["round"]
                round_value = self._get_round_value(individual, pdu_field_name, round_number)
                if round_value is None:
                    is_individual_allowed = True
                pdu_fields[pdu_field_name] = {
                    "field_name": pdu_field_name,  # Needed for frontend because of snake-camel default conversion
                    "round_number": round_number,
                    "round_name": round_info["round_name"],
                    "value": round_value,
                    "collection_date": None,
                    "subtype": field_data["subtype"],
                    "label": field_data["label"],
                    "is_editable": round_value is None,
                }

            if is_individual_allowed:
                edit_data.append(
                    {
                        "individual_uuid": str(individual.pk),
                        "unicef_id": individual.unicef_id,
                        "first_name": individual.given_name,
                        "last_name": individual.family_name,
                        "pdu_fields": pdu_fields,
                    }
                )
        return edit_data
