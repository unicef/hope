from typing import Any, Dict

from graphql import GraphQLError

from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.program.models import Program


class FlexibleAttributeForPDUService:
    def __init__(self, program: Program, pdu_fields: list) -> None:
        self.program: Program = program
        self.pdu_fields: list = pdu_fields

    @staticmethod
    def _validate_pdu_data(pdu_data: Dict) -> None:
        if pdu_data and pdu_data["number_of_rounds"] != len(pdu_data["rounds_names"]):
            raise GraphQLError("Number of rounds does not match the number of round names")

    def create_pdu_flex_attribute(self, pdu_field: dict) -> FlexibleAttribute:
        pdu_data = pdu_field.pop("pdu_data")
        self._validate_pdu_data(pdu_data)
        pdu_data_object = PeriodicFieldData.objects.create(**pdu_data)
        return FlexibleAttribute.objects.create(
            **pdu_field,
            type=FlexibleAttribute.PDU,
            program=self.program,
            pdu_data=pdu_data_object,
        )

    def create_pdu_flex_attributes(self) -> None:
        for pdu_field in self.pdu_fields:
            self.create_pdu_flex_attribute(pdu_field)

    def update_pdu_flex_attribute(self, pdu_field: dict, flexible_attribute_id: Any) -> None:
        pdu_data = pdu_field.pop("pdu_data", {})
        self._validate_pdu_data(pdu_data)
        flexible_attribute_object = FlexibleAttribute.objects.get(id=flexible_attribute_id)
        pdu_data_object = flexible_attribute_object.pdu_data
        for key, value in pdu_data.items():
            setattr(pdu_data_object, key, value)
        pdu_data_object.save()
        for key, value in pdu_field.items():
            setattr(flexible_attribute_object, key, value)
        flexible_attribute_object.save()

    def delete_pdu_flex_attributes(self, flexible_attribute_ids_to_preserve: list) -> None:
        FlexibleAttribute.objects.filter(program=self.program, type=FlexibleAttribute.PDU).exclude(
            id__in=flexible_attribute_ids_to_preserve
        ).delete()

    def update_pdu_flex_attributes(self) -> None:
        if self.program.registration_imports.exists():
            raise GraphQLError("Cannot update PDU fields for a program with RDIs.")
        flexible_attribute_ids_to_preserve = []
        for pdu_field in self.pdu_fields:
            if flexible_attribute_id := pdu_field.pop("id", None):
                self.update_pdu_flex_attribute(pdu_field, flexible_attribute_id)
                flexible_attribute_ids_to_preserve.append(flexible_attribute_id)
            else:
                flexible_attribute_ids_to_preserve.append(self.create_pdu_flex_attribute(pdu_field).id)

        self.delete_pdu_flex_attributes(flexible_attribute_ids_to_preserve)
