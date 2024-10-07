from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.page_object.base_components import BaseComponents


class ProgramCycleDetailsPage(BaseComponents):
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonCreatePaymentPlan = 'a[data-cy="button-create-payment-plan"]'
    buttonFinishProgrammeCycle = 'button[data-cy="button-finish-programme-cycle"]'
    buttonReactivateProgrammeCycle = 'button[data-cy="button-reactivate-programme-cycle"]'
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

    def getButtonReactivateProgrammeCycle(self) -> WebElement:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        from time import sleep

        sleep(2)
        return self.wait_for(self.buttonReactivateProgrammeCycle)

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
