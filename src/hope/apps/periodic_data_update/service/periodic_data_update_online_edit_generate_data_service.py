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
        field_subtype_map = {
            pdu_field.name: pdu_field.pdu_data.subtype
            for pdu_field in FlexibleAttribute.objects.filter(
                program=self.program, name__in=field_names, type=FlexibleAttribute.PDU
            )
        }

        individuals = self.get_individuals_queryset()
        edit_data = []

        for individual in individuals:
            pdu_fields = {}
            is_individual_allowed = False
            for round_info in self.rounds_data:
                pdu_field_name = round_info["field"]
                subtype = field_subtype_map.get(pdu_field_name)
                if not subtype:
                    raise ValidationError(
                        f"PDU field '{pdu_field_name}' not found in flexible attributes for program '{self.program.name}'."
                    )

                round_number = round_info["round"]
                round_value = self._get_round_value(individual, pdu_field_name, round_number)

                if round_value is None:
                    is_individual_allowed = True
                    pdu_fields[pdu_field_name] = {
                        "round_number": round_number,
                        "round_name": round_info["round_name"],
                        "value": None,
                        "subtype": subtype,
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
