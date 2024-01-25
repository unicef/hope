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
  getPaymentVerificationTitle(self):
        return self.wait_for(self.paymentVerificationTitle)
  getListOfPaymentPlansTitle(self):
        return self.wait_for(self.listOfPaymentPlansTitle)
  getPaymentPlanID(self):
        return self.wait_for(self.paymentPlanID).eq(0)
  getStatus(self):
        return self.wait_for(self.status)
  getFSP(self):
        return self.wait_for(self.FSP)
  getModality(self):
        return self.wait_for(self.modality)
  getStartDate(self):
        return self.wait_for(self.startDate)
  getEndDate(self):
        return self.wait_for(self.endDate)
  getTable(self):
        return self.wait_for(self.tableTitle)
  getPaymentPlanID(self):
        return self.wait_for(self.tableColumn).eq(0)
  getVerificationStatus(self):
        return self.wait_for(self.tableColumn).eq(1)
  getCashAmount(self):
        return self.wait_for(self.tableColumn).eq(2)
  getTimeFrame(self):
        return self.wait_for(self.tableColumn).eq(3)
  getLastModifiedDate(self):
        return self.wait_for(self.tableColumn).eq(4)
  getPaymentPlanRows(self):
        return self.wait_for(self.rows)
  getStatusOption(self):
        return self.wait_for(self.statusOptions)
  getApply(self):
        return self.wait_for(self.buttonApply)

  checkPaymentVerificationTitle() {
    return this.getPaymentVerificationTitle().contains(this.textTitle)
  }

  checkListOfPaymentPlansTitle() {
    return this.getListOfPaymentPlansTitle().contains(this.textTabTitle)
  }

  checkAllSearchFieldsVisible() {
    this.getPaymentPlanID().should("be.visible")
    this.getPaymentPlanID().get("span").contains(this.textPaymentPlanID)
    this.getStatus().should("be.visible")
    this.getStatus().get("span").contains(this.textStatus)
    this.getFSP().should("be.visible")
    this.getFSP().get("span").contains(this.textFSP)
    this.getModality().should("be.visible")
    this.getModality().get("span").contains(this.textModality)
    this.getStartDate().should("be.visible")
    this.getStartDate().get("span").contains(this.textStartDate)
    this.getEndDate().should("be.visible")
    this.getEndDate().get("span").contains(this.textEndDate)
  }

  checkPaymentPlansTableVisible() {
    this.getTable().should("be.visible")
    this.getPaymentPlanID()
      .should("be.visible")
      .contains(this.textPaymentPlanID)
    this.getVerificationStatus()
      .should("be.visible")
      .contains(this.textVerificationStatus)
    this.getCashAmount().should("be.visible").contains(this.textCashAmount)
    this.getTimeFrame().should("be.visible").contains(this.textTimeframe)
    this.getLastModifiedDate()
      .scrollIntoView()
      .should("be.visible")
      .contains(this.textLastModifiedDate)
  }

  countPaymentPlanArray() {
    return Array.from(Array(1).keys())
  }

  choosePaymentPlan(row) {
    return this.getPaymentPlanRows().eq(row)
  }

  selectStatus(status) {
    this.getStatus().click()
    this.getStatusOption().contains(status).click()
    this.pressEscapeFromElement(this.getStatusOption().contains(status))
    this.getApply().click()
  }
}
