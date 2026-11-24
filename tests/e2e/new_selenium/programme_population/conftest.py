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
    PeriodicFieldData,
    Program,
    RegistrationDataImport,
)


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


def create_template_with_xlsx(program: Program, attribute: FlexibleAttribute) -> PDUXlsxTemplate:
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


def prepare_xlsx_file(attribute: FlexibleAttribute, value: str, collection_date: str, path: Path) -> Path:
    """Export a template for `attribute` and fill its first PDU row with `value` and `collection_date`."""
    template = create_template_with_xlsx(attribute.program, attribute)
    workbook = openpyxl.load_workbook(template.file.file)
    sheet = workbook[PDUXlsxExportTemplateService.PDU_SHEET]
    sheet["G2"] = value
    sheet["H2"] = collection_date
    workbook.save(path)
    return path


def individuals_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/population/individuals"


def open_from_menu(browser: HopeTestBrowser, program: Program, *path: str) -> None:
    """Open the programme and follow the side menu: the last item of `path` is a link, the others are sections."""
    *sections, link = path
    browser.open(f"/{program.business_area.slug}/programs/{program.code}/details/{program.code}")
    browser.assert_text(program.name, 'h5[data-cy="page-header-title"]')
    for section in sections:
        browser.open_nav_section(section)
    browser.click(f'a[data-cy="nav-{link}"]')


def open_pdu_tab(browser: HopeTestBrowser, program: Program, subtab: str) -> None:
    """Open the individuals' periodic data updates tab on `subtab` (offline-templates, offline-edits, ...)."""
    open_from_menu(browser, program, "Main Menu", "Items")
    browser.click('button[data-cy="tab-periodic-data-updates"]')
    browser.click(f'button[data-cy="pdu-{subtab}"]')
    browser.wait_for_element_visible(f'button[data-cy="pdu-{subtab}"][aria-selected="true"]')


def assert_exact_texts(browser: HopeTestBrowser, expected: dict[str, str]) -> None:
    """Assert each selector in `expected` shows exactly its text."""
    for selector, text in expected.items():
        browser.assert_exact_text(text, selector)
