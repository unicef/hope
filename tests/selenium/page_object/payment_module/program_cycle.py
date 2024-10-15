from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.page_object.base_components import BaseComponents


class ProgramCyclePage(BaseComponents):
    mainContent = 'div[data-cy="main-content"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    selectFilter = 'div[data-cy="select-filter"]'
    datePickerFilter = 'div[data-cy="date-picker-filter-"]'
    datePickerFilterFrom = 'div[data-cy="date-picker-filter-"]'
    datePickerFilterTo = 'div[data-cy="date-picker-filter-"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'h6[data-cy="table-title"]'
    headCellId = 'th[data-cy="head-cell-id"]'
    tableLabel = 'span[data-cy="table-label"]'
    headCellProgrammeCyclesTitle = 'th[data-cy="head-cell-programme-cycles-title"]'
    headCellStatus = 'th[data-cy="head-cell-status"]'
    headCellTotalEntitledQuantity = 'th[data-cy="head-cell-total-entitled-quantity"]'
    headCellStartDate = 'th[data-cy="head-cell-start-date"]'
    headCellEndDate = 'th[data-cy="head-cell-end-date"]'
    headCellEmpty = 'th[data-cy="head-cell-empty"]'
    programCycleRow = 'tr[data-cy="program-cycle-row"]'
    programCycleId = 'td[data-cy="program-cycle-id"]'
    programCycleTitle = 'td[data-cy="program-cycle-title"]'
    programCycleStatus = 'td[data-cy="program-cycle-status"]'
    programCycleTotalEntitledQuantity = 'td[data-cy="program-cycle-total-entitled-quantity"]'
    programCycleStartDate = 'td[data-cy="program-cycle-start-date"]'
    programCycleEndDate = 'td[data-cy="program-cycle-end-date"]'
    programCycleDetailsBtn = 'td[data-cy="program-cycle-details-btn"]'
    tablePagination = 'div[data-cy="table-pagination"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getSelectFilter(self) -> WebElement:
        return self.wait_for(self.selectFilter)

    def getDatePickerFilter(self) -> WebElement:
        return self.wait_for(self.datePickerFilter)

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

    def getHeadCellId(self) -> WebElement:
        return self.wait_for(self.headCellId)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getHeadCellProgrammeCyclesTitle(self) -> WebElement:
        return self.wait_for(self.headCellProgrammeCyclesTitle)

    def getHeadCellStatus(self) -> WebElement:
        return self.wait_for(self.headCellStatus)

    def getHeadCellTotalEntitledQuantity(self) -> WebElement:
        return self.wait_for(self.headCellTotalEntitledQuantity)

    def getHeadCellStartDate(self) -> WebElement:
        return self.wait_for(self.headCellStartDate)

    def getHeadCellEndDate(self) -> WebElement:
        return self.wait_for(self.headCellEndDate)

    def getHeadCellEmpty(self) -> WebElement:
        return self.wait_for(self.headCellEmpty)

    def getProgramCycleRow(self) -> [WebElement]:
        self.wait_for(self.programCycleRow)
        return self.get_elements(self.programCycleRow)

    def getProgramCycleStatus(self) -> WebElement:
        return self.wait_for(self.programCycleStatus)

    def getProgramCycleTotalEntitledQuantity(self) -> WebElement:
        return self.wait_for(self.programCycleTotalEntitledQuantity)

    def getProgramCycleStartDate(self) -> WebElement:
        return self.wait_for(self.programCycleStartDate)

    def getProgramCycleEndDate(self) -> WebElement:
        return self.wait_for(self.programCycleEndDate)

    def getProgramCycleStartDateList(self) -> [WebElement]:
        self.wait_for(self.programCycleStartDate)
        return self.get_elements(self.programCycleStartDate)

    def getProgramCycleEndDateList(self) -> [WebElement]:
        self.wait_for(self.programCycleEndDate)
        return self.get_elements(self.programCycleEndDate)

    def getProgramCycleDetailsBtn(self) -> WebElement:
        return self.wait_for(self.programCycleDetailsBtn)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getTableProgramCycleTitle(self) -> [WebElement]:
        return self.get_elements(self.programCycleTitle)

    def getProgramCycleId(self) -> WebElement:
        return self.wait_for(self.programCycleId)
