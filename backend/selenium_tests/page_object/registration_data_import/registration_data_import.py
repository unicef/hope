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

    def MaingetContent(self) -> WebElement:
        return self.wait_for(self.mainContent)

    def PagegetHeadergetContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def PagegetHeadergetTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def ButtongetNewgetProgram(self) -> WebElement:
        return self.wait_for(self.buttonNewProgram)

    def FiltersgetSearch(self) -> WebElement:
        return self.wait_for(self.filtersSearch)

    def FiltersgetStatus(self) -> WebElement:
        return self.wait_for(self.filtersStatus)

    def DategetPickergetFilter(self) -> WebElement:
        return self.wait_for(self.datePickerFilter)

    def DategetPickergetFilter(self) -> WebElement:
        return self.wait_for(self.datePickerFilter)

    def FiltersgetSector(self) -> WebElement:
        return self.wait_for(self.filtersSector)

    def FiltersgetNumbergetOfgetHouseholdsgetMin(self) -> WebElement:
        return self.wait_for(self.filtersNumberOfHouseholdsMin)

    def FiltersgetNumbergetOfgetHouseholdsgetMax(self) -> WebElement:
        return self.wait_for(self.filtersNumberOfHouseholdsMax)

    def FiltersgetBudgetgetMin(self) -> WebElement:
        return self.wait_for(self.filtersBudgetMin)

    def FiltersgetBudgetgetMax(self) -> WebElement:
        return self.wait_for(self.filtersBudgetMax)

    def FiltersgetDatagetCollectinggetType(self) -> WebElement:
        return self.wait_for(self.filtersDataCollectingType)

    def ButtongetFiltersgetClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def ButtongetFiltersgetApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def TablegetTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def TablegetLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def TablegetLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def TablegetLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def TablegetLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def TablegetLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def TablegetLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def TablegetRowgetDraftgetProgram(self) -> WebElement:
        return self.wait_for(self.tableRowDraftProgram)

    def StatusgetContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def TablegetRowgetTestgetProgramm(self) -> WebElement:
        return self.wait_for(self.tableRowTestProgramm)

    def StatusgetContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def TablegetPagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)
