from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class RDIDetailsPage(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    label_status = 'div[data-cy="label-status"]'
    status_container = 'div[data-cy="status-container"]'
    label_source_of_data = 'div[data-cy="label-Source of Data"]'
    label_import_date = 'div[data-cy="label-Import Date"]'
    label_imported_by = 'div[data-cy="label-Imported by"]'
    labelized_field_container_households = 'div[data-cy="labelized-field-container-households"]'
    label_total_number_of_households = 'div[data-cy="label-Total Number of Items Groups"]'
    labelized_field_container_individuals = 'div[data-cy="labelized-field-container-individuals"]'
    label_total_number_of_individuals = 'div[data-cy="label-Total Number of Items"]'
    table_label = 'span[data-cy="table-label"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    imported_individuals_table = 'div[data-cy="imported-individuals-table"]'
    table_row = 'tr[data-cy="table-row"]'
    button_refuse_rdi = 'button[data-cy="button-refuse-rdi"]'
    button_merge_rdi = 'button[data-cy="button-merge-rdi"]'
    button_merge = 'button[data-cy="button-merge"]'
    button_view_tickets = 'a[data-cy="button-view-tickets"]'
    button_households = 'button[data-cy="tab-Households"]'
    button_individuals = 'button[data-cy="tab-Individuals"]'
    imported_households_row = './/tr[@data-cy="imported-households-row"]'

    # Texts
    button_refuse_rdi_text = "REFUSE IMPORT"
    button_merge_rdi_text = "MERGE"

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_label_status(self) -> WebElement:
        return self.wait_for(self.label_status)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_label_source_of_data(self) -> WebElement:
        return self.wait_for(self.label_source_of_data)

    def get_label_import_date(self) -> WebElement:
        return self.wait_for(self.label_import_date)

    def get_label_imported_by(self) -> WebElement:
        return self.wait_for(self.label_imported_by)

    def get_labelized_field_container_households(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_households)

    def get_label_total_number_of_households(self) -> WebElement:
        return self.wait_for(self.label_total_number_of_households)

    def get_labelized_field_container_individuals(self) -> WebElement:
        return self.wait_for(self.labelized_field_container_individuals)

    def get_label_total_number_of_individuals(self) -> WebElement:
        return self.wait_for(self.label_total_number_of_individuals)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_table_row(self) -> WebElement:
        return self.wait_for(self.table_row)

    def get_button_refuse_rdi(self) -> WebElement:
        return self.wait_for(self.button_refuse_rdi)

    def get_table_pagination(self) -> WebElement:
        return self.get(self.table_pagination)

    def get_button_merge_rdi(self) -> WebElement:
        return self.wait_for(self.button_merge_rdi)

    def get_button_merge(self) -> WebElement:
        return self.wait_for(self.button_merge)

    def get_button_view_tickets(self) -> WebElement:
        return self.wait_for(self.button_view_tickets)

    def get_button_households(self) -> WebElement:
        return self.wait_for(self.button_households)

    def get_button_individuals(self) -> WebElement:
        return self.wait_for(self.button_individuals)

    def get_imported_individuals_table(self) -> WebElement:
        return self.wait_for(self.imported_individuals_table)

    def get_imported_households_row(self, number: int) -> WebElement:
        self.wait_for(self.imported_households_row, By.XPATH)
        return self.get_elements(self.imported_households_row, By.XPATH)[number]

    def wait_for_status(self, status: str, timeout: int = 60) -> None:
        for _ in range(timeout):
            sleep(1)
            if self.get_status_container().text == status:
                break
            self.driver.refresh()

    def wait_for_number_of_rows(self, string: str, timeout: int = 60) -> bool:
        for _ in range(timeout):
            sleep(1)
            if string in self.get('//*[@data-cy="table-pagination"]/div/p[2]', By.XPATH).text:
                return True
        return False
