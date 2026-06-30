from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class AccessDenied(BaseComponents):
    access_denied_title = "h1"
    button_refresh_page = '[data-cy="button-refresh-page"]'
    button_go_back = '[data-cy="button-go-back"]'

    def get_button_refresh_page(self) -> WebElement:
        return self.wait_for(self.button_refresh_page)

    def get_button_go_back(self) -> WebElement:
        return self.wait_for(self.button_go_back)

    def navigate_to_home(self) -> None:
        self.driver.get(f"{self.driver.live_server.url}/")
