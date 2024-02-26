from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PVDetailsPage(BaseComponents):
    # Locators
    paymentVerificationTitle = 'h5[data-cy="page-header-title"]'
    createVerificationPlan = 'button[data-cy="button-new-plan"]'
    divPaymentDetails = 'div[data-cy="div-payment-plan-details"]'
    gridPaymentDetails = 'div[data-cy="grid-payment-plan-details"]'
    divBankReconciliation = 'div[data-cy="grid-bank-reconciliation"]'
    divVerificationPlansSummary = 'div[data-cy="grid-verification-plans-summary"]'
    tableTitle = 'h6[data-cy="table-label"]'
    gridBankReconciliation = 'div[data-cy="grid-bank-reconciliation"]'
    summaryStatus = 'div[data-cy="verification-plans-summary-status"]'
    statusVP = 'div[data-cy="verification-plan-status"]'
    summaryActivationDate = 'div[data-cy="labelized-field-container-summary-activation-date"]'
    summaryCompletionDate = 'div[data-cy="labelized-field-container-summary-completion-date"]'
    summaryNumberOfPlans = 'div[data-cy="labelized-field-container-summary-number-of-plans"]'
    deletePlan = 'button[data-cy="button-delete-plan"]'
    deletePopUP = 'div[data-cy="dialog-actions-container"]'
    activatePlan = 'button[data-cy="button-activate-plan"]'
    discardPlan = 'button[data-cy="button-discard-plan"]'
    finishPlan = 'button[data-cy="button-ed-plan"]'
    editVP = 'button[data-cy="button-new-plan"]'
    # Create Verification Plan
    cvp = 'div[data-cy="dialog-title"]'
    cvpTabList = 'div[data-cy="tabs"]'
    cvpTab = 'button[role="tab"]'
    cvpTitle = 'div[data-cy="dialog-title"]'
    cvpSliderConfidenceInterval = 'span[data-cy="slider-confidence-interval"]'
    cvpInputAdminCheckbox = 'span[data-cy="input-adminCheckbox"]'
    cvpSubmit = 'button[data-cy="button-submit"]'
    labelVERIFICATIONCHANNEL = 'div[data-cy="label-VERIFICATION CHANNEL"]'

    # Texts
    textTitle = "Payment Verification"
    textPaymentPlanDetails = "Payment Plan Details"
    textCreateVerificationPlan = "CREATE VERIFICATION PLAN"
    textProgrammeName = "PROGRAMME NAME"
    textProgrammeID = "PROGRAMME ID"
    textPaymentRecords = "PAYMENT RECORDS"
    textStartDate = "START DATE"
    textEndDate = "END DATE"
    textBankReconciliation = "Bank reconciliation"
    textSuccessful = "SUCCESSFUL"
    textErroneus = "ERRONEOUS"
    textVerificationPlansSummary = "Verification Plans Summary"
    textSummaryStatus = "Status"
    textSummaryActivationDate = "Activation Date"
    textSummaryCompletionDate = "Completion Date"
    textSummaryNumberOfPlans = "Number of Verification Plans"
    textCVPTitle = "Create Verification Plan"
    textCVPConfidenceInterval = "Confidence Interval"

    # Elements

    def getPaymentVerificationTitle(self) -> WebElement:
        return self.wait_for(self.paymentVerificationTitle)

    def getCreateVerificationPlan(self) -> WebElement:
        return self.wait_for(self.createVerificationPlan)

    def getPaymentPlanDetails(self) -> WebElement:
        return self.wait_for(self.divPaymentDetails)

    def getProgrammeName(self) -> WebElement:
        return self.getPaymentPlanDetails().get(self.gridPaymentDetails)

    def getProgrammeID(self) -> WebElement:
        return self.getPaymentPlanDetails().get(self.gridPaymentDetails)

    def getPaymentRecords(self) -> WebElement:
        return self.getPaymentPlanDetails().get(self.gridPaymentDetails)

    def getStartDate(self) -> WebElement:
        return self.getPaymentPlanDetails().get(self.gridPaymentDetails)

    def getEndDate(self) -> WebElement:
        return self.getPaymentPlanDetails().get(self.gridPaymentDetails)

    def getBankReconciliationTitle(self) -> WebElement:
        return self.wait_for(self.divBankReconciliation).get(self.tableTitle)

    def getSuccessful(self) -> WebElement:
        return self.wait_for(self.divBankReconciliation)

    def getErroneus(self) -> WebElement:
        return self.wait_for(self.divBankReconciliation)

    def getVerificationPlansSummary(self) -> WebElement:
        return self.wait_for(self.divVerificationPlansSummary).get(self.tableTitle)

    def getStatus(self) -> WebElement:
        return self.wait_for(self.summaryStatus)

    def getActivationDate(self) -> WebElement:
        return self.wait_for(self.summaryActivationDate)

    def getCompletionDate(self) -> WebElement:
        return self.wait_for(self.summaryCompletionDate)

    def getNumberOfPlans(self) -> WebElement:
        return self.wait_for(self.summaryNumberOfPlans)

    def getDeletePlan(self) -> WebElement:
        return self.wait_for(self.deletePlan)

    def getDelete(self) -> WebElement:
        return self.wait_for(self.deletePopUP).get(self.cvpSubmit)

    def getActivatePlan(self) -> WebElement:
        return self.wait_for(self.activatePlan)

    def getActivate(self) -> WebElement:
        return self.wait_for(self.cvpSubmit)

    def getDiscardPlan(self) -> WebElement:
        return self.wait_for(self.discardPlan)

    def getDiscard(self) -> WebElement:
        return self.wait_for(self.cvpSubmit)

    def getStatusVP(self) -> WebElement:
        return self.wait_for(self.statusVP)

    def getFinishPlan(self) -> WebElement:
        return self.wait_for(self.finishPlan)

    def getFinish(self) -> WebElement:
        return self.wait_for(self.cvpSubmit)

    def getEditVP(self) -> WebElement:
        return self.wait_for(self.editVP)

    def getMANUAL(self) -> WebElement:
        return self.wait_for("span").filter("MANUAL").eq(1)

    def getXLSX(self) -> WebElement:
        return self.wait_for('input[value="XLSX"]').eq(1)

    def getLabelVERIFICATIONCHANNEL(self) -> WebElement:
        return self.wait_for(self.labelVERIFICATIONCHANNEL)

    # Create Verification Plan

    def getCVPTitle(self) -> WebElement:
        return self.wait_for(self.cvp).get(self.cvpTitle)

    def getFullList(self) -> WebElement:
        return self.wait_for(self.cvp).get(self.cvpTab).eq(0)

    def getRandomSampling(self) -> WebElement:
        return self.wait_for(self.cvp).get(self.cvpTab).eq(1)

    def getCVPConfidenceInterval(self) -> WebElement:
        return self.wait_for(self.cvp).get(self.cvpSliderConfidenceInterval)

    def getCVPSave(self) -> WebElement:
        return self.wait_for(self.cvpSubmit)

    def getCvpInputAdminCheckbox(self) -> WebElement:
        return self.wait_for(self.cvpInputAdminCheckbox)

    def checkPaymentVerificationTitle(self) -> None:
        self.getPaymentVerificationTitle().should("be.visible")
        self.getCreateVerificationPlan()

    def checkGridPaymentDetails(self) -> None:
        self.getProgrammeName().get("span").contains(self.textProgrammeName)
        self.getProgrammeID().get("span").contains(self.textProgrammeName)
        self.getPaymentRecords().get("span").contains(self.textProgrammeName)
        self.getStartDate().get("span").contains(self.textProgrammeName)
        self.getEndDate().get("span").contains(self.textProgrammeName)

    def checkBankReconciliationTitle(self) -> None:
        self.getBankReconciliationTitle().contains(self.textBankReconciliation)

    def checkGridBankReconciliation(self) -> None:
        self.getSuccessful().contains(self.textSuccessful)
        self.getErroneus().contains(self.textErroneus)

    def checkVerificationPlansSummaryTitle(self) -> None:
        self.getVerificationPlansSummary().contains(self.textVerificationPlansSummary)

    def checkGridVerificationPlansSummary(self) -> None:
        self.getStatus().get("span").contains(self.textSummaryStatus)
        self.getActivationDate().contains(self.textSummaryActivationDate)
        self.getCompletionDate().contains(self.textSummaryCompletionDate)
        self.getNumberOfPlans().contains(self.textSummaryNumberOfPlans)

    def checkCVPTitle(self) -> None:
        self.getCVPTitle().contains(self.textCVPTitle)

    def checkVerificationPlan(self) -> None:
        self.checkVerificationPlansSummaryTitle()

    def deleteVerificationPlan(self, num: int = 0) -> None:
        self.getDeletePlan().scrollIntoView().should("be.visible")
        self.getDeletePlan().click()
        self.getDelete().should("be.visible")
        self.getDelete().click()
        self.getDelete().should("not.exist")
        self.getActivationDate().find("div").contains("-")
        self.getNumberOfPlans().contains(num)

    def discardVerificationPlan(self, num: int = 0) -> None:
        self.getDiscardPlan().eq(num).scrollIntoView().click()
        self.getDiscard().scrollIntoView().click()
        self.getDiscard().should("not.exist")
        self.getDiscardPlan().should("not.exist")
        self.getDeletePlan().scrollIntoView()
