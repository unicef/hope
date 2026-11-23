from pathlib import Path
from typing import Any

import openpyxl
import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.periodic_data_update.service.periodic_data_update_export_template_service import (
    PDUXlsxExportTemplateService,
)
from hope.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hope.models import (
    BusinessArea,
    FlexibleAttribute,
    Individual,
    PDUXlsxTemplate,
    PDUXlsxUpload,
    PeriodicFieldData,
    Program,
    RegistrationDataImport,
)

BUTTON_IMPORT = 'button[data-cy="button-import"]'
DIALOG_IMPORT = 'div[data-cy="dialog-import"]'
FILE_INPUT = 'input[data-cy="file-input"]'
BUTTON_IMPORT_SUBMIT = 'button[data-cy="button-import-submit"]'
STATUS_CONTAINER = '[data-cy="status-container"]'
PDU_FORM_ERRORS = 'div[data-cy="pdu-form-errors"]'


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    beneficiary_group = BeneficiaryGroupFactory(
        name="Main Menu",
        group_label="Items Group",
        group_label_plural="Items Groups",
        member_label="Item",
        member_label_plural="Items",
    )
    return ProgramFactory(
        name="Test Online Template Program",
        code="OTPL",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
    )


def create_pdu_attribute(program: Program, label: str, subtype: str) -> FlexibleAttribute:
    flexible_attribute = FlexibleAttribute.objects.create(
        label={"English(EN)": label},
        name=field_label_to_field_name(label),
        type=FlexibleAttribute.PDU,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        program=program,
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=subtype, number_of_rounds=1, rounds_names=["Round 1"]
    )
    flexible_attribute.save()
    return flexible_attribute


@pytest.fixture
def string_attribute(program: Program) -> FlexibleAttribute:
    return create_pdu_attribute(program, "Test String Attribute", FlexibleAttribute.STRING)


@pytest.fixture
def date_attribute(program: Program) -> FlexibleAttribute:
    return create_pdu_attribute(program, "Test Date Attribute", FlexibleAttribute.DATE)


@pytest.fixture
def individual(program: Program, business_area: BusinessArea, string_attribute: FlexibleAttribute) -> Individual:
    rdi = RegistrationDataImportFactory(status=RegistrationDataImport.MERGED, program=program)
    hoh = IndividualFactory(
        unicef_id="IND-00-0000.0001",
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
    )
    HouseholdFactory(
        business_area=business_area, program_id=program.pk, registration_data_import=rdi, head_of_household=hoh
    )
    populate_pdu_with_null_values(program, hoh.flex_fields)
    hoh.save()
    hoh.refresh_from_db()
    return hoh


def rounds_data(attribute: FlexibleAttribute) -> list[dict[str, Any]]:
    return [
        {
            "field": attribute.name,
            "round": 1,
            "round_name": attribute.pdu_data.rounds_names[0],
            "number_of_records": 0,
        }
    ]


def exported_template(program: Program, attribute: FlexibleAttribute) -> PDUXlsxTemplate:
    template = PDUXlsxTemplate.objects.create(
        program=program,
        business_area=program.business_area,
        filters={},
        rounds_data=rounds_data(attribute),
    )
    service = PDUXlsxExportTemplateService(template)
    service.generate_workbook()
    service.save_xlsx_file()
    return template


def prepare_xlsx_file(attribute: FlexibleAttribute, rows: list[list[Any]], path: Path) -> Path:
    """Export a template for `attribute` and fill its PDU sheet with `rows` (value, collection date)."""
    template = exported_template(attribute.program, attribute)
    workbook = openpyxl.load_workbook(template.file.file)
    sheet = workbook[PDUXlsxExportTemplateService.PDU_SHEET]
    for row_index, row in enumerate(rows, start=2):
        for col_index, value in enumerate(row, start=7):
            sheet.cell(row=row_index, column=col_index, value=value)
    workbook.save(path)
    return path


def individuals_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/population/individuals"


def open_pdu_tab(browser: HopeTestBrowser, list_url: str, subtab: str) -> None:
    """Open the periodic data updates tab of the `list_url` page on `subtab` (offline-templates, offline-edits, ...)."""
    browser.open(f"{list_url}?tab=periodic-data-updates&subtab={subtab}")
    browser.wait_for_element_visible(f'button[data-cy="pdu-{subtab}"][aria-selected="true"]')


def update_cell(column: str, upload: PDUXlsxUpload) -> str:
    return f'td[data-cy="update-{column}-{upload.pk}"]'


def upload_xlsx(browser: HopeTestBrowser, list_url: str, path: Path) -> None:
    open_pdu_tab(browser, list_url, "offline-edits")
    browser.click(BUTTON_IMPORT)
    browser.wait_for_element_visible(DIALOG_IMPORT)
    browser.assert_text("IMPORT", BUTTON_IMPORT_SUBMIT)
    browser.choose_file(FILE_INPUT, str(path))
    browser.click(BUTTON_IMPORT_SUBMIT)


def assert_texts(browser: HopeTestBrowser, expected: dict[str, str]) -> None:
    """Assert each selector in `expected` contains its text."""
    for selector, text in expected.items():
        browser.assert_text(text, selector)
