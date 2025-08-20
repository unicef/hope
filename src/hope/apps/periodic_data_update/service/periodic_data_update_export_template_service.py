from tempfile import NamedTemporaryFile

from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.db import transaction

import openpyxl
from openpyxl.packaging.custom import StringProperty

from hope.apps.core.models import FileTemp
from hope.apps.household.models import Individual
from hope.apps.periodic_data_update.models import PDUXlsxTemplate
from hope.apps.periodic_data_update.service.periodic_data_update_base_service import PDUDataExtractionService, \
    PDURoundValueMixin


class PDUXlsxExportTemplateService(PDUDataExtractionService, PDURoundValueMixin):
    PDU_SHEET = "Periodic Data Update"
    META_SHEET = "Meta"
    META_ID_ADDRESS = "B1"
    PROPERTY_ID_NAME = "pdu_template_id"

    def __init__(self, periodic_data_update_template: PDUXlsxTemplate):
        self.periodic_data_update_template = periodic_data_update_template
        self.rounds_data = periodic_data_update_template.rounds_data
        super().__init__(
            program=periodic_data_update_template.program,
            filters=periodic_data_update_template.filters,
        )

    def generate_workbook(self) -> openpyxl.Workbook:
        try:
            with transaction.atomic():
                self._create_workbook()
                self._add_meta()
                self.ws_pdu.append(self._generate_header())
                for round_info_data in self.rounds_data:
                    round_info_data["number_of_records"] = 0
                self.periodic_data_update_template.number_of_records = 0
                queryset = self._get_individuals_queryset()
                for individual in queryset:
                    row = self._generate_row(individual)
                    if row:
                        self.periodic_data_update_template.number_of_records += 1
                        self.ws_pdu.append(row)
                return self.wb
        except Exception:
            self.periodic_data_update_template.status = PDUXlsxTemplate.Status.FAILED
            self.periodic_data_update_template.save()
            raise

    def save_xlsx_file(self) -> None:
        filename = f"Periodic Data Update Template {self.periodic_data_update_template.pk}.xlsx"
        with NamedTemporaryFile() as tmp:
            xlsx_obj = FileTemp(
                object_id=self.periodic_data_update_template.pk,
                content_type=get_content_type_for_model(self.periodic_data_update_template),
                created_by=self.periodic_data_update_template.created_by,
            )
            self.wb.save(tmp.name)
            tmp.seek(0)
            xlsx_obj.file.save(filename, File(tmp))
            self.periodic_data_update_template.file = xlsx_obj
            self.periodic_data_update_template.status = PDUXlsxTemplate.Status.EXPORTED
            self.periodic_data_update_template.save()

    def _create_workbook(self) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws_pdu = wb.active
        ws_pdu.title = PDUXlsxExportTemplateService.PDU_SHEET
        self.wb = wb
        self.ws_pdu = ws_pdu
        self.ws_meta = wb.create_sheet(PDUXlsxExportTemplateService.META_SHEET)
        return wb

    def _add_meta(self) -> None:
        self.ws_meta["A1"] = "Periodic Data Update Template ID"
        self.ws_meta[self.META_ID_ADDRESS] = self.periodic_data_update_template.pk
        self.wb.custom_doc_props.append(
            StringProperty(name=self.PROPERTY_ID_NAME, value=str(self.periodic_data_update_template.pk))
        )

    def _generate_header(self) -> list[str]:
        header = [
            "individual__uuid",
            "individual_unicef_id",
            "first_name",
            "last_name",
        ]
        for round_info_data in self.rounds_data:
            header.extend(
                [
                    f"{round_info_data['field']}__round_number",
                    f"{round_info_data['field']}__round_name",
                    f"{round_info_data['field']}__round_value",
                    f"{round_info_data['field']}__collection_date",
                ]
            )
        return header

    def _generate_row(self, individual: Individual) -> list[str] | None:
        individual_uuid = individual.pk
        individual_unicef_id = individual.unicef_id
        first_name = individual.given_name
        last_name = individual.family_name
        row = [str(individual_uuid), individual_unicef_id, first_name, last_name]
        is_individual_allowed = False
        for round_info_data in self.rounds_data:
            pdu_field_name = round_info_data["field"]
            round_number = round_info_data["round"]
            round_name = round_info_data["round_name"]
            round_value = self._get_round_value(individual, pdu_field_name, round_number)
            if round_value is None:
                round_info_data["number_of_records"] = round_info_data["number_of_records"] + 1
                row.extend([round_number, round_name, "", ""])
            else:
                row.extend([round_number, round_name, "-", "-"])
            is_individual_allowed = is_individual_allowed or round_value is None
        if not is_individual_allowed:
            return None
        return row
