from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class AccountabilityCommunication(BaseComponents):
    # Locators
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_communication_create_new = 'a[data-cy="button-communication-create-new"]'
    filters_target_population_autocomplete = 'div[data-cy="filters-target-population-autocomplete"]'
    target_population_input = 'div[data-cy="Target Population-input"]'
    filters_created_by_autocomplete = 'div[data-cy="filters-created-by-autocomplete"]'
    created_by_input = 'div[data-cy="Created by-input"]'
    filters_creation_date_from = 'div[data-cy="filters-creation-date-from"]'
    filters_creation_date_to = 'div[data-cy="filters-creation-date-to"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    table_title = 'h6[data-cy="table-title"]'
    table_label = 'span[data-cy="table-label"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    rows = 'tr[role="checkbox"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_communication_create_new(self) -> WebElement:
        return self.wait_for(self.button_communication_create_new)

    def get_filters_target_population_autocomplete(self) -> WebElement:
        return self.wait_for(self.filters_target_population_autocomplete)

    def get_target_population_input(self) -> WebElement:
        return self.wait_for(self.target_population_input)

    def get_filters_created_by_autocomplete(self) -> WebElement:
        return self.wait_for(self.filters_created_by_autocomplete)

    def get_created_by_input(self) -> WebElement:
        return self.wait_for(self.created_by_input)

    def get_filters_creation_date_from(self) -> WebElement:
        return self.wait_for(self.filters_creation_date_from)

    def get_filters_creation_date_to(self) -> WebElement:
        return self.wait_for(self.filters_creation_date_to)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_table_label(self) -> [WebElement]:
        return self.get_elements(self.table_label)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_rows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)
