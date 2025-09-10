from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class Households(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    hh_filters_search = 'div[data-cy="hh-filters-search"]'
    filter_document_type = 'div[data-cy="filters-document-type"]'
    hh_filters_residence_status = 'div[data-cy="hh-filters-residence-status"]'
    hh_filters_admin2 = 'div[data-cy="hh-filters-admin2"]'
    admin_level_2_input = 'div[data-cy="Admin Level 2-input"]'
    hh_filters_household_size_from = 'div[data-cy="hh-filters-household-size-from"]'
    hh_filters_household_size_to = 'div[data-cy="hh-filters-household-size-to"]'
    hh_filters_order_by = 'div[data-cy="hh-filters-order-by"]'
    hh_filters_status = 'div[data-cy="hh-filters-status"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    page_details_container = 'div[data-cy="page-details-container"]'
    table_title = 'h6[data-cy="table-title"]'
    sanction_list_possible_match = 'th[data-cy="sanction-list-possible-match"]'
    table_label = 'span[data-cy="table-label"]'
    household_id = 'th[data-cy="household-id"]'
    status = 'th[data-cy="status"]'
    household_head_name = 'th[data-cy="household-head-name"]'
    household_size = 'th[data-cy="household-size"]'
    household_location = 'th[data-cy="household-location"]'
    household_residence_status = 'th[data-cy="household-residence-status"]'
    household_total_cash_received = 'th[data-cy="household-total-cash-received"]'
    household_registration_date = 'th[data-cy="household-registration-date"]'
    table_row = 'tr[data-cy="table-row"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    household_table_row = 'tr[data-cy="household-table-row"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_hh_filters_search(self) -> WebElement:
        return self.wait_for(self.hh_filters_search)

    def get_filter_document_type(self) -> WebElement:
        return self.wait_for(self.filter_document_type)

    def get_hh_filters_residence_status(self) -> WebElement:
        return self.wait_for(self.hh_filters_residence_status)

    def get_hh_filters_admin2(self) -> WebElement:
        return self.wait_for(self.hh_filters_admin2)

    def get_admin_level_2_input(self) -> WebElement:
        return self.wait_for(self.admin_level_2_input)

    def get_hh_filters_household_size_from(self) -> WebElement:
        return self.wait_for(self.hh_filters_household_size_from)

    def get_hh_filters_household_size_to(self) -> WebElement:
        return self.wait_for(self.hh_filters_household_size_to)

    def get_hh_filters_order_by(self) -> WebElement:
        return self.wait_for(self.hh_filters_order_by)

    def get_hh_filters_status(self) -> WebElement:
        return self.wait_for(self.hh_filters_status)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_page_details_container(self) -> WebElement:
        return self.wait_for(self.page_details_container)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_sanction_list_possible_match(self) -> WebElement:
        return self.wait_for(self.sanction_list_possible_match)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_household_id(self) -> WebElement:
        return self.wait_for(self.household_id)

    def get_status(self) -> WebElement:
        return self.wait_for(self.status)

    def get_household_head_name(self) -> WebElement:
        return self.wait_for(self.household_head_name)

    def get_household_size(self) -> WebElement:
        return self.wait_for(self.household_size)

    def get_household_location(self) -> WebElement:
        return self.wait_for(self.household_location)

    def get_household_residence_status(self) -> WebElement:
        return self.wait_for(self.household_residence_status)

    def get_household_total_cash_received(self) -> WebElement:
        return self.wait_for(self.household_total_cash_received)

    def get_household_registration_date(self) -> WebElement:
        return self.wait_for(self.household_registration_date)

    def get_table_row(self) -> WebElement:
        return self.wait_for(self.table_row)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_household_table_rows(self) -> WebElement:
        return self.wait_for(self.household_table_row)

    def get_households_rows(self) -> list[WebElement]:
        self.get_household_table_rows()
        return self.get_elements(self.household_table_row)

    def get_households_row_by_number(self, number: int) -> WebElement:
        return self.get_households_rows()[number]
