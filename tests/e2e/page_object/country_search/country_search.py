from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class CountrySearch(BaseComponents):
    nav_country_search = 'a[data-cy="nav-Country Search"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    page_details_container = 'div[data-cy="page-details-container"]'
    search_for_select = "#search-for"
    office_search = 'div[data-cy="office-filters-search"]'
    button_filters_apply = 'button[data-cy="button-filters-apply"]'
    results_table = 'div[data-cy="page-details-container"] table'

    def get_nav_country_search(self) -> WebElement:
        return self.wait_for(self.nav_country_search)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_search_for_select(self) -> WebElement:
        return self.wait_for(self.search_for_select)

    def get_office_search_input(self) -> WebElement:
        return self.wait_for(f"{self.office_search} input")

    def get_button_filters_apply(self) -> WebElement:
        return self.wait_for(self.button_filters_apply)

    def select_search_for(self, value: str) -> None:
        self.get_search_for_select().click()
        self.wait_for('ul[role="listbox"]')
        self.wait_for(f'li[data-value="{value}"]').click()
        self.wait_for_disappear('ul[role="listbox"]')
