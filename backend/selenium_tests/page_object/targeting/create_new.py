from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class CreateNew(BaseComponents):
    # Locators
    targetingCriteria = 'h6[data-cy="title-targeting-criteria"]'
    # Texts
    textTargetingCriteria = "Targeting Criteria"
    # Elements

    def getTargetingCriteria(self) -> WebElement:
        return self.wait_for(self.targetingCriteria)
