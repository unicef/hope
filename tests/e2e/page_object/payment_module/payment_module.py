from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentModule(BaseComponents):
    page_header_title = 'h5[data-cy="page-header-title"]'
    select_filter = 'div[data-cy="select-filter"]'
    filters_total_entitled_quantity_from = 'div[data-cy="filters-total-entitled-quantity-from"]'
    filters_total_entitled_quantity_to = 'div[data-cy="filters-total-entitled-quantity-to"]'
    date_picker_filter_from = 'div[data-cy="date-picker-filter-From"]'
    date_picker_filter_to = 'div[data-cy="date-picker-filter-To"]'
    button_filters_clear = 'button[data-cy="button-filters-clear"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    table_title = 'h6[data-cy="table-title"]'
    table_label = 'span[data-cy="table-label"]'
    status_container = 'div[data-cy="status-container"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    rows = '[role="checkbox"]'

    def get_business_area_container(self) -> WebElement:
        return self.wait_for(self.business_area_container)

    def get_global_program_filter_container(self) -> WebElement:
        return self.wait_for(self.global_program_filter_container)

    def get_global_program_filter(self) -> WebElement:
        return self.wait_for(self.global_program_filter)

    def get_menu_user_profile(self) -> WebElement:
        return self.wait_for(self.menu_user_profile)

    def get_side_nav(self) -> WebElement:
        return self.wait_for(self.side_nav)

    def get_drawer_items(self) -> WebElement:
        return self.wait_for(self.drawer_items)

    def get_nav_country_dashboard(self) -> WebElement:
        return self.wait_for(self.nav_country_dashboard)

    def get_nav_registration_data_import(self) -> WebElement:
        return self.wait_for(self.nav_registration_data_import)

    def get_nav_program_population(self) -> WebElement:
        return self.wait_for(self.nav_program_population)

    def get_nav_individuals(self) -> WebElement:
        return self.wait_for(self.nav_individuals)

    def get_nav_program_details(self) -> WebElement:
        return self.wait_for(self.nav_program_details)

    def get_nav_targeting(self) -> WebElement:
        return self.wait_for(self.nav_targeting)

    def get_nav_payment_module(self) -> WebElement:
        return self.wait_for(self.nav_payment_module)

    def get_nav_payment_verification(self) -> WebElement:
        return self.wait_for(self.nav_payment_verification)

    def get_nav_grievance(self) -> WebElement:
        return self.wait_for(self.nav_grievance)

    def get_nav_grievance_tickets(self) -> WebElement:
        return self.wait_for(self.nav_grievance_tickets)

    def get_nav_grievance_dashboard(self) -> WebElement:
        return self.wait_for(self.nav_grievance_dashboard)

    def get_nav_feedback(self) -> WebElement:
        return self.wait_for(self.nav_feedback)

    def get_nav_accountability(self) -> WebElement:
        return self.wait_for(self.nav_accountability)

    def get_nav_communication(self) -> WebElement:
        return self.wait_for(self.nav_communication)

    def get_nav_surveys(self) -> WebElement:
        return self.wait_for(self.nav_surveys)

    def get_nav_programme_users(self) -> WebElement:
        return self.wait_for(self.nav_programme_users)

    def get_nav_program_log(self) -> WebElement:
        return self.wait_for(self.nav_program_log)

    def get_nav_resources_knowledge_base(self) -> WebElement:
        return self.wait_for(self.nav_resources_knowledge_base)

    def get_nav_resources_conversations(self) -> WebElement:
        return self.wait_for(self.nav_resources_conversations)

    def get_nav_resources_tools_and_materials(self) -> WebElement:
        return self.wait_for(self.nav_resources_tools_and_materials)

    def get_nav_resources_release_note(self) -> WebElement:
        return self.wait_for(self.nav_resources_release_note)

    def get_main_content(self) -> WebElement:
        return self.wait_for(self.main_content)

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_select_filter(self) -> WebElement:
        return self.wait_for(self.select_filter)

    def get_filters_total_entitled_quantity_from(self) -> WebElement:
        return self.wait_for(self.filters_total_entitled_quantity_from)

    def get_filters_total_entitled_quantity_to(self) -> WebElement:
        return self.wait_for(self.filters_total_entitled_quantity_to)

    def get_date_picker_filter_from(self) -> WebElement:
        return self.wait_for(self.date_picker_filter_from)

    def get_date_picker_filter_to(self) -> WebElement:
        return self.wait_for(self.date_picker_filter_to)

    def get_button_filters_clear(self) -> WebElement:
        return self.wait_for(self.button_filters_clear)

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_table_label(self) -> [WebElement]:
        return self.get_elements(self.table_label)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_rows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)

    def get_row(self, number: int) -> WebElement:
        self.wait_for(self.rows)
        try:
            sleep(0.5)
            return self.get_elements(self.rows)[number]
        except BaseException:
            sleep(5)
            return self.get_elements(self.rows)[number]
