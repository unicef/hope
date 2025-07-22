from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class People(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    indFiltersSearch = 'div[data-cy="ind-filters-search"]'
    selectFilter = 'div[data-cy="select-filter"]'
    filtersDocumentType = 'div[data-cy="filters-document-type"]'
    filtersDocumentNumber = 'div[data-cy="filters-document-number"]'
    indFiltersAdmin1 = 'div[data-cy="ind-filters-admin1"]'
    adminLevel1Input = 'div[data-cy="Admin Level 1-input"]'
    indFiltersAdmin2 = 'div[data-cy="ind-filters-admin2"]'
    adminLevel2Input = 'div[data-cy="Admin Level 2-input"]'
    indFiltersGender = 'div[data-cy="ind-filters-gender"]'
    indFiltersAgeFrom = 'div[data-cy="ind-filters-age-from"]'
    indFiltersAgeTo = 'div[data-cy="ind-filters-age-to"]'
    indFiltersFlags = 'div[data-cy="ind-filters-flags"]'
    indFiltersOrderBy = 'div[data-cy="ind-filters-order-by"]'
    indFiltersStatus = 'div[data-cy="ind-filters-status"]'
    indFiltersRegDateFrom = 'div[data-cy="ind-filters-reg-date-from"]'
    indFiltersRegDateTo = 'div[data-cy="ind-filters-reg-date-to"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    pageDetailsContainer = 'div[data-cy="page-details-container"]'
    tableTitle = 'h6[data-cy="table-title"]'
    sanctionListPossibleMatch = 'th[data-cy="sanction-list-possible-match"]'
    tableLabel = 'span[data-cy="table-label"]'
    individualId = 'th[data-cy="individual-id"]'
    individualName = 'th[data-cy="individual-name"]'
    individualAge = 'th[data-cy="individual-age"]'
    individualSex = 'th[data-cy="individual-sex"]'
    individualLocation = 'th[data-cy="individual-location"]'
    tableRow = 'tr[data-cy="table-row"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    individualTableRow = 'tr[data-cy="individual-table-row"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getIndFiltersSearch(self) -> WebElement:
        return self.wait_for(self.indFiltersSearch)

    def getSelectFilter(self) -> WebElement:
        return self.wait_for(self.selectFilter)

    def getFiltersDocumentType(self) -> WebElement:
        return self.wait_for(self.filtersDocumentType)

    def getFiltersDocumentNumber(self) -> WebElement:
        return self.wait_for(self.filtersDocumentNumber)

    def getIndFiltersAdmin1(self) -> WebElement:
        return self.wait_for(self.indFiltersAdmin1)

    def getAdminLevel1Input(self) -> WebElement:
        return self.wait_for(self.adminLevel1Input)

    def getIndFiltersAdmin2(self) -> WebElement:
        return self.wait_for(self.indFiltersAdmin2)

    def getAdminLevel2Input(self) -> WebElement:
        return self.wait_for(self.adminLevel2Input)

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

    def getIndFiltersRegDateFrom(self) -> WebElement:
        return self.wait_for(self.indFiltersRegDateFrom)

    def getIndFiltersRegDateTo(self) -> WebElement:
        return self.wait_for(self.indFiltersRegDateTo)

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

    def getIndividualAge(self) -> WebElement:
        return self.wait_for(self.individualAge)

    def getIndividualSex(self) -> WebElement:
        return self.wait_for(self.individualSex)

    def getIndividualLocation(self) -> WebElement:
        return self.wait_for(self.individualLocation)

    def getTableRow(self) -> WebElement:
        return self.wait_for(self.tableRow)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getIndividualTableRow(self, number: int) -> WebElement:
        self.wait_for(self.individualTableRow)
        return self.get_elements(self.individualTableRow)[number]
