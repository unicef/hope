from helpers.helper import Common
from selenium.webdriver.remote.webelement import WebElement


class BaseComponents(Common):
    globalProgramFilter = 'div[data-cy="global-program-filter"]'
    navProgrammeManagement = 'a[data-cy="nav-Programme Management"]'
    navGrievance = 'a[data-cy="nav-Grievance"]'
    navFeedback = 'a[data-cy="nav-Feedback"]'
    navGrievanceTicket = 'a[data-cy="nav-Grievance Tickets"]'
    navGrievanceDashboard = 'a[data-cy="nav-Grievance Dashboard"]'

    globalProgramFilterText = "All Programmes"

    def getNavProgrammeManagement(self) -> WebElement:
        return self.wait_for(self.navProgrammeManagement)

    def getNavFeedback(self) -> WebElement:
        return self.wait_for(self.navFeedback)

    def getNavGrievance(self) -> WebElement:
        return self.wait_for(self.navGrievance)

    def getGlobalProgramFilter(self) -> WebElement:
        return self.wait_for(self.globalProgramFilter)

    def selectGlobalProgramFilter(self, name: str) -> WebElement:
        self.getGlobalProgramFilter().click()
        return self.select_listbox_element(name)
