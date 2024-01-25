from page_object.base_components import BaseComponents


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
    def getPaymentVerificationTitle(self):
        return self.wait_for(self.paymentVerificationTitle)

    def getListOfPaymentPlansTitle(self):
        return self.wait_for(self.listOfPaymentPlansTitle)

    def getPaymentPlanID(self):
        return self.wait_for(self.paymentPlanID).eq(0)

    def getStatus(self):
        return self.wait_for(self.status)

    def getFSP(self):
        return self.wait_for(self.FSP)

    def getModality(self):
        return self.wait_for(self.modality)

    def getStartDate(self):
        return self.wait_for(self.startDate)

    def getEndDate(self):
        return self.wait_for(self.endDate)

    def getTable(self):
        return self.wait_for(self.tableTitle)

    def getPaymentPlanID(self):
        return self.wait_for(self.tableColumn).eq(0)

    def getVerificationStatus(self):
        return self.wait_for(self.tableColumn).eq(1)

    def getCashAmount(self):
        return self.wait_for(self.tableColumn).eq(2)

    def getTimeFrame(self):
        return self.wait_for(self.tableColumn).eq(3)

    def getLastModifiedDate(self):
        return self.wait_for(self.tableColumn).eq(4)

    def getPaymentPlanRows(self):
        return self.wait_for(self.rows)

    def getStatusOption(self):
        return self.wait_for(self.statusOptions)

    def getApply(self):
        return self.wait_for(self.buttonApply)

    def checkPaymentVerificationTitle(self):
        return self.getPaymentVerificationTitle().contains(self.textTitle)

    def checkListOfPaymentPlansTitle(self):
        return self.getListOfPaymentPlansTitle().contains(self.textTabTitle)

    def checkAllSearchFieldsVisible(self):
        self.getPaymentPlanID().should("be.visible")
        self.getPaymentPlanID().get("span").contains(self.textPaymentPlanID)
        self.getStatus().should("be.visible")
        self.getStatus().get("span").contains(self.textStatus)
        self.getFSP().should("be.visible")
        self.getFSP().get("span").contains(self.textFSP)
        self.getModality().should("be.visible")
        self.getModality().get("span").contains(self.textModality)
        self.getStartDate().should("be.visible")
        self.getStartDate().get("span").contains(self.textStartDate)
        self.getEndDate().should("be.visible")
        self.getEndDate().get("span").contains(self.textEndDate)

    def checkPaymentPlansTableVisible(self):
        self.getTable().should("be.visible")
        self.getPaymentPlanID()
        self.getVerificationStatus()
        self.getCashAmount().should("be.visible").contains(self.textCashAmount)
        self.getTimeFrame().should("be.visible").contains(self.textTimeframe)
        self.getLastModifiedDate()

    def countPaymentPlanArray(self):
        return  # Array.from(Array(1).keys())

    def choosePaymentPlan(self, row):
        return self.getPaymentPlanRows().eq(row)

    def selectStatus(self, status):
        self.getStatus().click()
        self.getStatusOption().contains(status).click()
        self.pressEscapeFromElement(self.getStatusOption().contains(status))
        self.getApply().click()
