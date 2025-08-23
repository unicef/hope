from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class AccountabilitySurveys(BaseComponents):
    # Locators
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_new_survey = 'button[data-cy="button-new-survey"]'
    filters_search = 'div[data-cy="filters-search"]'
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
    menu_item_rapid_pro = 'li[data-cy="menu-item-rapid-pro"]'
    menu_item_rapid_pro_text = 'div[data-cy="menu-item-rapid-pro-text"]'
    menu_item_sms_text = 'li[data-cy="menu-item-sms-text"]'
    menu_item_manual = 'li[data-cy="menu-item-manual"]'
    menu_item_manual_text = 'div[data-cy="menu-item-manual-text"]'
    rows = 'tr[role="checkbox"]'

    # Texts
    text_title_page = "Surveys"
    text_new_survey = "New Survey"
    text_target_population_filter = "Target Population"
    text_tab_created_by = "Created by"

    # Elements
    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_new_survey(self) -> WebElement:
        return self.wait_for(self.button_new_survey)

    def get_filters_search(self) -> WebElement:
        return self.wait_for(self.filters_search)

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
        self.wait_for(self.table_label)
        return self.get_elements(self.table_label)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_menu_item_rapid_pro(self) -> WebElement:
        return self.wait_for(self.menu_item_rapid_pro)

    def get_menu_item_rapid_pro_text(self) -> WebElement:
        return self.wait_for(self.menu_item_rapid_pro_text)

    def get_menu_item_sms_text(self) -> WebElement:
        return self.wait_for(self.menu_item_sms_text)

    def get_menu_item_manual(self) -> WebElement:
        return self.wait_for(self.menu_item_manual)

    def get_menu_item_manual_text(self) -> WebElement:
        return self.wait_for(self.menu_item_manual_text)

    def get_rows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)
