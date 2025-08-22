from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ErrorPage(BaseComponents):
    # Locators
    page_not_found = "h1"
    button_refresh = "button"
    button_country_dashboard = 'button[data-cy="button-go-back"]'

    # Texts
    text_404_error = "Access Denied"
    text_refresh = "REFRESH PAGE"
    text_go_to = "GO BACK"

    # Elements

    def get_page_no_found(self) -> WebElement:
        return self.wait_for(self.page_not_found).contains(self.text_404_error)

    def get_button_refresh(self) -> WebElement:
        return self.wait_for(self.button_refresh).contains(self.text_refresh)

    def get_go_to_country_dashboard(self) -> WebElement:
        return self.wait_for(self.button_country_dashboard).contains(self.text_go_to)
