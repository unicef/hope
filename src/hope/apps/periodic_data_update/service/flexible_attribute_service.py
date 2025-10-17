from typing import Any

from rest_framework.exceptions import ValidationError

from hope.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hope.apps.payment.models import PaymentPlan
from hope.apps.periodic_data_update.signals import (
    increment_periodic_field_version_cache,
)
from hope.apps.periodic_data_update.utils import field_label_to_field_name
from hope.apps.program.models import Program


class FlexibleAttributeForPDUService:
    def __init__(self, program: Program, pdu_fields: list) -> None:
        self.program: Program = program
        self.pdu_fields: list = pdu_fields

    @staticmethod
    def _validate_pdu_data(pdu_data: dict) -> None:
        if pdu_data["number_of_rounds"] != len(pdu_data["rounds_names"]):
            raise ValidationError("Number of rounds does not match the number of round names.")

    def create_pdu_flex_attribute(self, pdu_field: dict) -> FlexibleAttribute:
        pdu_data = pdu_field.pop("pdu_data")
        self._validate_pdu_data(pdu_data)
        pdu_data_object = PeriodicFieldData.objects.create(**pdu_data)
        return FlexibleAttribute.objects.create(
            **pdu_field,
            type=FlexibleAttribute.PDU,
            program=self.program,
            pdu_data=pdu_data_object,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )

    def create_pdu_flex_attributes(self) -> None:
        self._populate_names_and_labels()
        self._validate_pdu_names_in_batch()
        for pdu_field in self.pdu_fields:
            self.create_pdu_flex_attribute(pdu_field)

    def update_pdu_flex_attribute(self, pdu_field: dict, flexible_attribute_id: Any) -> None:
        pdu_data = pdu_field.pop("pdu_data")
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
        # incr cache key (since it's bulk action)
        business_area_slug = self.program.business_area.slug
        program_id = self.program.id
        increment_periodic_field_version_cache(business_area_slug, program_id)

    def update_pdu_flex_attributes(self) -> None:
        self._populate_names_and_labels()
        self._validate_pdu_names_in_batch()
        flexible_attribute_ids_to_preserve = []
        for pdu_field in self.pdu_fields:
            if flexible_attribute_id := pdu_field.pop("id", None):
                self.update_pdu_flex_attribute(pdu_field, flexible_attribute_id)
                flexible_attribute_ids_to_preserve.append(flexible_attribute_id)
            else:
                flexible_attribute_ids_to_preserve.append(self.create_pdu_flex_attribute(pdu_field).id)

        self.delete_pdu_flex_attributes(flexible_attribute_ids_to_preserve=flexible_attribute_ids_to_preserve)

    def update_pdu_flex_attributes_in_program_update(self) -> None:
        if (
            self.program.registration_imports.exists()
            or PaymentPlan.objects.filter(program_cycle__program=self.program).exists()
        ):
            self.increase_pdu_rounds_for_program_with_rdi()
        else:
            self.update_pdu_flex_attributes()

    def increase_pdu_rounds_for_program_with_rdi(self) -> None:
        for pdu_field in self.pdu_fields:
            if flexible_attribute_id := pdu_field.pop("id", None):
                flexible_attribute_object = FlexibleAttribute.objects.get(id=flexible_attribute_id)
                pdu_data_object = flexible_attribute_object.pdu_data

                pdu_data = pdu_field.pop("pdu_data")

                if pdu_data["number_of_rounds"] == pdu_data_object.number_of_rounds:
                    continue

                self._validate_pdu_data(pdu_data)
                self._validate_pdu_data_for_program_with_rdi(pdu_data_object, pdu_data)

                pdu_data_object.number_of_rounds = pdu_data["number_of_rounds"]
                pdu_data_object.rounds_names = pdu_data["rounds_names"]
                pdu_data_object.save()

    def _validate_pdu_names_in_batch(self) -> None:
        pdu_names = [pdu_field["name"] for pdu_field in self.pdu_fields]
        if len(pdu_names) != len(set(pdu_names)):
            raise ValidationError("Time Series Field names must be unique.")

    def _populate_names_and_labels(self) -> None:
        for pdu_field in self.pdu_fields:
            pdu_field["name"] = field_label_to_field_name(pdu_field["label"])
            pdu_field["label"] = {"English(EN)": pdu_field["label"]}

    @staticmethod
    def _validate_pdu_data_for_program_with_rdi(pdu_data_object: PeriodicFieldData, pdu_data: dict) -> None:
        current_number_of_rounds = pdu_data_object.number_of_rounds
        current_rounds_names = pdu_data_object.rounds_names
        new_number_of_rounds = pdu_data["number_of_rounds"]
        new_rounds_names = pdu_data["rounds_names"]
        if new_number_of_rounds <= current_number_of_rounds:
            raise ValidationError("It is not possible to decrease the number of rounds for a Program with RDI or TP.")
        if current_rounds_names != new_rounds_names[:current_number_of_rounds]:
            raise ValidationError(
                "It is not possible to change the names of existing rounds for a Program with RDI or TP."
            )
