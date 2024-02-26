from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class RegistrationDataImport(BaseComponents):
    # Locators
    buttonImport = 'button[data-cy="button-import"]'

    # Texts

    # Elements

    def getButtonImport(self) -> WebElement:
        return self.wait_for(self.buttonImport)
