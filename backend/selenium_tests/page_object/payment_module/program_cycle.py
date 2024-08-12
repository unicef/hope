from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


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
        return self.get_elements(self.programCycleRow)

    def getProgramCycleStatus(self) -> WebElement:
        return self.wait_for(self.programCycleStatus)

    def getProgramCycleTotalEntitledQuantity(self) -> WebElement:
        return self.wait_for(self.programCycleTotalEntitledQuantity)

    def getProgramCycleStartDate(self) -> WebElement:
        return self.wait_for(self.programCycleStartDate)

    def getProgramCycleEndDate(self) -> WebElement:
        return self.wait_for(self.programCycleEndDate)

    def getProgramCycleDetailsBtn(self) -> WebElement:
        return self.wait_for(self.programCycleDetailsBtn)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getTableProgramCycleTitle(self) -> WebElement:
        return self.get_elements(self.programCycleTitle)

    def getProgramCycleId(self) -> WebElement:
        return self.wait_for(self.programCycleId)


class ProgramCycleDetailsPage(BaseComponents):
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonCreatePaymentPlan = 'a[data-cy="button-create-payment-plan"]'
    buttonFinishProgrammeCycle = 'button[data-cy="button-finish-programme-cycle"]'
    statusContainer = 'div[data-cy="status-container"]'
    labelCreatedBy = 'div[data-cy="label-Created By"]'
    labelStartDate = 'div[data-cy="label-Start Date"]'
    labelEndDate = 'div[data-cy="label-End Date"]'
    labelProgrammeStartDate = 'div[data-cy="label-Programme Start Date"]'
    labelProgrammeEndDate = 'div[data-cy="label-Programme End Date"]'
    labelFrequencyOfPayment = 'div[data-cy="label-Frequency of Payment"]'
    selectFilter = 'div[data-cy="select-filter"]'
    datePickerFilterFrom = 'div[data-cy="date-picker-filter-From"]'
    datePickerFilterTo = 'div[data-cy="date-picker-filter-To"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    tableLabel = 'span[data-cy="table-label"]'
    tableRow = 'tr[data-cy="table-row"]'
    tablePagination = 'div[data-cy="table-pagination"]'

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonCreatePaymentPlan(self) -> WebElement:
        return self.wait_for(self.buttonCreatePaymentPlan)

    def getButtonFinishProgrammeCycle(self) -> WebElement:
        return self.wait_for(self.buttonFinishProgrammeCycle)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getLabelCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelCreatedBy)

    def getLabelStartDate(self) -> WebElement:
        return self.wait_for(self.labelStartDate)

    def getLabelEndDate(self) -> WebElement:
        return self.wait_for(self.labelEndDate)

    def getLabelProgrammeStartDate(self) -> WebElement:
        return self.wait_for(self.labelProgrammeStartDate)

    def getLabelProgrammeEndDate(self) -> WebElement:
        return self.wait_for(self.labelProgrammeEndDate)

    def getLabelFrequencyOfPayment(self) -> WebElement:
        return self.wait_for(self.labelFrequencyOfPayment)

    def getSelectFilter(self) -> WebElement:
        return self.wait_for(self.selectFilter)

    def getDatePickerFilterFrom(self) -> WebElement:
        return self.wait_for(self.datePickerFilterFrom)

    def getDatePickerFilterTo(self) -> WebElement:
        return self.wait_for(self.datePickerFilterTo)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getTableRow(self) -> WebElement:
        return self.wait_for(self.tableRow)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)
