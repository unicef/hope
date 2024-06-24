from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class AccountabilitySurveysDetails(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)
