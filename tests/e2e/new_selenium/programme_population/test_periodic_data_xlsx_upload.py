from pathlib import Path

import openpyxl
import pytest

from e2e.new_selenium.programme_population.conftest import (
    PDU_FORM_ERRORS,
    STATUS_CONTAINER,
    exported_template,
    open_pdu_tab,
    prepare_xlsx_file,
    rounds_data,
    update_cell,
    upload_xlsx,
)
from extras.test_utils.factories import PDUXlsxTemplateFactory, PDUXlsxUploadFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PDUXlsxExportTemplateService,
)
from hope.models import FlexibleAttribute, Individual, PDUXlsxUpload, Program

pytestmark = pytest.mark.django_db()

PDU_UPLOAD_ERROR = 'div[data-cy="pdu-upload-error"]'


@pytest.fixture
def valid_xlsx(individual: Individual, string_attribute: FlexibleAttribute, tmp_path: Path) -> Path:
    return prepare_xlsx_file(string_attribute, [["Test Value", "2021-05-02"]], tmp_path / "valid.xlsx")


@pytest.fixture
def invalid_date_xlsx(individual: Individual, date_attribute: FlexibleAttribute, tmp_path: Path) -> Path:
    return prepare_xlsx_file(date_attribute, [["Test Value", "2021-05-02"]], tmp_path / "invalid_date.xlsx")


@pytest.fixture
def unknown_template_xlsx(
    individual: Individual, string_attribute: FlexibleAttribute, program: Program, tmp_path: Path
) -> Path:
    template = exported_template(program, string_attribute)
    workbook = openpyxl.load_workbook(template.file.file)
    del workbook.custom_doc_props[PDUXlsxExportTemplateService.PROPERTY_ID_NAME]
    workbook[PDUXlsxExportTemplateService.META_SHEET][PDUXlsxExportTemplateService.META_ID_ADDRESS] = "-1"
    path = tmp_path / "unknown_template.xlsx"
    workbook.save(path)
    return path


@pytest.fixture
def successful_upload(program: Program, string_attribute: FlexibleAttribute) -> PDUXlsxUpload:
    template = PDUXlsxTemplateFactory(
        program=program,
        business_area=program.business_area,
        filters={},
        rounds_data=rounds_data(string_attribute),
    )
    return PDUXlsxUploadFactory(template=template, status=PDUXlsxUpload.Status.SUCCESSFUL)


def test_upload_xlsx_updates_individual(
    valid_xlsx: Path,
    individual: Individual,
    string_attribute: FlexibleAttribute,
    program: Program,
    login: HopeTestBrowser,
) -> None:
    upload_xlsx(login, program, valid_xlsx)

    login.wait_for_element_visible('td[data-cy^="update-status-"]')
    upload = PDUXlsxUpload.objects.get()
    login.assert_text("Successful", update_cell("status", upload))
    assert upload.status == PDUXlsxUpload.Status.SUCCESSFUL
    assert upload.error_message is None
    individual.refresh_from_db()
    assert individual.flex_fields[string_attribute.name]["1"] == {
        "value": "Test Value",
        "collection_date": "2021-05-02",
    }


def test_upload_xlsx_with_invalid_value_shows_form_errors(
    invalid_date_xlsx: Path, program: Program, login: HopeTestBrowser
) -> None:
    upload_xlsx(login, program, invalid_date_xlsx)

    login.assert_text("Failed", STATUS_CONTAINER)
    upload = PDUXlsxUpload.objects.get()
    assert upload.status == PDUXlsxUpload.Status.FAILED
    login.assert_text("Failed", update_cell("status", upload))
    login.click(f'button[data-cy="update-details-btn-{upload.pk}"]')
    login.assert_exact_text("Row: 2\ntest_date_attribute__round_value\nEnter a valid date.", PDU_FORM_ERRORS)


def test_upload_xlsx_for_unknown_template_shows_error(
    unknown_template_xlsx: Path, program: Program, login: HopeTestBrowser
) -> None:
    upload_xlsx(login, program, unknown_template_xlsx)

    login.assert_exact_text(
        "Error uploading file: Periodic Data Update Template with ID -1 not found", PDU_UPLOAD_ERROR
    )
    assert not PDUXlsxUpload.objects.exists()


def test_uploads_list_shows_upload(successful_upload: PDUXlsxUpload, program: Program, login: HopeTestBrowser) -> None:
    open_pdu_tab(login, program, "offline-edits")

    login.assert_text(str(successful_upload.pk), update_cell("id", successful_upload))
    login.assert_text(str(successful_upload.template.pk), update_cell("template", successful_upload))
    login.assert_text(f"{successful_upload.created_at:%-d %b %Y}", update_cell("created-at", successful_upload))
    login.assert_text(successful_upload.created_by.get_full_name(), update_cell("created-by", successful_upload))
    login.assert_text("Successful", update_cell("status", successful_upload))
