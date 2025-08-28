from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class PDUXlsxTemplates(BaseComponents):
    nav_program_population = 'a[data-cy="nav-Programme Population"]'
    nav_program_details = 'a[data-cy="nav-Programme Details"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    tab_individuals = 'button[data-cy="tab-individuals"]'
    tab_periodic_data_updates = 'button[data-cy="tab-periodic-data-updates"]'
    title = 'h6[data-cy="title"]'
    new_template_button = 'a[data-cy="new-template-button"]'
    button_import = 'button[data-cy="button-import"]'
    pdu_templates_btn = 'button[data-cy="pdu-templates"]'
    pdu_updates_btn = 'button[data-cy="pdu-updates"]'
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

    def get_pdu_templates_btn(self) -> WebElement:
        return self.wait_for(self.pdu_templates_btn)

    def get_pdu_updates_btn(self) -> WebElement:
        return self.wait_for(self.pdu_updates_btn)

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


class PDUXlsxTemplatesDetails(BaseComponents):
    nav_program_population = 'a[data-cy="nav-Programme Population"]'
    nav_program_details = 'a[data-cy="nav-Programme Details"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    arrow_back = 'div[data-cy="arrow_back"]'
    breadcrumbs_container = 'div[data-cy="breadcrumbs-container"]'
    breadcrumbs_element_container = 'span[data-cy="breadcrumbs-element-container"]'
    breadcrumbs_link = 'a[data-cy="breadcrumbs-link"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    title = 'h6[data-cy="title"]'
    label_key = 'div[data-cy="label-key"]'
    filters_registration_data_import = 'div[data-cy="filters-registration-data-import"]'
    registration_data_import_input = 'div[data-cy="Registration Data Import-input"]'
    filters_target_population_autocomplete = 'div[data-cy="filters-target-population-autocomplete"]'
    target_population_input = 'div[data-cy="Target Population-input"]'
    select_filter = 'div[data-cy="select-filter"]'
    ind_filters_gender = 'div[data-cy="ind-filters-gender"]'
    hh_filters_age_from = 'div[data-cy="hh-filters-age-from"]'
    hh_filters_age_to = 'div[data-cy="hh-filters-age-to"]'
    ind_filters_reg_date_from = 'div[data-cy="ind-filters-reg-date-from"]'
    ind_filters_reg_date_to = 'div[data-cy="ind-filters-reg-date-to"]'
    ind_filters_grievance_ticket = 'div[data-cy="ind-filters-grievance-ticket"]'
    filter_administrative_area = 'div[data-cy="filter-administrative-area"]'
    admin_level_1_input = 'div[data-cy="Admin Level 1-input"]'
    admin_level_2_input = 'div[data-cy="Admin Level 2-input"]'
    ind_filters_received_assistance = 'div[data-cy="ind-filters-received-assistance"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    cancel_button = 'a[data-cy="cancel-button"]'
    submit_button = 'button[data-cy="submit-button"]'
    table_container = 'div[data-cy="table-container"]'
    table = 'table[data-cy="table"]'
    table_header_checkbox = 'th[data-cy="table-header-checkbox"]'
    table_header_field = 'th[data-cy="table-header-field"]'
    table_header_roundnumber = 'th[data-cy="table-header-roundNumber"]'
    table_row = 'tr[data-cy="table-row-{}"]'
    checkbox = 'span[data-cy="checkbox-{}"]'
    table_cell_field = 'td[data-cy="table-cell-field-{}"]'
    table_cell_roundnumber = 'td[data-cy="table-cell-roundNumber-{}"]'
    select_roundnumber = 'div[data-cy="select-roundNumber-{}"]'
    back_button = 'button[data-cy="back-button"]'

    def get_nav_program_population(self) -> WebElement:
        return self.wait_for(self.nav_program_population)

    def get_nav_program_details(self) -> WebElement:
        return self.wait_for(self.nav_program_details)

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_arrow_back(self) -> WebElement:
        return self.wait_for(self.arrow_back)

    def get_breadcrumbs_container(self) -> WebElement:
        return self.wait_for(self.breadcrumbs_container)

    def get_breadcrumbs_element_container(self) -> WebElement:
        return self.wait_for(self.breadcrumbs_element_container)

    def get_breadcrumbs_link(self) -> WebElement:
        return self.wait_for(self.breadcrumbs_link)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_title(self) -> WebElement:
        return self.wait_for(self.title)

    def get_label_key(self) -> WebElement:
        return self.wait_for(self.label_key)

    def get_filters_registration_data_import(self) -> WebElement:
        return self.wait_for(self.filters_registration_data_import)

    def get_registration_data_import_input(self) -> WebElement:
        return self.wait_for(self.registration_data_import_input)

    def get_filters_target_population_autocomplete(self) -> WebElement:
        return self.wait_for(self.filters_target_population_autocomplete)

    def get_target_population_input(self) -> WebElement:
        return self.wait_for(self.target_population_input)

    def get_select_filter(self) -> WebElement:
        return self.wait_for(self.select_filter)

    def get_ind_filters_gender(self) -> WebElement:
        return self.wait_for(self.ind_filters_gender)

    def get_hh_filters_age_from(self) -> WebElement:
        return self.wait_for(self.hh_filters_age_from)

    def get_hh_filters_age_to(self) -> WebElement:
        return self.wait_for(self.hh_filters_age_to)

    def get_ind_filters_reg_date_from(self) -> WebElement:
        return self.wait_for(self.ind_filters_reg_date_from)

    def get_ind_filters_reg_date_to(self) -> WebElement:
        return self.wait_for(self.ind_filters_reg_date_to)

    def get_ind_filters_grievance_ticket(self) -> WebElement:
        return self.wait_for(self.ind_filters_grievance_ticket)

    def get_filter_administrative_area(self) -> WebElement:
        return self.wait_for(self.filter_administrative_area)

    def get_admin_level_1_input(self) -> WebElement:
        return self.wait_for(self.admin_level_1_input)

    def get_admin_level_2_input(self) -> WebElement:
        return self.wait_for(self.admin_level_2_input)

    def get_ind_filters_received_assistance(self) -> WebElement:
        return self.wait_for(self.ind_filters_received_assistance)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_cancel_button(self) -> WebElement:
        return self.wait_for(self.cancel_button)

    def get_submit_button(self) -> WebElement:
        return self.wait_for(self.submit_button)

    def get_table_container(self) -> WebElement:
        return self.wait_for(self.table_container)

    def get_table(self) -> WebElement:
        return self.wait_for(self.table)

    def get_table_header_checkbox(self) -> WebElement:
        return self.wait_for(self.table_header_checkbox)

    def get_table_header_field(self) -> WebElement:
        return self.wait_for(self.table_header_field)

    def get_table_header_roundnumber(self) -> WebElement:
        return self.wait_for(self.table_header_roundnumber)

    def get_table_row(self, index: str) -> WebElement:
        locator = self.table_row.format(index)
        return self.wait_for(locator)

    def get_checkbox(self, index: str) -> WebElement:
        locator = self.checkbox.format(index)
        return self.wait_for(locator)

    def get_table_cell_field(self, index: str) -> WebElement:
        locator = self.table_cell_field.format(index)
        return self.wait_for(locator)

    def get_table_cell_roundnumber(self, index: str) -> WebElement:
        locator = self.table_cell_roundnumber.format(index)
        return self.wait_for(locator)

    def get_select_roundnumber(self, index: str) -> WebElement:
        locator = self.select_roundnumber.format(index)
        return self.wait_for(locator)

    def get_back_button(self) -> WebElement:
        return self.wait_for(self.back_button)
