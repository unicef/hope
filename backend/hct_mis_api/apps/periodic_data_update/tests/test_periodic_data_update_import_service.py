from tempfile import NamedTemporaryFile
from typing import Any

from django.test import TestCase

from django.core.files import File
import openpyxl
from freezegun import freeze_time

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import FEMALE, MALE
from hct_mis_api.apps.payment.fixtures import PaymentFactory
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate, PeriodicDataUpdateUpload
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PeriodicDataUpdateExportTemplateService,
)
from hct_mis_api.apps.periodic_data_update.service.periodic_data_update_import_service import (
    PeriodicDataUpdateImportService,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from openpyxl.packaging.custom import StringProperty
from hct_mis_api.apps.sanction_list.fixtures import SanctionListIndividualFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory


def create_flexible_attribute(
    name: str, subtype: str, number_of_rounds: int, rounds_names: list[str]
) -> FlexibleAttribute:
    flexible_attribute = FlexibleAttribute.objects.create(
        name=name, type=FlexibleAttribute.PDU, associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=subtype, number_of_rounds=number_of_rounds, rounds_names=rounds_names
    )
    flexible_attribute.save()
    return flexible_attribute


def add_pdu_data_to_xlsx(periodic_data_update_template, rows: list[list[Any]]):
    wb = openpyxl.load_workbook(periodic_data_update_template.file.file)
    ws_pdu = wb[PeriodicDataUpdateExportTemplateService.PDU_SHEET]
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            ws_pdu.cell(row=row_index + 2, column=col_index + 7, value=value)
    tmp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(tmp_file.name)
    tmp_file.seek(0)
    return tmp_file


class TestPeriodicDataUpdateImportService(TestCase):
    rdi = None
    business_area = None
    program = None

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(name="Test Program", status=Program.DRAFT, business_area=cls.business_area)
        cls.rdi = RegistrationDataImportFactory()
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program_id": cls.program.pk,
                "registration_data_import": cls.rdi,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program_id": cls.program.pk,
                    "registration_data_import": cls.rdi,
                },
            ],
        )
        cls.individual = cls.individuals[0]
        cls.string_attribute = create_flexible_attribute(
            name="string_attribute", subtype=PeriodicFieldData.STRING, number_of_rounds=1, rounds_names=["May"]
        )
        cls.decimal_attribute = create_flexible_attribute(
            name="decimal_attribute", subtype=PeriodicFieldData.DECIMAL, number_of_rounds=1, rounds_names=["May"]
        )
        cls.boolean_attribute = create_flexible_attribute(
            name="boolean_attribute", subtype=PeriodicFieldData.BOOLEAN, number_of_rounds=1, rounds_names=["May"]
        )
        cls.date_attribute = create_flexible_attribute(
            name="date_attribute", subtype=PeriodicFieldData.DATE, number_of_rounds=1, rounds_names=["May"]
        )

    def prepare_test_data(self, rounds_data: list, rows: list) -> tuple:
        periodic_data_update_template = PeriodicDataUpdateTemplate.objects.create(
            program=self.program,
            business_area=self.business_area,
            filters=dict(),
            rounds_data=rounds_data,
        )
        service = PeriodicDataUpdateExportTemplateService(periodic_data_update_template)
        service.generate_workbook()
        service.save_xlsx_file()
        tmp_file = add_pdu_data_to_xlsx(periodic_data_update_template, rows)
        periodic_data_update_upload = PeriodicDataUpdateUpload(
            template=periodic_data_update_template,
            created_by=periodic_data_update_template.created_by,
        )
        tmp_file.seek(0)
        periodic_data_update_upload.file.save("test.xlsx", File(tmp_file))
        periodic_data_update_upload.save()
        tmp_file.close()
        return periodic_data_update_template, periodic_data_update_upload

    def test_full_flow(self):
        periodic_data_update_template = PeriodicDataUpdateTemplate.objects.create(
            program=self.program,
            business_area=self.business_area,
            filters=dict(),
            rounds_data=[
                {
                    "field": self.string_attribute.name,
                    "round": 1,
                    "round_name": self.string_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
        )
        service = PeriodicDataUpdateExportTemplateService(periodic_data_update_template)
        service.generate_workbook()
        service.save_xlsx_file()
        periodic_data_update_template_from_xlsx = (
            PeriodicDataUpdateImportService.read_periodic_data_update_template_object(
                periodic_data_update_template.file.file
            )
        )
        self.assertEqual(periodic_data_update_template_from_xlsx.pk, periodic_data_update_template.pk)

    def test_import_data_string(self):
        flexible_attribute = self.string_attribute
        periodic_data_update_template, periodic_data_update_upload = self.prepare_test_data(
            [
                {
                    "field": flexible_attribute.name,
                    "round": 1,
                    "round_name": flexible_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
            [["Test Value", "2021-05-02"]],
        )
        service = PeriodicDataUpdateImportService(periodic_data_update_upload)
        service.import_data()
        self.assertEqual(periodic_data_update_upload.status, PeriodicDataUpdateUpload.Status.SUCCESSFUL)
        self.assertEqual(periodic_data_update_upload.error_message, None)
        self.individual.refresh_from_db()
        self.assertEqual(self.individual.flex_fields[flexible_attribute.name]["1"]["value"], "Test Value")
        self.assertEqual(self.individual.flex_fields[flexible_attribute.name]["1"]["collection_date"], "2021-05-02")

    def test_import_data_decimal(self):
        flexible_attribute = self.decimal_attribute
        periodic_data_update_template, periodic_data_update_upload = self.prepare_test_data(
            [
                {
                    "field": flexible_attribute.name,
                    "round": 1,
                    "round_name": flexible_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
            [["20.456", "2021-05-02"]],
        )
        service = PeriodicDataUpdateImportService(periodic_data_update_upload)
        service.import_data()
        self.assertEqual(periodic_data_update_upload.status, PeriodicDataUpdateUpload.Status.SUCCESSFUL)
        self.assertEqual(periodic_data_update_upload.error_message, None)
        self.individual.refresh_from_db()
        self.assertEqual(self.individual.flex_fields[flexible_attribute.name]["1"]["value"], "20.456")
        self.assertEqual(self.individual.flex_fields[flexible_attribute.name]["1"]["collection_date"], "2021-05-02")

    def test_import_data_boolean(self):
        flexible_attribute = self.boolean_attribute
        periodic_data_update_template, periodic_data_update_upload = self.prepare_test_data(
            [
                {
                    "field": flexible_attribute.name,
                    "round": 1,
                    "round_name": flexible_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
            [[True, "2021-05-02"]],
        )
        service = PeriodicDataUpdateImportService(periodic_data_update_upload)
        service.import_data()
        self.assertEqual(periodic_data_update_upload.status, PeriodicDataUpdateUpload.Status.SUCCESSFUL)
        self.assertEqual(periodic_data_update_upload.error_message, None)
        self.individual.refresh_from_db()
        self.assertEqual(self.individual.flex_fields[flexible_attribute.name]["1"]["value"], True)
        self.assertEqual(self.individual.flex_fields[flexible_attribute.name]["1"]["collection_date"], "2021-05-02")

    def test_import_data_date(self):
        flexible_attribute = self.date_attribute
        periodic_data_update_template, periodic_data_update_upload = self.prepare_test_data(
            [
                {
                    "field": flexible_attribute.name,
                    "round": 1,
                    "round_name": flexible_attribute.pdu_data.rounds_names[0],
                    "number_of_records": 0,
                }
            ],
            [["1996-06-21", "2021-05-02"]],
        )
        service = PeriodicDataUpdateImportService(periodic_data_update_upload)
        service.import_data()
        self.assertEqual(periodic_data_update_upload.status, PeriodicDataUpdateUpload.Status.SUCCESSFUL)
        self.assertEqual(periodic_data_update_upload.error_message, None)
        self.individual.refresh_from_db()
        self.assertEqual(self.individual.flex_fields[flexible_attribute.name]["1"]["value"], "1996-06-21")
        self.assertEqual(self.individual.flex_fields[flexible_attribute.name]["1"]["collection_date"], "2021-05-02")
