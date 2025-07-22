from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentVerification(BaseComponents):
    # Locators
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    filterSearch = 'div[data-cy="filter-search"]'
    selectFilter = 'div[data-cy="select-filter"]'
    filterStatus = 'div[data-cy="filter-status"]'
    filterFsp = 'div[data-cy="filter-fsp"]'
    filterModality = 'div[data-cy="filter-Modality"]'
    filterStartDate = 'div[data-cy="filter-start-date"]'
    filterEndDate = 'div[data-cy="filter-end-date"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'h6[data-cy="table-title"]'
    unicefid = 'th[data-cy="unicefId"]'
    tableLabel = 'span[data-cy="table-label"]'
    verificationstatus = 'th[data-cy="verificationStatus"]'
    totaldeliveredquantity = 'th[data-cy="totalDeliveredQuantity"]'
    startdate = 'th[data-cy="startDate"]'
    cycleTitleHeader = 'th[data-cy="cycleTitle"]'
    cycleTitle = 'td[data-cy="cycle-title"]'
    updatedat = 'th[data-cy="updatedAt"]'
    cashPlanTableRow = 'tr[data-cy="cash-plan-table-row"]'
    statusContainer = 'div[data-cy="status-container"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    buttonNewPlan = 'button[data-cy="button-new-plan"]'
    tabFullList = 'button[data-cy="tab-full-list"]'
    tabRandomSampling = 'button[data-cy="tab-random-sampling"]'
    selectExcludedadminareasfull = 'div[data-cy="select-excludedAdminAreasFull"]'
    checkboxVerificationChannel = 'div[data-cy="checkbox-verification-channel"]'
    sliderConfidenceInterval = 'span[data-cy="slider-confidence-interval"]'
    sliderMarginOfError = 'span[data-cy="slider-margin-of-error"]'
    inputAdmincheckbox = 'span[data-cy="input-adminCheckbox"]'
    inputAgecheckbox = 'span[data-cy="input-ageCheckbox"]'
    inputSexcheckbox = 'span[data-cy="input-sexCheckbox"]'
    dialogActionsContainer = 'div[data-cy="dialog-actions-container"]'
    buttonCancel = 'button[data-cy="button-cancel"]'
    buttonSubmit = 'button[data-cy="button-submit"]'
    radioRapidpro = 'span[data-cy="radio-rapidpro"]'
    radioXlsx = 'span[data-cy="radio-xlsx"]'
    radioManual = 'span[data-cy="radio-manual"]'
    radioVerificationChannel = 'span[data-cy="radio-{}"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getFilterSearch(self) -> WebElement:
        return self.wait_for(self.filterSearch)

    def getSelectFilter(self) -> WebElement:
        return self.wait_for(self.selectFilter)

    def getFilterStatus(self) -> WebElement:
        return self.wait_for(self.filterStatus)

    def getFilterFsp(self) -> WebElement:
        return self.wait_for(self.filterFsp)

    def getFilterModality(self) -> WebElement:
        return self.wait_for(self.filterModality)

    def getFilterStartDate(self) -> WebElement:
        return self.wait_for(self.filterStartDate)

    def getFilterEndDate(self) -> WebElement:
        return self.wait_for(self.filterEndDate)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getUnicefid(self) -> WebElement:
        return self.wait_for(self.unicefid)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getVerificationstatus(self) -> WebElement:
        return self.wait_for(self.verificationstatus)

    def getTotaldeliveredquantity(self) -> WebElement:
        return self.wait_for(self.totaldeliveredquantity)

    def getStartdate(self) -> WebElement:
        return self.wait_for(self.startdate)

    def getCycleTitleHeader(self) -> WebElement:
        return self.wait_for(self.cycleTitleHeader)

    def getCycleTitle(self) -> WebElement:
        return self.wait_for(self.cycleTitle)

    def getUpdatedat(self) -> WebElement:
        return self.wait_for(self.updatedat)

    def getCashPlanTableRow(self) -> WebElement:
        return self.wait_for(self.cashPlanTableRow)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getButtonNewPlan(self) -> WebElement:
        return self.wait_for(self.buttonNewPlan)

    def getTabFullList(self) -> WebElement:
        return self.wait_for(self.tabFullList)

    def getTabRandomSampling(self) -> WebElement:
        return self.wait_for(self.tabRandomSampling)

    def getSelectExcludedadminareasfull(self) -> WebElement:
        return self.wait_for(self.selectExcludedadminareasfull)

    def getCheckboxVerificationChannel(self) -> WebElement:
        return self.wait_for(self.checkboxVerificationChannel)

    def getRadioRapidpro(self) -> WebElement:
        return self.wait_for(self.radioRapidpro)

    def getRadioXlsx(self) -> WebElement:
        return self.wait_for(self.radioXlsx)

    def getRadioManual(self) -> WebElement:
        return self.wait_for(self.radioManual)

    def getRadioVerificationChannel(self, name: str) -> WebElement:
        return self.wait_for(self.radioVerificationChannel.format(name))

    def getSliderConfidenceInterval(self) -> WebElement:
        return self.wait_for(self.sliderConfidenceInterval)

    def getSliderMarginOfError(self) -> WebElement:
        return self.wait_for(self.sliderMarginOfError)

    def getInputAdmincheckbox(self) -> WebElement:
        return self.wait_for(self.inputAdmincheckbox)

    def getInputAgecheckbox(self) -> WebElement:
        return self.wait_for(self.inputAgecheckbox)

    def getInputSexcheckbox(self) -> WebElement:
        return self.wait_for(self.inputSexcheckbox)

    def getDialogActionsContainer(self) -> WebElement:
        return self.wait_for(self.dialogActionsContainer)

    def getButtonCancel(self) -> WebElement:
        return self.wait_for(self.buttonCancel)

    def getButtonSubmit(self) -> WebElement:
        return self.wait_for(self.buttonSubmit)
