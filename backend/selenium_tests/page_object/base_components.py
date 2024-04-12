from helpers.helper import Common
from selenium.webdriver.remote.webelement import WebElement


class BaseComponents(Common):
    # Labels
    businessAreaContainer = 'div[data-cy="business-area-container"]'
    globalProgramFilterContainer = 'div[data-cy="global-program-filter-container"]'
    globalProgramFilter = 'div[data-cy="global-program-filter"]'
    menuUserProfile = 'button[data-cy="menu-user-profile"]'
    sideNav = 'div[data-cy="side-nav"]'
    navCountryDashboard = 'a[data-cy="nav-Country Dashboard"]'
    navRegistrationDataImport = 'a[data-cy="nav-Registration Data Import"]'
    navProgrammePopulation = 'a[data-cy="nav-Program Population"]'
    navHouseholds = 'a[data-cy="nav-Households"]'
    navIndividuals = 'a[data-cy="nav-Individuals"]'
    navProgrammeManagement = 'a[data-cy="nav-Programs"]'
    navProgrammeDetails = 'a[data-cy="nav-Program Details"]'
    navTargeting = 'a[data-cy="nav-Targeting"]'
    navCashAssist = 'a[data-cy="nav-Cash Assist"]'
    navPaymentModule = 'a[data-cy="nav-Payment Module"]'
    navPaymentVerification = 'a[data-cy="nav-Payment Verification"]'
    navGrievance = 'a[data-cy="nav-Grievance"]'
    navGrievanceTickets = 'a[data-cy="nav-Grievance Tickets"]'
    navGrievanceDashboard = 'a[data-cy="nav-Grievance Dashboard"]'
    navFeedback = 'a[data-cy="nav-Feedback"]'
    navAccountability = 'a[data-cy="nav-Accountability"]'
    navCommunication = 'a[data-cy="nav-Communication"]'
    navSurveys = 'a[data-cy="nav-Surveys"]'
    navProgrammeUsers = 'a[data-cy="nav-Programme Users"]'
    navActivityLog = 'a[data-cy="nav-Activity Log"]'
    navResourcesKnowledgeBase = 'a[data-cy="nav-resources-Knowledge Base"]'
    navResourcesConversations = 'a[data-cy="nav-resources-Conversations"]'
    navResourcesToolsAndMaterials = 'a[data-cy="nav-resources-Tools and Materials"]'
    navResourcesReleaseNote = 'a[data-cy="nav-resources-Release Note"]'
    mainContent = 'div[data-cy="main-content"]'
    drawerItems = 'div[data-cy="drawer-items"]'
    drawerInactiveSubheader = 'div[data-cy="program-inactive-subheader"]'

    # Text
    globalProgramFilterText = "All Programmes"

    def getMainContent(self) -> WebElement:
        return self.wait_for(self.mainContent)

    def getBusinessAreaContainer(self) -> WebElement:
        return self.wait_for(self.businessAreaContainer)

    def getGlobalProgramFilterContainer(self) -> WebElement:
        return self.wait_for(self.globalProgramFilterContainer)

    def getGlobalProgramFilter(self) -> WebElement:
        return self.wait_for(self.globalProgramFilter)

    def getMenuUserProfile(self) -> WebElement:
        return self.wait_for(self.menuUserProfile)

    def getSideNav(self) -> WebElement:
        return self.wait_for(self.sideNav)

    def getNavCountryDashboard(self) -> WebElement:
        return self.wait_for(self.navCountryDashboard)

    def getNavRegistrationDataImport(self) -> WebElement:
        return self.wait_for(self.navRegistrationDataImport)

    def getNavProgrammePopulation(self) -> WebElement:
        return self.wait_for(self.navProgrammePopulation)

    def getNavHouseholds(self) -> WebElement:
        return self.wait_for(self.navHouseholds)

    def getNavIndividuals(self) -> WebElement:
        return self.wait_for(self.navIndividuals)

    def getNavProgrammeManagement(self) -> WebElement:
        return self.wait_for(self.navProgrammeManagement)

    def getNavProgrammeDetails(self) -> WebElement:
        return self.wait_for(self.navProgrammeDetails)

    def getNavTargeting(self) -> WebElement:
        return self.wait_for(self.navTargeting)

    def getNavCashAssist(self) -> WebElement:
        return self.wait_for(self.navCashAssist)

    def getNavPaymentModule(self) -> WebElement:
        return self.wait_for(self.navPaymentModule)

    def getNavPaymentVerification(self) -> WebElement:
        return self.wait_for(self.navPaymentVerification)

    def getNavGrievance(self) -> WebElement:
        return self.wait_for(self.navGrievance)

    def getNavGrievanceTickets(self) -> WebElement:
        return self.wait_for(self.navGrievanceTickets)

    def getNavGrievanceDashboard(self) -> WebElement:
        return self.wait_for(self.navGrievanceDashboard)

    def getNavFeedback(self) -> WebElement:
        return self.wait_for(self.navFeedback)

    def getNavAccountability(self) -> WebElement:
        return self.wait_for(self.navAccountability)

    def getNavCommunication(self) -> WebElement:
        return self.wait_for(self.navCommunication)

    def getNavSurveys(self) -> WebElement:
        return self.wait_for(self.navSurveys)

    def getNavProgrammeUsers(self) -> WebElement:
        return self.wait_for(self.navProgrammeUsers)

    def getNavActivityLog(self) -> WebElement:
        return self.wait_for(self.navActivityLog)

    def getNavResourcesKnowledgeBase(self) -> WebElement:
        return self.wait_for(self.navResourcesKnowledgeBase)

    def getNavResourcesConversations(self) -> WebElement:
        return self.wait_for(self.navResourcesConversations)

    def getNavResourcesToolsAndMaterials(self) -> WebElement:
        return self.wait_for(self.navResourcesToolsAndMaterials)

    def getNavResourcesReleaseNote(self) -> WebElement:
        return self.wait_for(self.navResourcesReleaseNote)

    def getDrawerItems(self) -> WebElement:
        return self.wait_for(self.drawerItems)

    def selectGlobalProgramFilter(self, name: str) -> WebElement:
        self.getGlobalProgramFilter().click()
        return self.select_listbox_element(name)

    def getdrawerInactiveSubheader(self, timeout=Common.DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_for(self.drawerInactiveSubheader, timeout=timeout)
