from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ProgrammeUsers(BaseComponents):
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    buttonTargetPopulationCreateNew = 'a[data-cy="button-target-population-create-new"]'
    selectFilter = 'div[data-cy="select-filter"]'
    partnerFilter = 'div[data-cy="partner-filter"]'
    roleFilter = 'div[data-cy="role-filter"]'
    statusFilter = 'div[data-cy="status-filter"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableLabel = 'span[data-cy="table-label"]'
    statusContainer = 'div[data-cy="status-container"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    arrowDown = 'button[data-cy="arrow-down"]'
    countryRole = 'div[data-cy="country-role"]'
    mappedCountryRole = 'div[data-cy="mapped-country-role"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonTargetPopulationCreateNew(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationCreateNew)

    def getSelectFilter(self) -> WebElement:
        return self.wait_for(self.selectFilter)

    def getPartnerFilter(self) -> WebElement:
        return self.wait_for(self.partnerFilter)

    def getRoleFilter(self) -> WebElement:
        return self.wait_for(self.roleFilter)

    def getStatusFilter(self) -> WebElement:
        return self.wait_for(self.statusFilter)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getTableLabel(self) -> [WebElement]:
        self.wait_for(self.tableLabel)
        return self.get_elements(self.tableLabel)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getArrowDown(self) -> WebElement:
        return self.wait_for(self.arrowDown)

    def getCountryRole(self) -> WebElement:
        return self.wait_for(self.countryRole)

    def getMappedCountryRole(self) -> WebElement:
        return self.wait_for(self.mappedCountryRole)
