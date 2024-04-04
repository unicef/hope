from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class IndividualsDetails(BaseComponents):
    mainContent = 'div[data-cy="main-content"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    indFiltersSearch = 'div[data-cy="ind-filters-search"]'
    filterSearchType = 'div[data-cy="filter-search-type"]'
    indFiltersGender = 'div[data-cy="ind-filters-gender"]'
    indFiltersAgeFrom = 'div[data-cy="ind-filters-age-from"]'
    indFiltersAgeTo = 'div[data-cy="ind-filters-age-to"]'
    indFiltersFlags = 'div[data-cy="ind-filters-flags"]'
    indFiltersOrderBy = 'div[data-cy="ind-filters-order-by"]'
    indFiltersStatus = 'div[data-cy="ind-filters-status"]'
    datePickerFilter = 'div[data-cy="date-picker-filter"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    pageDetailsContainer = 'div[data-cy="page-details-container"]'
    tableTitle = 'h6[data-cy="table-title"]'
    sanctionListPossibleMatch = 'th[data-cy="sanction-list-possible-match"]'
    tableLabel = 'span[data-cy="table-label"]'
    individualId = 'th[data-cy="individual-id"]'
    individualName = 'th[data-cy="individual-name"]'
    householdId = 'th[data-cy="household-id"]'
    relationship = 'th[data-cy="relationship"]'
    individualAge = 'th[data-cy="individual-age"]'
    individualSex = 'th[data-cy="individual-sex"]'
    individualLocation = 'th[data-cy="individual-location"]'
    individualTableRow = 'tr[data-cy="individual-table-row"]'
    tablePagination = 'div[data-cy="table-pagination"]'

    def getMainContent(self) -> WebElement:
        return self.wait_for(self.mainContent)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getIndFiltersSearch(self) -> WebElement:
        return self.wait_for(self.indFiltersSearch)

    def getFilterSearchType(self) -> WebElement:
        return self.wait_for(self.filterSearchType)

    def getIndFiltersGender(self) -> WebElement:
        return self.wait_for(self.indFiltersGender)

    def getIndFiltersAgeFrom(self) -> WebElement:
        return self.wait_for(self.indFiltersAgeFrom)

    def getIndFiltersAgeTo(self) -> WebElement:
        return self.wait_for(self.indFiltersAgeTo)

    def getIndFiltersFlags(self) -> WebElement:
        return self.wait_for(self.indFiltersFlags)

    def getIndFiltersOrderBy(self) -> WebElement:
        return self.wait_for(self.indFiltersOrderBy)

    def getIndFiltersStatus(self) -> WebElement:
        return self.wait_for(self.indFiltersStatus)

    def getDatePickerFilter(self) -> WebElement:
        return self.wait_for(self.datePickerFilter)

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

    def getIndividualId(self) -> WebElement:
        return self.wait_for(self.individualId)

    def getIndividualName(self) -> WebElement:
        return self.wait_for(self.individualName)

    def getHouseholdId(self) -> WebElement:
        return self.wait_for(self.householdId)

    def getRelationship(self) -> WebElement:
        return self.wait_for(self.relationship)

    def getIndividualAge(self) -> WebElement:
        return self.wait_for(self.individualAge)

    def getIndividualSex(self) -> WebElement:
        return self.wait_for(self.individualSex)

    def getIndividualLocation(self) -> WebElement:
        return self.wait_for(self.individualLocation)

    def getIndividualTableRow(self) -> WebElement:
        return self.wait_for(self.individualTableRow)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)
