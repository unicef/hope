from time import sleep

from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.helpers.helper import Common


class BaseComponents(Common):
    # Labels
    businessAreaContainer = 'div[data-cy="business-area-container"]'
    globalProgramFilterContainer = 'div[data-cy="global-program-filter-container"]'
    globalProgramFilter = 'button[data-cy="global-program-filter"]'
    menuUserProfile = 'button[data-cy="menu-user-profile"]'
    sideNav = 'div[data-cy="side-nav"]'
    navCountryDashboard = 'a[data-cy="nav-Country Dashboard"]'
    navRegistrationDataImport = 'a[data-cy="nav-Registration Data Import"]'
    navProgrammePopulation = 'a[data-cy="nav-Programme Population"]'
    navHouseholds = 'a[data-cy="nav-Households"]'
    navIndividuals = 'a[data-cy="nav-Household Members"]'
    navPeople = 'a[data-cy="nav-People"]'
    navProgrammeManagement = 'a[data-cy="nav-Programmes"]'
    navManagerialConsole = 'a[data-cy="nav-Managerial Console"]'
    navProgrammeDetails = 'a[data-cy="nav-Programme Details"]'
    navTargeting = 'a[data-cy="nav-Targeting"]'
    navCashAssist = 'a[data-cy="nav-Cash Assist"]'
    navPaymentModule = 'a[data-cy="nav-Payment Module"]'
    navProgrammeCycles = 'a[data-cy="nav-Programme Cycles"]'
    navPaymentPlans = 'a[data-cy="nav-Payment Plans"]'
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
    navProgramLog = 'a[data-cy="nav-Programme Log"]'
    mainContent = 'div[data-cy="main-content"]'
    drawerItems = 'div[data-cy="drawer-items"]'
    drawerInactiveSubheader = 'div[data-cy="program-inactive-subheader"]'
    menuItemClearCache = 'li[data-cy="menu-item-clear-cache"]'
    globalProgramFilterSearchInput = 'input[data-cy="search-input-gpf"]'
    globalProgramFilterSearchButton = 'button[data-cy="search-icon"]'
    globalProgramFilterClearButton = 'button[data-cy="clear-icon"]'
    rows = 'tr[role="checkbox"]'
    alert = '[role="alert"]'
    breadcrumbsChevronIcon = 'svg[data-cy="breadcrumbs-chevron-icon"]'
    arrowBack = 'div[data-cy="arrow_back"]'

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

    def getNavPeople(self) -> WebElement:
        return self.wait_for(self.navPeople)

    def getNavProgrammeManagement(self) -> WebElement:
        return self.wait_for(self.navProgrammeManagement)

    def getNavManagerialConsole(self) -> WebElement:
        return self.wait_for(self.navManagerialConsole)

    def getNavProgrammeDetails(self) -> WebElement:
        return self.wait_for(self.navProgrammeDetails)

    def getNavTargeting(self) -> WebElement:
        return self.wait_for(self.navTargeting)

    def getNavCashAssist(self) -> WebElement:
        return self.wait_for(self.navCashAssist)

    def getNavPaymentModule(self) -> WebElement:
        return self.wait_for(self.navPaymentModule)

    def getNavPaymentPlans(self) -> WebElement:
        return self.wait_for(self.navPaymentPlans)

    def getNavProgrammeCycles(self) -> WebElement:
        return self.wait_for(self.navProgrammeCycles)

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

    def selectGlobalProgramFilter(self, name: str) -> None:
        # TODO: remove this one after fix bug with cache
        self.getMenuUserProfile().click()
        self.getMenuItemClearCache().click()

        self.getGlobalProgramFilter().click()
        if name != "All Programmes":
            self.getGlobalProgramFilterSearchInput().send_keys(name)
            self.getGlobalProgramFilterSearchButton().click()

            self.wait_for_text_disappear("All Programmes", '[data-cy="select-option-name"]')
        self.select_listbox_element(name)

    def getDrawerInactiveSubheader(self, timeout: int = Common.DEFAULT_TIMEOUT) -> WebElement:
        return self.wait_for(self.drawerInactiveSubheader, timeout=timeout)

    def getMenuItemClearCache(self) -> WebElement:
        return self.wait_for(self.menuItemClearCache)

    def getGlobalProgramFilterSearchButton(self) -> WebElement:
        return self.wait_for(self.globalProgramFilterSearchButton)

    def getGlobalProgramFilterSearchInput(self) -> WebElement:
        return self.wait_for(self.globalProgramFilterSearchInput)

    def getBreadcrumbsChevronIcon(self) -> WebElement:
        return self.wait_for(self.breadcrumbsChevronIcon)

    def getArrowBack(self) -> WebElement:
        return self.wait_for(self.arrowBack)

    def getNavProgramLog(self) -> WebElement:
        return self.wait_for(self.navProgramLog)

    def waitForRows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)

    def getRows(self) -> [WebElement]:
        return self.get_elements(self.rows)

    def getAlert(self) -> WebElement:
        return self.wait_for(self.alert)

    def checkAlert(self, text: str) -> None:
        self.getAlert()
        for _ in range(300):
            if text in self.getAlert().text:
                break
            sleep(0.1)
        assert text in self.getAlert().text

    def waitForNumberOfRows(self, number: int) -> bool:
        for _ in range(5):
            if len(self.getRows()) == number:
                return True
            sleep(1)
        return False
