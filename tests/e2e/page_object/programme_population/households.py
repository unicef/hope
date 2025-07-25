from e2e.page_object.base_components import BaseComponents
from e2e.webdriver.remote.webelement import WebElement


class Households(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    hhFiltersSearch = 'div[data-cy="hh-filters-search"]'
    filterDocumentType = 'div[data-cy="filters-document-type"]'
    hhFiltersResidenceStatus = 'div[data-cy="hh-filters-residence-status"]'
    hhFiltersAdmin2 = 'div[data-cy="hh-filters-admin2"]'
    adminLevel2Input = 'div[data-cy="Admin Level 2-input"]'
    hhFiltersHouseholdSizeFrom = 'div[data-cy="hh-filters-household-size-from"]'
    hhFiltersHouseholdSizeTo = 'div[data-cy="hh-filters-household-size-to"]'
    hhFiltersOrderBy = 'div[data-cy="hh-filters-order-by"]'
    hhFiltersStatus = 'div[data-cy="hh-filters-status"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    pageDetailsContainer = 'div[data-cy="page-details-container"]'
    tableTitle = 'h6[data-cy="table-title"]'
    sanctionListPossibleMatch = 'th[data-cy="sanction-list-possible-match"]'
    tableLabel = 'span[data-cy="table-label"]'
    householdId = 'th[data-cy="household-id"]'
    status = 'th[data-cy="status"]'
    householdHeadName = 'th[data-cy="household-head-name"]'
    householdSize = 'th[data-cy="household-size"]'
    householdLocation = 'th[data-cy="household-location"]'
    householdResidenceStatus = 'th[data-cy="household-residence-status"]'
    householdTotalCashReceived = 'th[data-cy="household-total-cash-received"]'
    householdRegistrationDate = 'th[data-cy="household-registration-date"]'
    tableRow = 'tr[data-cy="table-row"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    householdTableRow = 'tr[data-cy="household-table-row"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getHhFiltersSearch(self) -> WebElement:
        return self.wait_for(self.hhFiltersSearch)

    def getFilterDocumentType(self) -> WebElement:
        return self.wait_for(self.filterDocumentType)

    def getHhFiltersResidenceStatus(self) -> WebElement:
        return self.wait_for(self.hhFiltersResidenceStatus)

    def getHhFiltersAdmin2(self) -> WebElement:
        return self.wait_for(self.hhFiltersAdmin2)

    def getAdminLevel2Input(self) -> WebElement:
        return self.wait_for(self.adminLevel2Input)

    def getHhFiltersHouseholdSizeFrom(self) -> WebElement:
        return self.wait_for(self.hhFiltersHouseholdSizeFrom)

    def getHhFiltersHouseholdSizeTo(self) -> WebElement:
        return self.wait_for(self.hhFiltersHouseholdSizeTo)

    def getHhFiltersOrderBy(self) -> WebElement:
        return self.wait_for(self.hhFiltersOrderBy)

    def getHhFiltersStatus(self) -> WebElement:
        return self.wait_for(self.hhFiltersStatus)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getPageDetailsContainer(self) -> WebElement:
        return self.wait_for(self.pageDetailsContainer)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getSanctionListPossibleMatch(self) -> WebElement:
        return self.wait_for(self.sanctionListPossibleMatch)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getHouseholdId(self) -> WebElement:
        return self.wait_for(self.householdId)

    def getStatus(self) -> WebElement:
        return self.wait_for(self.status)

    def getHouseholdHeadName(self) -> WebElement:
        return self.wait_for(self.householdHeadName)

    def getHouseholdSize(self) -> WebElement:
        return self.wait_for(self.householdSize)

    def getHouseholdLocation(self) -> WebElement:
        return self.wait_for(self.householdLocation)

    def getHouseholdResidenceStatus(self) -> WebElement:
        return self.wait_for(self.householdResidenceStatus)

    def getHouseholdTotalCashReceived(self) -> WebElement:
        return self.wait_for(self.householdTotalCashReceived)

    def getHouseholdRegistrationDate(self) -> WebElement:
        return self.wait_for(self.householdRegistrationDate)

    def getTableRow(self) -> WebElement:
        return self.wait_for(self.tableRow)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getHouseholdTableRows(self) -> WebElement:
        return self.wait_for(self.householdTableRow)

    def getHouseholdsRows(self) -> list[WebElement]:
        self.getHouseholdTableRows()
        return self.get_elements(self.householdTableRow)

    def getHouseholdsRowByNumber(self, number: int) -> WebElement:
        return self.getHouseholdsRows()[number]
