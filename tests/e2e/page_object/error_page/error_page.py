from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class ErrorPage(BaseComponents):
    page_not_found_title = "h1"
    button_refresh_page = '[data-cy="button-refresh-page"]'
    button_go_to_programme_management = '[data-cy="go-to-programme-management"]'

    def get_button_refresh_page(self) -> WebElement:
        return self.wait_for(self.button_refresh_page)

    def get_button_go_to_programme_management(self) -> WebElement:
        return self.wait_for(self.button_go_to_programme_management)

    def navigate_to_non_existent_program(self, business_area_slug: str) -> None:
        self.driver.get(f"{self.driver.live_server.url}/{business_area_slug}/programs/NONEXISTENT/country-dashboard")

    def navigate_to_unknown_route(self, business_area_slug: str, program_code: str) -> None:
        self.driver.get(
            f"{self.driver.live_server.url}/{business_area_slug}/programs/{program_code}/this-route-does-not-exist"
        )
