from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class RegistrationDataImport(BaseComponents):
    # Locators
    mainContent = 'div[data-cy="main-content"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonImport = 'button[data-cy="button-import"]'
    filterSearch = 'div[data-cy="filter-search"]'
    importedByInput = 'div[data-cy="Imported By-input"]'
    filterStatus = 'div[data-cy="filter-status"]'
    filterSizeMin = 'div[data-cy="filter-size-min"]'
    filterSizeMax = 'div[data-cy="filter-size-max"]'
    datePickerFilter = 'div[data-cy="date-picker-filter"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableLabel = 'span[data-cy="table-label"]'
    statusContainer = 'div[data-cy="status-container"]'
    tablePagination = 'div[data-cy="table-pagination"]'

    # Texts

    # Elements

    def getMainContent(self) -> WebElement:
        return self.wait_for(self.mainContent)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonImport(self) -> WebElement:
        return self.wait_for(self.buttonImport)

    def getFilterSearch(self) -> WebElement:
        return self.wait_for(self.filterSearch)

    def getImportedByInput(self) -> WebElement:
        return self.wait_for(self.importedByInput)

    def getFilterStatus(self) -> WebElement:
        return self.wait_for(self.filterStatus)

    def getFilterSizeMin(self) -> WebElement:
        return self.wait_for(self.filterSizeMin)

    def getFilterSizeMax(self) -> WebElement:
        return self.wait_for(self.filterSizeMax)

    def getDatePickerFilter(self) -> WebElement:
        return self.wait_for(self.datePickerFilter)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)
