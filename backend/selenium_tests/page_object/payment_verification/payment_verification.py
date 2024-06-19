from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentVerification(BaseComponents):
    # Locators
    paymentVerificationTitle = "h5[data-cy='page-header-title']"
    paymentPlanID = 'div[data-cy="filter-search"]'
    status = 'div[data-cy="filter-status"]'
    FSP = 'div[data-cy="filter-fsp"]'
    modality = 'div[data-cy="filter-Modality"]'
    startDate = 'div[data-cy="filter-start-date"]'
    endDate = 'div[data-cy="filter-end-date"]'
    statusOptions = 'li[role="option"]'
    listOfPaymentPlansTitle = 'h6[data-cy="table-title"]'
    buttonApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'table[data-cy="table-title"]'
    tableColumn = 'span[data-cy="table-label"]'
    rows = 'tr[data-cy="cash-plan-table-row"]'

    # Texts
    textTitle = "Payment Verification"
    textTabTitle = "List of Payment Plans"
    textPaymentPlanID = "Payment Plan ID"
    textStatus = "Status"
    textFSP = "FSP"
    textModality = "Delivery Mechanism"
    textStartDate = "Start Date"
    textEndDate = "End Date"
    textProgramme = "Programme"
    textPaymentPlanID = "Payment Plan ID"
    textVerificationStatus = "Verification Status"
    textCashAmount = "Cash Amount"
    textTimeframe = "Timeframe"
    textLastModifiedDate = "Last Modified Date"

    # Elements
    def getPaymentVerificationTitle(self) -> WebElement:
        return self.wait_for(self.paymentVerificationTitle)

    def getListOfPaymentPlansTitle(self) -> WebElement:
        return self.wait_for(self.listOfPaymentPlansTitle)

    def getPaymentPlanID(self) -> WebElement:
        return self.wait_for(self.paymentPlanID).eq(0)

    def getStatus(self) -> WebElement:
        return self.wait_for(self.status)

    def getFSP(self) -> WebElement:
        return self.wait_for(self.FSP)

    def getModality(self) -> WebElement:
        return self.wait_for(self.modality)

    def getStartDate(self) -> WebElement:
        return self.wait_for(self.startDate)

    def getEndDate(self) -> WebElement:
        return self.wait_for(self.endDate)

    def getTable(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getVerificationStatus(self) -> WebElement:
        return self.wait_for(self.tableColumn).eq(1)

    def getCashAmount(self) -> WebElement:
        return self.wait_for(self.tableColumn).eq(2)

    def getTimeFrame(self) -> WebElement:
        return self.wait_for(self.tableColumn).eq(3)

    def getLastModifiedDate(self) -> WebElement:
        return self.wait_for(self.tableColumn).eq(4)

    def getPaymentPlanRows(self) -> WebElement:
        return self.wait_for(self.rows)

    def getStatusOption(self) -> WebElement:
        return self.wait_for(self.statusOptions)

    def getApply(self) -> WebElement:
        return self.wait_for(self.buttonApply)
