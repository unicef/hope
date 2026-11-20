from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class PDUXlsxTemplates(BaseComponents):
    nav_program_population = 'a[data-cy="nav-Programme Population"]'
    nav_program_details = 'a[data-cy="nav-Programme Details"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    tab_individuals = 'button[data-cy="tab-individuals"]'
    tab_periodic_data_updates = 'button[data-cy="tab-periodic-data-updates"]'
    tab_offline_templates = 'button[data-cy="pdu-offline-templates"]'
    tab_offline_edits = 'button[data-cy="pdu-offline-edits"]'
    title = 'h6[data-cy="title"]'
    new_template_button = 'a[data-cy="new-template-button"]'
    button_import = 'button[data-cy="button-import"]'
    head_cell_template_id = 'th[data-cy="head-cell-template-id"]'
    table_label = 'span[data-cy="table-label"]'
    head_cell_number_of_records = 'th[data-cy="head-cell-number-of-records"]'
    head_cell_created_at = 'th[data-cy="head-cell-created-at"]'
    head_cell_created_by = 'th[data-cy="head-cell-created-by"]'
    head_cell_details = 'th[data-cy="head-cell-details"]'
    head_cell_status = 'th[data-cy="head-cell-status"]'
    head_cell_empty = 'th[data-cy="head-cell-empty"]'
    template_row = 'tr[data-cy="template-row-{}"]'
    template_id = 'td[data-cy="template-id-{}"]'
    template_records = 'td[data-cy="template-records-{}"]'
    template_created_at = 'td[data-cy="template-created-at-{}"]'
    template_created_by = 'td[data-cy="template-created-by-{}"]'
    template_details_btn = 'td[data-cy="template-details-btn-{}"]'
    template_status = 'td[data-cy="template-status-{}"]'
    status_container = 'div[data-cy="status-container"]'
    template_action = 'td[data-cy="template-action-{}"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    # details
    detail_modal = 'div[data-cy="periodic-data-update-detail"]'
    template_field = 'td[data-cy="template-field-{}"]'
    template_round_number = 'td[data-cy="template-round-number-{}"]'
    template_round_name = 'td[data-cy="template-round-name-{}"]'
    template_number_of_individuals = 'td[data-cy="template-number-of-individuals-{}"]'

    def get_nav_program_population(self) -> WebElement:
        return self.wait_for(self.nav_program_population)

    def get_nav_program_details(self) -> WebElement:
        return self.wait_for(self.nav_program_details)

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_tab_individuals(self) -> WebElement:
        return self.wait_for(self.tab_individuals)

    def get_tab_periodic_data_updates(self) -> WebElement:
        return self.wait_for(self.tab_periodic_data_updates)

    def get_tab_offline_templates(self) -> WebElement:
        return self.wait_for(self.tab_offline_templates)

    def get_tab_offline_edits(self) -> WebElement:
        return self.wait_for(self.tab_offline_edits)

    def get_title(self) -> WebElement:
        return self.wait_for(self.title)

    def get_new_template_button(self) -> WebElement:
        return self.wait_for(self.new_template_button)

    def get_button_import(self) -> WebElement:
        return self.wait_for(self.button_import)

    def get_head_cell_template_id(self) -> WebElement:
        return self.wait_for(self.head_cell_template_id)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_head_cell_number_of_records(self) -> WebElement:
        return self.wait_for(self.head_cell_number_of_records)

    def get_head_cell_created_at(self) -> WebElement:
        return self.wait_for(self.head_cell_created_at)

    def get_head_cell_created_by(self) -> WebElement:
        return self.wait_for(self.head_cell_created_by)

    def get_head_cell_details(self) -> WebElement:
        return self.wait_for(self.head_cell_details)

    def get_head_cell_status(self) -> WebElement:
        return self.wait_for(self.head_cell_status)

    def get_head_cell_empty(self) -> WebElement:
        return self.wait_for(self.head_cell_empty)

    def get_template_row(self) -> WebElement:
        return self.wait_for(self.template_row)

    def get_template_id(self, index: int) -> WebElement:
        locator = self.template_id.format(index)
        return self.wait_for(locator)

    def get_template_records(self, index: int) -> WebElement:
        locator = self.template_records.format(index)
        return self.wait_for(locator)

    def get_template_created_at(self, index: int) -> WebElement:
        locator = self.template_created_at.format(index)
        return self.wait_for(locator)

    def get_template_created_by(self, index: int) -> WebElement:
        locator = self.template_created_by.format(index)
        return self.wait_for(locator)

    def get_template_details_btn(self, index: int) -> WebElement:
        locator = self.template_details_btn.format(index)
        return self.wait_for(locator)

    def get_template_status(self, index: int) -> WebElement:
        locator = self.template_status.format(index)
        return self.wait_for(locator)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_template_action(self) -> WebElement:
        return self.wait_for(self.template_action)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_template_field(self, index: int) -> WebElement:
        locator = self.template_field.format(index)
        return self.wait_for(locator)

    def get_template_round_number(self, index: int) -> WebElement:
        locator = self.template_round_number.format(index)
        return self.wait_for(locator)

    def get_template_round_name(self, index: int) -> WebElement:
        locator = self.template_round_name.format(index)
        return self.wait_for(locator)

    def get_template_number_of_individuals(self, index: int) -> WebElement:
        locator = self.template_number_of_individuals.format(index)
        return self.wait_for(locator)

    def get_detail_modal(self) -> WebElement:
        return self.wait_for(self.detail_modal)
