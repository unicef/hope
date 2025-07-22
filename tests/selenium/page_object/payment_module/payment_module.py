from time import sleep

from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentModule(BaseComponents):
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    selectFilter = 'div[data-cy="select-filter"]'
    filtersTotalEntitledQuantityFrom = 'div[data-cy="filters-total-entitled-quantity-from"]'
    filtersTotalEntitledQuantityTo = 'div[data-cy="filters-total-entitled-quantity-to"]'
    datePickerFilterFrom = 'div[data-cy="date-picker-filter-From"]'
    datePickerFilterTo = 'div[data-cy="date-picker-filter-To"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableLabel = 'span[data-cy="table-label"]'
    statusContainer = 'div[data-cy="status-container"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    rows = '[role="checkbox"]'

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

    def getNavIndividuals(self) -> WebElement:
        return self.wait_for(self.navIndividuals)

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

    def getSelectFilter(self) -> WebElement:
        return self.wait_for(self.selectFilter)

    def getFiltersTotalEntitledQuantityFrom(self) -> WebElement:
        return self.wait_for(self.filtersTotalEntitledQuantityFrom)

    def getFiltersTotalEntitledQuantityTo(self) -> WebElement:
        return self.wait_for(self.filtersTotalEntitledQuantityTo)

    def getDatePickerFilterFrom(self) -> WebElement:
        return self.wait_for(self.datePickerFilterFrom)

    def getDatePickerFilterTo(self) -> WebElement:
        return self.wait_for(self.datePickerFilterTo)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getTableLabel(self) -> [WebElement]:
        return self.get_elements(self.tableLabel)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getRows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)

    def getRow(self, number: int) -> WebElement:
        self.wait_for(self.rows)
        try:
            sleep(0.5)
            return self.get_elements(self.rows)[number]
        except BaseException:
            sleep(5)
            return self.get_elements(self.rows)[number]
