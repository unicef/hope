from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class People(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    ind_filters_search = 'div[data-cy="ind-filters-search"]'
    select_filter = 'div[data-cy="select-filter"]'
    filters_document_type = 'div[data-cy="filters-document-type"]'
    filters_document_number = 'div[data-cy="filters-document-number"]'
    ind_filters_admin1 = 'div[data-cy="ind-filters-admin1"]'
    admin_level_1_input = 'div[data-cy="Admin Level 1-input"]'
    ind_filters_admin2 = 'div[data-cy="ind-filters-admin2"]'
    admin_level_2_input = 'div[data-cy="Admin Level 2-input"]'
    ind_filters_gender = 'div[data-cy="ind-filters-gender"]'
    ind_filters_age_from = 'div[data-cy="ind-filters-age-from"]'
    ind_filters_age_to = 'div[data-cy="ind-filters-age-to"]'
    ind_filters_flags = 'div[data-cy="ind-filters-flags"]'
    ind_filters_order_by = 'div[data-cy="ind-filters-order-by"]'
    ind_filters_status = 'div[data-cy="ind-filters-status"]'
    ind_filters_reg_date_from = 'div[data-cy="ind-filters-reg-date-from"]'
    ind_filters_reg_date_to = 'div[data-cy="ind-filters-reg-date-to"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    page_details_container = 'div[data-cy="page-details-container"]'
    table_title = 'h6[data-cy="table-title"]'
    sanction_list_possible_match = 'th[data-cy="sanction-list-possible-match"]'
    table_label = 'span[data-cy="table-label"]'
    individual_id = 'th[data-cy="individual-id"]'
    individual_name = 'th[data-cy="individual-name"]'
    individual_age = 'th[data-cy="individual-age"]'
    individual_sex = 'th[data-cy="individual-sex"]'
    individual_location = 'th[data-cy="individual-location"]'
    table_row = 'tr[data-cy="table-row"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    individual_table_row = 'tr[data-cy="individual-table-row"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_ind_filters_search(self) -> WebElement:
        return self.wait_for(self.ind_filters_search)

    def get_select_filter(self) -> WebElement:
        return self.wait_for(self.select_filter)

    def get_filters_document_type(self) -> WebElement:
        return self.wait_for(self.filters_document_type)

    def get_filters_document_number(self) -> WebElement:
        return self.wait_for(self.filters_document_number)

    def get_ind_filters_admin1(self) -> WebElement:
        return self.wait_for(self.ind_filters_admin1)

    def get_admin_level_1_input(self) -> WebElement:
        return self.wait_for(self.admin_level_1_input)

    def get_ind_filters_admin2(self) -> WebElement:
        return self.wait_for(self.ind_filters_admin2)

    def get_admin_level_2_input(self) -> WebElement:
        return self.wait_for(self.admin_level_2_input)

    def get_ind_filters_gender(self) -> WebElement:
        return self.wait_for(self.ind_filters_gender)

    def get_ind_filters_age_from(self) -> WebElement:
        return self.wait_for(self.ind_filters_age_from)

    def get_ind_filters_age_to(self) -> WebElement:
        return self.wait_for(self.ind_filters_age_to)

    def get_ind_filters_flags(self) -> WebElement:
        return self.wait_for(self.ind_filters_flags)

    def get_ind_filters_order_by(self) -> WebElement:
        return self.wait_for(self.ind_filters_order_by)

    def get_ind_filters_status(self) -> WebElement:
        return self.wait_for(self.ind_filters_status)

    def get_ind_filters_reg_date_from(self) -> WebElement:
        return self.wait_for(self.ind_filters_reg_date_from)

    def get_ind_filters_reg_date_to(self) -> WebElement:
        return self.wait_for(self.ind_filters_reg_date_to)

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

    def get_individual_id(self) -> WebElement:
        return self.wait_for(self.individual_id)

    def get_individual_name(self) -> WebElement:
        return self.wait_for(self.individual_name)

    def get_individual_age(self) -> WebElement:
        return self.wait_for(self.individual_age)

    def get_individual_sex(self) -> WebElement:
        return self.wait_for(self.individual_sex)

    def get_individual_location(self) -> WebElement:
        return self.wait_for(self.individual_location)

    def get_table_row(self) -> WebElement:
        return self.wait_for(self.table_row)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_individual_table_row(self, number: int) -> WebElement:
        self.wait_for(self.individual_table_row)
        return self.get_elements(self.individual_table_row)[number]
