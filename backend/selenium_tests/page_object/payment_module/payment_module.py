from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentModule(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'

    # Texts
    textTitle = "Payment Module"

    # Elements
    def getTitle(self) -> WebElement:
        return self.wait_for(self.titlePage)
