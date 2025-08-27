from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PeriodicDataUpdateXlsxUploads(BaseComponents):
    nav_program_population = 'a[data-cy="nav-Programme Population"]'
    nav_program_details = 'a[data-cy="nav-Programme Details"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    tab_individuals = 'button[data-cy="tab-individuals"]'
    tab_periodic_data_updates = 'button[data-cy="tab-periodic-data-updates"]'
    title = 'h6[data-cy="title"]'
    new_template_button = 'a[data-cy="new-template-button"]'
    button_import = 'button[data-cy="button-import"]'
    pdu_templates = 'button[data-cy="pdu-templates"]'
    pdu_updates = 'button[data-cy="pdu-updates"]'
    head_cell_import_id = 'th[data-cy="head-cell-import-id"]'
    table_label = 'span[data-cy="table-label"]'
    head_cell_template_id = 'th[data-cy="head-cell-template-id"]'
    head_cell_import_date = 'th[data-cy="head-cell-import-date"]'
    head_cell_imported_by = 'th[data-cy="head-cell-imported-by"]'
    head_cell_details = 'th[data-cy="head-cell-details"]'
    head_cell_status = 'th[data-cy="head-cell-status"]'
    update_row = 'tr[data-cy="update-row-{}"]'
    update_id = 'td[data-cy="update-id-{}"]'
    update_template = 'td[data-cy="update-template-{}"]'
    update_created_at = 'td[data-cy="update-created-at-{}"]'
    update_created_by = 'td[data-cy="update-created-by-{}"]'
    update_details = 'td[data-cy="update-details-{}"]'
    update_status = 'td[data-cy="update-status-{}"]'
    status_container = 'div[data-cy="status-container"]'
    table_pagination = 'div[data-cy="table-pagination"]'

    def get_nav_program_population(self) -> WebElement:
        return self.wait_for(self.nav_program_population)

    def get_nav_program_details(self) -> WebElement:
        return self.wait_for(self.nav_program_details)

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_tab_individuals(self) -> WebElement:
        return self.wait_for(self.tab_individuals)

    def get_tab_periodic_data_updates(self) -> WebElement:
        return self.wait_for(self.tab_periodic_data_updates)

    def get_title(self) -> WebElement:
        return self.wait_for(self.title)

    def get_new_template_button(self) -> WebElement:
        return self.wait_for(self.new_template_button)

    def get_button_import(self) -> WebElement:
        return self.wait_for(self.button_import)

    def get_pdu_templates(self) -> WebElement:
        return self.wait_for(self.pdu_templates)

    def get_pdu_updates(self) -> WebElement:
        return self.wait_for(self.pdu_updates)

    def get_head_cell_import_id(self) -> WebElement:
        return self.wait_for(self.head_cell_import_id)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_head_cell_template_id(self) -> WebElement:
        return self.wait_for(self.head_cell_template_id)

    def get_head_cell_import_date(self) -> WebElement:
        return self.wait_for(self.head_cell_import_date)

    def get_head_cell_imported_by(self) -> WebElement:
        return self.wait_for(self.head_cell_imported_by)

    def get_head_cell_details(self) -> WebElement:
        return self.wait_for(self.head_cell_details)

    def get_head_cell_status(self) -> WebElement:
        return self.wait_for(self.head_cell_status)

    def get_update_row(self, index: int) -> WebElement:
        locator = self.update_row.format(index)
        return self.wait_for(locator)

    def get_update_id(self, index: int) -> WebElement:
        locator = self.update_id.format(index)
        return self.wait_for(locator, timeout=120)

    def get_update_template(self, index: int) -> WebElement:
        locator = self.update_template.format(index)
        return self.wait_for(locator)

    def get_update_created_at(self, index: int) -> WebElement:
        locator = self.update_created_at.format(index)
        return self.wait_for(locator)

    def get_update_created_by(self, index: int) -> WebElement:
        locator = self.update_created_by.format(index)
        return self.wait_for(locator)

    def get_update_details(self, index: int) -> WebElement:
        locator = self.update_details.format(index)
        return self.wait_for(locator)

    def get_update_status(self, index: int) -> WebElement:
        locator = self.update_status.format(index)
        return self.wait_for(locator)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)
