from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class ProgrammeUsers(BaseComponents):
    page_header_title = 'h5[data-cy="page-header-title"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    button_target_population_create_new = 'a[data-cy="button-target-population-create-new"]'
    select_filter = 'div[data-cy="select-filter"]'
    partner_filter = 'div[data-cy="partner-filter"]'
    role_filter = 'div[data-cy="role-filter"]'
    status_filter = 'div[data-cy="status-filter"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    table_title = 'h6[data-cy="table-title"]'
    table_label = 'span[data-cy="table-label"]'
    status_container = 'div[data-cy="status-container"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    arrow_down = 'button[data-cy="arrow-down"]'
    country_role = 'div[data-cy="country-role"]'
    mapped_country_role = 'div[data-cy="mapped-country-role"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_target_population_create_new(self) -> WebElement:
        return self.wait_for(self.button_target_population_create_new)

    def get_select_filter(self) -> WebElement:
        return self.wait_for(self.select_filter)

    def get_partner_filter(self) -> WebElement:
        return self.wait_for(self.partner_filter)

    def get_role_filter(self) -> WebElement:
        return self.wait_for(self.role_filter)

    def get_status_filter(self) -> WebElement:
        return self.wait_for(self.status_filter)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_table_label(self) -> [WebElement]:
        self.wait_for(self.table_label)
        return self.get_elements(self.table_label)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_arrow_down(self) -> WebElement:
        return self.wait_for(self.arrow_down)

    def get_country_role(self) -> WebElement:
        return self.wait_for(self.country_role)

    def get_mapped_country_role(self) -> WebElement:
        return self.wait_for(self.mapped_country_role)
