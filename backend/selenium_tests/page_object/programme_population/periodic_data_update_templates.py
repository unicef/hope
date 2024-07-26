from selenium.webdriver.remote.webelement import WebElement

from page_object.base_components import BaseComponents


class PeriodicDatUpdateTemplates(BaseComponents):
    businessAreaContainer = 'div[data-cy="business-area-container"]'
    globalProgramFilterContainer = 'div[data-cy="global-program-filter-container"]'
    globalProgramFilter = 'button[data-cy="global-program-filter"]'
    menuUserProfile = 'button[data-cy="menu-user-profile"]'
    sideNav = 'div[data-cy="side-nav"]'
    drawerItems = 'div[data-cy="drawer-items"]'
    navCountryDashboard = 'a[data-cy="nav-Country Dashboard"]'
    navRegistrationDataImport = 'a[data-cy="nav-Registration Data Import"]'
    navProgramPopulation = 'a[data-cy="nav-Program Population"]'
    navHouseholds = 'a[data-cy="nav-Households"]'
    navHouseholdMembers = 'a[data-cy="nav-Household Members"]'
    navProgramDetails = 'a[data-cy="nav-Program Details"]'
    navTargeting = 'a[data-cy="nav-Targeting"]'
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
    navProgramLog = 'a[data-cy="nav-Program Log"]'
    navResourcesKnowledgeBase = 'a[data-cy="nav-resources-Knowledge Base"]'
    navResourcesConversations = 'a[data-cy="nav-resources-Conversations"]'
    navResourcesToolsAndMaterials = 'a[data-cy="nav-resources-Tools and Materials"]'
    navResourcesReleaseNote = 'a[data-cy="nav-resources-Release Note"]'
    mainContent = 'div[data-cy="main-content"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    tabIndividuals = 'button[data-cy="tab-individuals"]'
    tabPeriodicDataUpdates = 'button[data-cy="tab-periodic-data-updates"]'
    title = 'h6[data-cy="title"]'
    newTemplateButton = 'a[data-cy="new-template-button"]'
    buttonImport = 'button[data-cy="button-import"]'
    pduTemplatesBtn = 'button[data-cy="pdu-templates"]'
    pduUpdates = 'button[data-cy="pdu-updates"]'
    headCellTemplateId = 'th[data-cy="head-cell-template-id"]'
    tableLabel = 'span[data-cy="table-label"]'
    headCellNumberOfRecords = 'th[data-cy="head-cell-number-of-records"]'
    headCellCreatedAt = 'th[data-cy="head-cell-created-at"]'
    headCellCreatedBy = 'th[data-cy="head-cell-created-by"]'
    headCellDetails = 'th[data-cy="head-cell-details"]'
    headCellStatus = 'th[data-cy="head-cell-status"]'
    headCellEmpty = 'th[data-cy="head-cell-empty"]'
    templateRow = 'tr[data-cy="template-row-{}"]'
    templateId = 'td[data-cy="template-id-{}"]'
    templateRecords = 'td[data-cy="template-records-{}"]'
    templateCreatedAt = 'td[data-cy="template-created-at-{}"]'
    templateCreatedBy = 'td[data-cy="template-created-by-{}"]'
    templateDetailsBtn = 'td[data-cy="template-details-btn-{}"]'
    templateStatus = 'td[data-cy="template-status-{}"]'
    statusContainer = 'div[data-cy="status-container"]'
    templateAction = 'td[data-cy="template-action-{}"]'
    tablePagination = 'div[data-cy="table-pagination"]'

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

    def getDrawerItems(self) -> WebElement:
        return self.wait_for(self.drawerItems)

    def getNavCountryDashboard(self) -> WebElement:
        return self.wait_for(self.navCountryDashboard)

    def getNavRegistrationDataImport(self) -> WebElement:
        return self.wait_for(self.navRegistrationDataImport)

    def getNavProgramPopulation(self) -> WebElement:
        return self.wait_for(self.navProgramPopulation)

    def getNavHouseholds(self) -> WebElement:
        return self.wait_for(self.navHouseholds)

    def getNavHouseholdMembers(self) -> WebElement:
        return self.wait_for(self.navHouseholdMembers)

    def getNavProgramDetails(self) -> WebElement:
        return self.wait_for(self.navProgramDetails)

    def getNavTargeting(self) -> WebElement:
        return self.wait_for(self.navTargeting)

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

    def getNavProgramLog(self) -> WebElement:
        return self.wait_for(self.navProgramLog)

    def getNavResourcesKnowledgeBase(self) -> WebElement:
        return self.wait_for(self.navResourcesKnowledgeBase)

    def getNavResourcesConversations(self) -> WebElement:
        return self.wait_for(self.navResourcesConversations)

    def getNavResourcesToolsAndMaterials(self) -> WebElement:
        return self.wait_for(self.navResourcesToolsAndMaterials)

    def getNavResourcesReleaseNote(self) -> WebElement:
        return self.wait_for(self.navResourcesReleaseNote)

    def getMainContent(self) -> WebElement:
        return self.wait_for(self.mainContent)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getTabIndividuals(self) -> WebElement:
        return self.wait_for(self.tabIndividuals)

    def getTabPeriodicDataUpdates(self) -> WebElement:
        return self.wait_for(self.tabPeriodicDataUpdates)

    def getTitle(self) -> WebElement:
        return self.wait_for(self.title)

    def getNewTemplateButton(self) -> WebElement:
        return self.wait_for(self.newTemplateButton)

    def getButtonImport(self) -> WebElement:
        return self.wait_for(self.buttonImport)

    def getPduTemplatesBtn(self) -> WebElement:
        return self.wait_for(self.pduTemplatesBtn)

    def getPduUpdates(self) -> WebElement:
        return self.wait_for(self.pduUpdates)

    def getHeadCellTemplateId(self) -> WebElement:
        return self.wait_for(self.headCellTemplateId)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getHeadCellNumberOfRecords(self) -> WebElement:
        return self.wait_for(self.headCellNumberOfRecords)

    def getHeadCellCreatedAt(self) -> WebElement:
        return self.wait_for(self.headCellCreatedAt)

    def getHeadCellCreatedBy(self) -> WebElement:
        return self.wait_for(self.headCellCreatedBy)

    def getHeadCellDetails(self) -> WebElement:
        return self.wait_for(self.headCellDetails)

    def getHeadCellStatus(self) -> WebElement:
        return self.wait_for(self.headCellStatus)

    def getHeadCellEmpty(self) -> WebElement:
        return self.wait_for(self.headCellEmpty)

    def getTemplateRow(self) -> WebElement:
        return self.wait_for(self.templateRow)

    def getTemplateId(self, index: int) -> WebElement:
        locator = self.templateId.format(index)
        return self.wait_for(locator)

    def getTemplateRecords(self, index: int) -> WebElement:
        locator = self.templateRecords.format(index)
        return self.wait_for(locator)

    def getTemplateCreatedAt(self, index: int) -> WebElement:
        locator = self.templateCreatedAt.format(index)
        return self.wait_for(locator)

    def getTemplateCreatedBy(self, index: int) -> WebElement:
        locator = self.templateCreatedBy.format(index)
        return self.wait_for(locator)

    def getTemplateDetailsBtn(self, index: int) -> WebElement:
        locator = self.templateDetailsBtn.format(index)
        return self.wait_for(locator)

    def getTemplateStatus(self, index: int) -> WebElement:
        locator = self.templateStatus.format(index)
        return self.wait_for(locator)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTemplateAction(self) -> WebElement:
        return self.wait_for(self.templateAction)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)
