from pathlib import Path

import pytest

from e2e.new_selenium.programme_population.conftest import open_pdu_tab, rounds_data
from extras.test_utils.factories import PDUXlsxTemplateFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import FlexibleAttribute, Individual, PDUXlsxTemplate, Program

pytestmark = pytest.mark.django_db()

NEW_TEMPLATE = 'a[data-cy="new-template-button"]'
DETAIL_MODAL = 'div[data-cy="periodic-data-update-detail"]'
RDI_FILTER = 'div[data-cy="filters-registration-data-import"]'
SUBMIT = 'button[data-cy="submit-button"]'


def template_cell(column: str, template: PDUXlsxTemplate) -> str:
    return f'td[data-cy="template-{column}-{template.pk}"]'


def export_button(template: PDUXlsxTemplate) -> str:
    return f'button[data-cy="export-btn-{template.pk}"]'


def download_button(template: PDUXlsxTemplate) -> str:
    return f'a[data-cy="download-btn-{template.pk}"]'


def download_template(browser: HopeTestBrowser, template: PDUXlsxTemplate) -> None:
    browser.wait_for_text("Exported", template_cell("status", template))
    template.refresh_from_db()
    filename = Path(template.file.file.name).name
    browser.delete_downloaded_file_if_present(filename, browser=True)
    browser.click(download_button(template))
    browser.assert_downloaded_file(filename, browser=True)


@pytest.fixture
def template_to_export(
    program: Program, string_attribute: FlexibleAttribute, individual: Individual
) -> PDUXlsxTemplate:
    return PDUXlsxTemplate.objects.create(
        program=program,
        business_area=program.business_area,
        status=PDUXlsxTemplate.Status.TO_EXPORT,
        filters={},
        rounds_data=rounds_data(string_attribute),
    )


@pytest.fixture
def exported_template(program: Program, string_attribute: FlexibleAttribute) -> PDUXlsxTemplate:
    return PDUXlsxTemplateFactory(
        program=program,
        business_area=program.business_area,
        status=PDUXlsxTemplate.Status.EXPORTED,
        number_of_records=10,
        filters={},
        rounds_data=rounds_data(string_attribute),
    )


def test_export_and_download_template(
    template_to_export: PDUXlsxTemplate, program: Program, login: HopeTestBrowser
) -> None:
    open_pdu_tab(login, program, "offline-templates")
    login.assert_text("To export", template_cell("status", template_to_export))

    login.click(export_button(template_to_export))

    download_template(login, template_to_export)


def test_template_list_shows_template(
    exported_template: PDUXlsxTemplate, program: Program, login: HopeTestBrowser
) -> None:
    open_pdu_tab(login, program, "offline-templates")

    login.assert_exact_text(str(exported_template.pk), template_cell("id", exported_template))
    login.assert_exact_text("10", template_cell("records", exported_template))
    login.assert_text(f"{exported_template.created_at:%-d %b %Y}", template_cell("created-at", exported_template))
    login.assert_text(exported_template.created_by.get_full_name(), template_cell("created-by", exported_template))
    login.assert_text("Exported", template_cell("status", exported_template))
    login.assert_element_visible(download_button(exported_template))


def test_template_details_shows_rounds(
    template_to_export: PDUXlsxTemplate,
    string_attribute: FlexibleAttribute,
    program: Program,
    login: HopeTestBrowser,
) -> None:
    open_pdu_tab(login, program, "offline-templates")

    login.click(f"{template_cell('details-btn', template_to_export)} button")

    login.wait_for_element_visible(DETAIL_MODAL)
    login.assert_text("Test String Attribute", 'td[data-cy="template-field-0"]')
    login.assert_exact_text("1", 'td[data-cy="template-round-number-0"]')
    login.assert_text("Round 1", 'td[data-cy="template-round-name-0"]')
    login.assert_exact_text("0", 'td[data-cy="template-number-of-individuals-0"]')


def test_create_and_download_template(
    individual: Individual,
    string_attribute: FlexibleAttribute,
    program: Program,
    login: HopeTestBrowser,
) -> None:
    open_pdu_tab(login, program, "offline-templates")

    login.click(NEW_TEMPLATE)
    login.click(RDI_FILTER)
    login.select_listbox_element(individual.registration_data_import.name)
    login.click(SUBMIT)
    login.check_checkbox(f'span[data-cy="checkbox-{string_attribute.name}"]')
    login.click(SUBMIT)
    # The template name step is optional.
    login.click(SUBMIT)

    login.wait_for_element_visible(NEW_TEMPLATE)
    template = PDUXlsxTemplate.objects.get(program=program)
    login.assert_exact_text(str(template.pk), template_cell("id", template))
    download_template(login, template)
