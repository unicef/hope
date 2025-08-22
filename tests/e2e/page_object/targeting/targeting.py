from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class Targeting(BaseComponents):
    # Locators
    title_page = 'h5[data-cy="page-header-title"]'
    search_filter = 'div[data-cy="filters-search"]'
    status_filter = 'div[data-cy="filters-status"]'
    program_filter = 'div[data-cy="filters-program"]'
    min_number_of_households = 'div[data-cy="filters-total-households-count-min"]'
    max_number_of_households = 'div[data-cy="filters-total-households-count-max"]'
    button_create_new = 'a[data-cy="button-new-tp"]'
    button_create_new_by_filters = 'li[data-cy="menu-item-filters"]'
    tab_title = 'h6[data-cy="table-title"]'
    tab_column_label = 'span[data-cy="table-label"]'
    status_options = 'li[role="option"]'
    rows = 'tr[role="checkbox"]'
    create_user_filters = 'div[data-cy="menu-item-filters-text"]'
    create_use_ids = 'div[data-cy="menu-item-ids-text"]'
    button_inactive_create_new = 'a[data-cy="button-target-population-create-new"]'
    tooltip = 'div[role="tooltip"]'
    status_container = 'div[data-cy="status-container"]'
    loading_rows = 'tr[data-cy="table-row"]'
    button_target_population = 'button[data-cy="button-target-population-info"]'
    button_apply = 'button[data-cy="button-filters-apply"]'
    button_clear = 'button[data-cy="button-filters-clear"]'
    tab_field_list = 'button[data-cy="tab-field-list"]'
    tab_targeting_diagram = 'button[data-cy="tab-targeting-diagram"]'
    name = 'th[data-cy="name"]'
    status = 'th[data-cy="status"]'
    num_of_households = 'th[data-cy="num-of-households"]'
    date_created = 'th[data-cy="date-created"]'
    last_edited = 'th[data-cy="last-edited"]'
    created_by = 'th[data-cy="created-by"]'

    # Texts
    text_title_page = "Targeting"
    text_create_new = "Create new"
    text_tab_title = "Target Populations"
    text_tab_name = "Name"
    text_tab_status = "Status"
    text_tab_programme = "Programme"
    text_tab_no_households = "Num. of Households"
    text_tab_date_created = "Date Created"
    text_tab_last_edited = "Last Edited"
    text_tab_created_by = "Created by"

    def navigate_to_page(self, business_area_slug: str, program_slug: str) -> None:
        self.driver.get(self.get_page_url(business_area_slug, program_slug))
        self.driver.refresh()

    def get_page_url(self, business_area_slug: str, program_slug: str) -> str:
        return f"{self.driver.live_server.url}/{business_area_slug}/programs/{program_slug}/target-population"

    # Elements

    def get_title_page(self) -> WebElement:
        return self.wait_for(self.title_page)

    def wait_for_text_title_page(self, text: str) -> bool:
        return self.wait_for_text(text, self.title_page)

    def get_search_filter(self) -> WebElement:
        return self.wait_for(self.search_filter)

    def get_status_filter(self) -> WebElement:
        return self.wait_for(self.status_filter)

    def get_program_filter(self) -> WebElement:
        return self.wait_for(self.program_filter)

    def get_min_number_of_households_filter(self) -> WebElement:
        return self.wait_for(self.min_number_of_households)

    def get_max_number_of_households_filter(self) -> WebElement:
        return self.wait_for(self.max_number_of_households)

    def get_button_create_new(self) -> WebElement:
        return self.wait_for(self.button_create_new)

    def get_button_create_new_by_filters(self) -> WebElement:
        return self.wait_for(self.button_create_new_by_filters)

    def get_tab_title(self) -> WebElement:
        return self.wait_for(self.tab_title)

    def get_tab_column_label(self) -> list[WebElement]:
        return self.get_elements(self.tab_column_label)

    def get_status_option(self) -> WebElement:
        return self.wait_for(self.status_options)

    def get_apply(self) -> WebElement:
        return self.wait_for(self.button_apply)

    def get_clear(self) -> WebElement:
        return self.wait_for(self.button_clear)

    def get_target_populations_rows(self) -> list[WebElement]:
        return self.get_elements(self.rows)

    def choose_target_populations(self, number: int) -> WebElement:
        try:
            self.wait_for(self.rows)
            return self.get_elements(self.rows)[number]
        except IndexError:
            sleep(1)
            return self.get_elements(self.rows)[number]

    def count_target_populations(self, number: int) -> None:
        for _ in range(50):
            if len(self.get_target_populations_rows()) == number:
                break
            sleep(0.1)
        else:
            raise TimeoutError(f"{len(self.get_target_populations_rows())} target populations instead of {number}")

    def get_create_use_filters(self) -> WebElement:
        return self.wait_for(self.create_user_filters)

    def get_create_use_ids(self) -> WebElement:
        return self.wait_for(self.create_use_ids)

    def get_button_inactive_create_new(self) -> WebElement:
        return self.wait_for(self.button_inactive_create_new)

    def get_tooltip(self) -> WebElement:
        return self.wait_for(self.tooltip)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_tab_field_list(self) -> WebElement:
        return self.wait_for(self.tab_field_list)

    def get_tab_targeting_diagram(self) -> WebElement:
        return self.wait_for(self.tab_targeting_diagram)

    def get_button_target_population(self) -> WebElement:
        return self.wait_for(self.button_target_population)

    def get_loading_rows(self) -> WebElement:
        return self.wait_for(self.loading_rows)

    def get_column_name(self) -> WebElement:
        return self.wait_for(self.name).find_element(By.CSS_SELECTOR, self.tab_column_label)

    def get_column_status(self) -> WebElement:
        return self.wait_for(self.status).find_element(By.CSS_SELECTOR, self.tab_column_label)

    def get_column_num_of_households(self) -> WebElement:
        return self.wait_for(self.num_of_households).find_element(By.CSS_SELECTOR, self.tab_column_label)

    def get_column_date_created(self) -> WebElement:
        return self.wait_for(self.date_created).find_element(By.CSS_SELECTOR, self.tab_column_label)

    def get_column_last_edited(self) -> WebElement:
        return self.wait_for(self.last_edited).find_element(By.CSS_SELECTOR, self.tab_column_label)

    def get_column_created_by(self) -> WebElement:
        return self.wait_for(self.created_by).find_element(By.CSS_SELECTOR, self.tab_column_label)

    def disappear_loading_rows(self) -> WebElement:
        try:
            self.get_loading_rows()
        except BaseException:
            self.get_status_container()
        return self.wait_for_disappear(self.loading_rows)
