from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ErrorPage(BaseComponents):
    # Locators
    pageNotFound = "h1"
    buttonRefresh = "button"
    buttonCountryDashboard = 'button[data-cy="button-go-back"]'

    # Texts
    text404Error = "Access Denied"
    textRefresh = "REFRESH PAGE"
    textGoTo = "GO BACK"

    # Elements

    def getPageNoFound(self) -> WebElement:
        return self.wait_for(self.pageNotFound).contains(self.text404Error)

    def getButtonRefresh(self) -> WebElement:
        return self.wait_for(self.buttonRefresh).contains(self.textRefresh)

    def getGoToCountryDashboard(self) -> WebElement:
        return self.wait_for(self.buttonCountryDashboard).contains(self.textGoTo)
