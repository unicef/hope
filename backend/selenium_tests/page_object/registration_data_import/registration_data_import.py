from time import sleep

from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class RegistrationDataImport(BaseComponents):
    # Locators
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
    tableRow = 'tr[role="checkbox"]'
    importTypeSelect = 'div[data-cy="import-type-select"]'
    koboProjectSelect = 'div[data-cy="kobo-project-select"]'
    progressCircle = 'span[role="progressbar"]'
    downloadTemplate = 'a[data-cy="a-download-template"]'
    buttonImportRDI = 'button[data-cy="button-import-rdi"]'
    excelItem = 'li[data-cy="excel-menu-item"]'
    koboItem = 'li[data-cy="kobo-menu-item"]'
    inputName = 'input[data-cy="input-name"]'
    inputFile = 'input[type="file"]'
    numberOfHouseholds = 'div[data-cy="number-of-households"]'
    numberOfIndividuals = 'div[data-cy="number-of-individuals"]'
    errorsContainer = 'div[data-cy="errors-container"]'

    # Texts
    titleText = "Registration Data Import"
    importText = "IMPORT"
    tableTitleText = "List of Imports"
    importTypeSelectText = "Import From"
    downloadTemplateText = "DOWNLOAD TEMPLATE"
    koboItemText = "Kobo"
    excelItemText = "Excel"
    inputFileText = "UPLOAD FILE"

    # Elements

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
        return self.get_elements(self.tableLabel)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getRows(self) -> list[WebElement]:
        return self.get_elements(self.tableRow)

    def expectedRows(self, number: int) -> bool:
        for _ in range(15):
            if len(self.getRows()) == number:
                return True
            sleep(1)
        return False

    def getImportTypeSelect(self) -> WebElement:
        return self.wait_for(self.importTypeSelect)

    def getKoboProjectSelect(self) -> WebElement:
        return self.wait_for(self.koboProjectSelect)

    def checkLoadingProgressCircle(self) -> None:
        self.wait_for(self.progressCircle)
        self.wait_for_disappear(self.progressCircle)

    def getDownloadTemplate(self) -> WebElement:
        return self.wait_for(self.downloadTemplate)

    def getButtonImportFile(self) -> WebElement:
        return self.wait_for(self.buttonImportRDI)

    def disappearButtonImportFile(self) -> None:
        self.wait_for_disappear(self.buttonImportRDI, timeout=30)

    def getExcelItem(self) -> WebElement:
        return self.wait_for(self.excelItem)

    def getKoboItem(self) -> WebElement:
        return self.wait_for(self.koboItem)

    def getInputName(self) -> WebElement:
        return self.wait_for(self.inputName)

    def getInputFile(self) -> WebElement:
        return self.wait_for(self.inputFile)

    def getNumberOfHouseholds(self) -> WebElement:
        return self.wait_for(self.numberOfHouseholds)

    def getNumberOfIndividuals(self) -> WebElement:
        return self.wait_for(self.numberOfIndividuals)

    def getErrorsContainer(self) -> WebElement:
        return self.wait_for(self.errorsContainer)

    def buttonImportFileIsEnabled(self, timeout: int = 30) -> bool:
        for i in range(timeout):
            print(self.getButtonImportFile().is_enabled())
            self.screenshot(str(i))
            if self.getButtonImportFile().is_enabled():  # type: ignore
                return True
            sleep(1)
        return False
