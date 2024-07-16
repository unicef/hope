from typing import Optional, Union, Any

import openpyxl
from django import forms
from django.core.exceptions import ValidationError
from django.core.files import File

from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PeriodicDataUpdateExportTemplateService,
)


class PeriodicDataUpdateBaseForm(forms.Form):
    individual__uuid = forms.UUIDField()
    individual_unicef_id = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()


class PeriodicDataUpdateImportService:
    def __init__(self, file: File, created_by_id: str) -> None:
        self.file = file

    def open_workbook(self):
        self.wb = openpyxl.load_workbook(self.file)
        self.ws_pdu = self.wb[PeriodicDataUpdateExportTemplateService.PDU_SHEET]
        self.ws_meta = self.wb[PeriodicDataUpdateExportTemplateService.META_SHEET]
        self.periodic_data_update_template_id: Optional[PeriodicDataUpdateTemplate] = None
        self.flexible_attributes_dict: Optional[dict[str, FlexibleAttribute]] = None

    def _read_periodic_data_update_template_object(self):
        id = self.wb.custom_doc_props[PeriodicDataUpdateExportTemplateService.PROPERTY_ID_NAME]
        if not id:
            id = self.ws_pdu[PeriodicDataUpdateExportTemplateService.ID_COLUMN].value
        if not id:
            raise ValidationError("Periodic Data Update Template ID is missing in the file")
        try:
            if isinstance(id, str):
                id = id.strip()
                id = int(id)
        except ValueError:
            raise ValidationError("Periodic Data Update Template ID must be a number")
        if not isinstance(id, int):
            raise ValidationError("Periodic Data Update Template ID must be an integer")

        self.periodic_data_update_template_id = id
        self.periodic_data_update_template = PeriodicDataUpdateTemplate.objects.filter(id=id).first()
        if not self.periodic_data_update_template:
            raise ValidationError(f"Periodic Data Update Template with ID {id} not found")

    def _read_flexible_attributes(self):
        rounds_data = self.periodic_data_update_template.rounds_data
        fields_name = [field["field"] for field in rounds_data]
        fields_name = set(fields_name)
        flexible_attributes = FlexibleAttribute.objects.filter(name__in=fields_name, type=FlexibleAttribute.PDU)
        if len(flexible_attributes) != len(fields_name):
            raise ValidationError("Some fields are missing in the flexible attributes")
        self.flexible_attributes_dict = {field.name: field for field in flexible_attributes}

    def _read_header(self):
        header = [cell.value for cell in self.ws_pdu[1]]
        return header

    def _read_rows(self):
        header = self._read_header()
        for row in self.ws_pdu.iter_rows(min_row=2, values_only=True):
            row_empty_values = []
            for value in row:
                if value == "-":
                    row_empty_values.append(None)
                else:
                    row_empty_values.append(value)

            data = dict(zip(header, row))

            form = self._build_form()(data=data)
            if not form.is_valid():
                raise ValidationError(form.errors)

    def _import_cleaned_data(self, cleaned_data: dict):
        for round in self.periodic_data_update_template.rounds_data:
            individual_uuid = cleaned_data["individual__uuid"]
            individual_unicef_id = cleaned_data["individual_unicef_id"]
            round_number_from_xlsx = cleaned_data[f"{round['field']}__round_number"]
            value_from_xlsx = cleaned_data[f"{round['field']}__round_value"]
            collection_date_from_xlsx = cleaned_data[f"{round['field']}__collection_date"]
            if value_from_xlsx is None:
                continue
            if round_number_from_xlsx != round["round_number"]:
                raise ValidationError(
                    f"Round number mismatch for field {round['field']} and individual {individual_uuid} / {individual_unicef_id}"
                )
            individual = Individual.objects.filter(uuid=individual_uuid).first()
            if not individual:
                raise ValidationError(f"Individual with UUID {individual_uuid} / {individual_unicef_id} not found")
            current_value = self._get_round_value(individual, round["field"], round["round_number"])
            if current_value and value_from_xlsx:
                raise ValidationError(
                    f"Value already exists for field {round['field']} for round {round['round_number']} and individual {individual_uuid} / {individual_unicef_id}"
                )
            self._set_round_value(
                individual, round["field"], round["round_number"], value_from_xlsx, collection_date_from_xlsx
            )

    def _get_round_value(
        self, individual: Individual, pdu_field_name: str, round_number: int
    ) -> Optional[Union[str, int, float, bool]]:
        flex_fields_data = individual.flex_fields
        field_data = flex_fields_data.get(pdu_field_name)
        if field_data:
            round_data = field_data.get(str(round_number))
            if round_data:
                return round_data.get("value")
        return None

    def _set_round_value(
        self, individual: Individual, pdu_field_name: str, round_number: int, value: Any, collection_date: Any
    ) -> None:
        flex_fields_data = individual.flex_fields
        if pdu_field_name not in flex_fields_data:
            flex_fields_data[pdu_field_name] = {}
        field_data = flex_fields_data[pdu_field_name]
        if str(round_number) not in field_data:
            field_data[str(round_number)] = {}
        round_data = field_data.get(str(round_number))
        round_data["value"] = value
        round_data["collection_date"] = collection_date

    def _build_form(self):
        form_fields_dict: dict[str, forms.Field] = {}
        for round in self.periodic_data_update_template.rounds_data:
            flexible_attribute = self.flexible_attributes_dict.get(round["field"])
            if not flexible_attribute:
                raise ValidationError(f"Flexible Attribute for field {round['field']} not found")
            form_fields_dict[f"{round['field']}__round_number"] = forms.IntegerField()
            form_fields_dict[f"{round['field']}__round_name"] = forms.CharField()
            form_fields_dict[f"{round['field']}__round_value"] = self._get_form_field_for_value(flexible_attribute)
            form_fields_dict[f"{round['field']}__collection_date"] = forms.DateField()

        return type("PeriodicDataUpdateForm", (PeriodicDataUpdateBaseForm,), form_fields_dict)

    def _get_form_field_for_value(self, flexible_attribute: FlexibleAttribute):
        if flexible_attribute.pdu_data.subtype == PeriodicFieldData.STRING:
            return forms.CharField()
        elif flexible_attribute.pdu_data.subtype == PeriodicFieldData.DECIMAL:
            return forms.DecimalField()
        elif flexible_attribute.pdu_data.subtype == PeriodicFieldData.BOOLEAN:
            return forms.BooleanField()
        elif flexible_attribute.pdu_data.subtype == PeriodicFieldData.DATE:
            return forms.DateField()
