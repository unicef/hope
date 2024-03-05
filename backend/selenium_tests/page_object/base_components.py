from helpers.helper import Common
from selenium.webdriver.remote.webelement import WebElement


class BaseComponents(Common):
    navProgrammeManagement = 'a[data-cy="nav-Programme Management"]'
    navGrievance = ''
    navFeedback = ''
    navGrievanceTicket = ''

    def getNavProgrammeManagement(self) -> WebElement:
        return self.wait_for(self.navProgrammeManagement)

    def getNavFeedback(self) -> WebElement:
        return self.wait_for(self.navFeedback)

    def getNavGrievance(self) -> WebElement:
        return self.wait_for(self.navGrievance)