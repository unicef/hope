from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Filters(BaseComponents):
    filters_search = 'div[data-cy="filters-search"]'
    search_text_field = 'div[data-cy="search-text-field"]'
    ind_filters_search = 'div[data-cy="ind-filters-search"]'
    ind_filters_gender = 'div[data-cy="ind-filters-gender"]'
    ind_filters_age_from = 'div[data-cy="ind-filters-age-from"]'
    ind_filters_age_to = 'div[data-cy="ind-filters-age-to"]'
    ind_filters_flags = 'div[data-cy="ind-filters-flags"]'
    ind_filters_order_by = 'div[data-cy="ind-filters-order-by"]'
    ind_filters_status = 'div[data-cy="ind-filters-status"]'
    ind_filters_reg_date_from = 'div[data-cy="ind-filters-reg-date-from"]'
    ind_filters_reg_date_to = 'div[data-cy="ind-filters-reg-date-to"]'
    date_picker_filter_from = 'div[data-cy="date-picker-filter-From"]'
    date_picker_filter_to = 'div[data-cy="date-picker-filter-To"]'
    filter_fsp = 'div[data-cy="filter-fsp"]'
    filter_modality = 'div[data-cy="filter-Modality"]'
    filters_status = 'div[data-cy="filters-status"]'
    filters_sector = 'div[data-cy="filters-sector"]'
    data_picker_filter = 'div[data-cy="date-picker-filter"]'
    filters_number_of_households_min = 'div[data-cy="filters-number-of-households-min"]'
    filters_number_of_households_max = 'div[data-cy="filters-number-of-households-max"]'
    filters_budget_min = 'div[data-cy="filters-budget-min"]'
    filters_budget_max = 'div[data-cy="filters-budget-max"]'
    filters_data_collecting_type = 'div[data-cy="filters-data-collecting-type"]'
    filters_program = 'div[data-cy="filters-program"]'
    filters_document_type = 'div[data-cy="filters-document-type"]'
    filters_document_number = 'div[data-cy="filters-document-number"]'
    filters_fsp = 'div[data-cy="filters-fsp"]'
    filters_category = 'div[data-cy="filters-category"]'
    filters_admin_level = 'div[data-cy="filters-admin-level-2"]'
    filters_assignee = 'div[data-cy="filters-assignee"]'
    filters_created_by_autocomplete = 'div[data-cy="filters-created-by-autocomplete"]'
    filters_registration_data_import = 'div[data-cy="filters-registration-data-import"]'
    filters_preferred_language = 'div[data-cy="filters-preferred-language"]'
    filters_priority = 'div[data-cy="filters-priority"]'
    filters_urgency = 'div[data-cy="filters-urgency"]'
    filters_active_tickets = 'div[data-cy="filters-active-tickets"]'
    filters_program_state = 'div[data-cy="filters-program-state"]'
    filters_residence_status = 'div[data-cy="filters-residence-status"]'
    hh_filters_search = 'div[data-cy="hh-filters-search"]'
    hh_filters_residence_status = 'div[data-cy="hh-filters-residence-status"]'
    hh_filters_admin2 = 'div[data-cy="hh-filters-admin2"]'
    hh_filters_household_size_from = 'div[data-cy="hh-filters-household-size-from"]'
    hh_filters_household_size_to = 'div[data-cy="hh-filters-household-size-to"]'
    hh_filters_order_by = 'div[data-cy="hh-filters-order-by"]'
    hh_filters_status = 'div[data-cy="hh-filters-status"]'
    menu_item_filters_text = 'div[data-cy="menu-item-filters-text"]'
    filters_total_households_count_min = 'div[data-cy="filters-total-households-count-min"]'
    filters_total_households_count_max = 'div[data-cy="filters-total-households-count-max"]'
    global_program_filter_container = 'div[data-cy="global-program-filter-container"]'
    filter_search = 'div[data-cy="filter-search"]'
    filter_status = 'div[data-cy="filter-status"]'
    filter_size_min = 'div[data-cy="filter-size-min"]'
    filter_size_max = 'div[data-cy="filter-size-max"]'
    global_program_filter = 'button[data-cy="global-program-filter"]'
    report_type_filter = 'div[data-cy="report-type-filter"]'
    report_created_from_filter = 'div[data-cy="report-created-from-filter"]'
    report_created_to_filter = 'div[data-cy="report-created-to-filter"]'
    report_status_filter = 'div[data-cy="report-status-filter"]'
    report_only_my_filter = 'span[data-cy="report-only-my-filter"]'
    programme_input = 'div[data-cy="Programme-input"]'
    filters_creation_date_from = 'div[data-cy="filters-creation-date-from"]'
    filters_creation_date_to = 'div[data-cy="filters-creation-date-to"]'
    user_input = 'div[data-cy="User-input"]'
    select_filter = 'div[data-cy="select-filter"]'
    filters_end_date = 'div[data-cy="filters-end-date"]'
    filters_start_date = 'div[data-cy="filters-start-date"]'
    filter_end_date = 'div[data-cy="filter-end-date"]'
    filter_start_date = 'div[data-cy="filter-start-date"]'
    assigned_to_input = 'div[data-cy="Assigned To-input"]'
    filters_issue_type = 'div[data-cy="filters-issue-type"]'
    filter_import_date_range_min = 'div[data-cy="filter-import-date-range-min"]'
    filter_import_date_range_max = 'div[data-cy="filter-import-date-range-max"]'
    filters_target_population_autocomplete = 'div[data-cy="filters-target-population-autocomplete"]'
    target_population_input = 'div[data-cy="Target Population-input"]'
    created_by_input = 'div[data-cy="Created by-input"]'
    filters_total_entitled_quantity_from = 'div[data-cy="date-picker-filter-From"]'
    filters_total_entitled_quantity_to = 'div[data-cy="date-picker-filter-To"]'

    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    imported_by_input = 'div[data-cy="Imported By-input"]'

    def get_filters_search(self) -> WebElement:
        return self.wait_for(self.filters_search).find_element(By.XPATH, "./div/input")

    def get_filters_document_type(self) -> WebElement:
        return self.wait_for(self.filters_document_type)

    def get_filters_document_number(self) -> WebElement:
        return self.wait_for(self.filters_document_number)

    def get_filters_program(self) -> WebElement:
        return self.wait_for(self.filters_program)

    def get_filters_status(self) -> WebElement:
        return self.wait_for(self.filters_status)

    def select_filters_satus(self, status: str) -> None:
        self.get_filters_status().click()
        self.wait_for(f'li[data-value="{status.upper()}"]').click()
        for _ in range(10):
            sleep(1)
            if status.capitalize() in self.get_filters_status().text:
                self.get_button_filters_apply().click()
                break
        else:
            raise Exception(f"Status: {status.capitalize()} does not occur.")

    def get_filters_fsp(self) -> WebElement:
        return self.wait_for(self.filters_fsp)

    def get_filters_category(self) -> WebElement:
        return self.wait_for(self.filters_category)

    def get_filters_admin_level(self) -> WebElement:
        return self.wait_for(self.filters_admin_level)

    def get_filters_assignee(self) -> WebElement:
        return self.wait_for(self.filters_assignee)

    def get_filters_created_by_autocomplete(self) -> WebElement:
        return self.wait_for(self.filters_created_by_autocomplete)

    def get_filters_registration_data_import(self) -> WebElement:
        return self.wait_for(self.filters_registration_data_import)

    def get_filters_preferred_language(self) -> WebElement:
        return self.wait_for(self.filters_preferred_language)

    def get_filters_priority(self) -> WebElement:
        return self.wait_for(self.filters_priority)

    def get_filters_urgency(self) -> WebElement:
        return self.wait_for(self.filters_urgency)

    def get_filters_active_tickets(self) -> WebElement:
        return self.wait_for(self.filters_active_tickets)

    def get_filters_program_state(self) -> WebElement:
        return self.wait_for(self.filters_program_state)

    def get_filters_sector(self) -> WebElement:
        return self.wait_for(self.filters_sector)

    def get_filters_number_of_households_min(self) -> WebElement:
        return self.wait_for(self.filters_number_of_households_min).find_element(By.XPATH, "./div/input")

    def get_filters_number_of_households_max(self) -> WebElement:
        return self.wait_for(self.filters_number_of_households_max).find_element(By.XPATH, "./div/input")

    def get_filters_budget_min(self) -> WebElement:
        return self.wait_for(self.filters_budget_min)

    def get_filters_budget_max(self) -> WebElement:
        return self.wait_for(self.filters_budget_max)

    def get_filters_data_collecting_type(self) -> WebElement:
        return self.wait_for(self.filters_data_collecting_type)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_filters_residence_status(self) -> WebElement:
        return self.wait_for(self.filters_residence_status)

    def get_hh_filters_search(self) -> WebElement:
        return self.wait_for(self.hh_filters_search)

    def get_hh_filters_residence_status(self) -> WebElement:
        return self.wait_for(self.hh_filters_residence_status)

    def get_hh_filters_admin2(self) -> WebElement:
        return self.wait_for(self.hh_filters_admin2)

    def get_hh_filters_household_size_from(self) -> WebElement:
        return self.wait_for(self.hh_filters_household_size_from)

    def get_hh_filters_household_size_to(self) -> WebElement:
        return self.wait_for(self.hh_filters_household_size_to)

    def get_hh_filters_order_by(self) -> WebElement:
        return self.wait_for(self.hh_filters_order_by)

    def get_hh_filters_status(self) -> WebElement:
        return self.wait_for(self.hh_filters_status)

    def get_menu_item_filters_text(self) -> WebElement:
        return self.wait_for(self.menu_item_filters_text)

    def get_filters_total_households_count_min(self) -> WebElement:
        return self.wait_for(self.filters_total_households_count_min).find_element(By.XPATH, "./div/input")

    def get_filters_total_households_count_max(self) -> WebElement:
        return self.wait_for(self.filters_total_households_count_max).find_element(By.XPATH, "./div/input")

    def get_global_program_filter_container(self) -> WebElement:
        return self.wait_for(self.global_program_filter_container)

    def get_filter_search(self) -> WebElement:
        return self.wait_for(self.filter_search)

    def get_filter_status(self) -> WebElement:
        return self.wait_for(self.filter_status)

    def get_filter_size_min(self) -> WebElement:
        return self.wait_for(self.filter_size_min)

    def get_filter_size_max(self) -> WebElement:
        return self.wait_for(self.filter_size_max)

    def get_global_program_filter(self) -> WebElement:
        return self.wait_for(self.global_program_filter)

    def get_report_type_filter(self) -> WebElement:
        return self.wait_for(self.report_type_filter)

    def get_report_created_from_filter(self) -> WebElement:
        return self.wait_for(self.report_created_from_filter)

    def get_report_created_to_filter(self) -> WebElement:
        return self.wait_for(self.report_created_to_filter)

    def get_report_status_filter(self) -> WebElement:
        return self.wait_for(self.report_status_filter)

    def get_report_only_my_filter(self) -> WebElement:
        return self.wait_for(self.report_only_my_filter)

    def get_filter_by_locator(self, value: str, locator_type: str = "data-cy") -> WebElement:
        return self.driver.find_elements(By.CSS_SELECTOR, f"[{locator_type}='{value}']")[0].find_elements(
            By.TAG_NAME, "input"
        )[0]
