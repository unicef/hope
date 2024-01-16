from helpers.helper import Common
from selenium.webdriver.remote.webelement import WebElement


class BaseComponents(Common):

    navProgrammeManagement = 'a[data-cy="nav-Programme Management"]'

    def getNavProgrammeManagement(self) -> WebElement:
        return self.wait_for(self.navProgrammeManagement)