from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.page_object.base_components import BaseComponents


class PaymentVerificationDetails(BaseComponents):
    # Locators
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonNewPlan = 'button[data-cy="button-new-plan"]'
    buttonEditPlan = 'button[data-cy="button-edit-plan"]'
    divPaymentPlanDetails = 'div[data-cy="div-payment-plan-details"]'
    gridPaymentPlanDetails = 'div[data-cy="grid-payment-plan-details"]'
    labelProgrammeName = 'div[data-cy="label-PROGRAMME NAME"]'
    labelPaymentRecords = 'div[data-cy="label-PAYMENT RECORDS"]'
    labelStartDate = 'div[data-cy="label-START DATE"]'
    labelEndDate = 'div[data-cy="label-END DATE"]'
    gridBankReconciliation = 'div[data-cy="grid-bank-reconciliation"]'
    tableLabel = 'h6[data-cy="table-label"]'
    labelSuccessful = 'div[data-cy="label-SUCCESSFUL"]'
    labelErroneous = 'div[data-cy="label-ERRONEOUS"]'
    gridVerificationPlansSummary = 'div[data-cy="grid-verification-plans-summary"]'
    labelStatus = 'div[data-cy="label-Status"]'
    verificationPlansSummaryStatus = 'div[data-cy="verification-plans-summary-status"]'
    labelizedFieldContainerSummaryActivationDate = 'div[data-cy="labelized-field-container-summary-activation-date"]'
    labelActivationDate = 'div[data-cy="label-Activation Date"]'
    labelizedFieldContainerSummaryCompletionDate = 'div[data-cy="labelized-field-container-summary-completion-date"]'
    labelCompletionDate = 'div[data-cy="label-Completion Date"]'
    labelizedFieldContainerSummaryNumberOfPlans = 'div[data-cy="labelized-field-container-summary-number-of-plans"]'
    labelNumberOfVerificationPlans = 'div[data-cy="label-Number of Verification Plans"]'
    buttonDeletePlan = 'button[data-cy="button-delete-plan"]'
    buttonActivatePlan = 'button[data-cy="button-activate-plan"]'
    verificationPlanStatus = 'div[data-cy="verification-plan-status"]'
    labelSampling = 'div[data-cy="label-SAMPLING"]'
    labelResponded = 'div[data-cy="label-RESPONDED"]'
    labelReceivedWithIssues = 'div[data-cy="label-RECEIVED WITH ISSUES"]'
    labelVerificationChannel = 'div[data-cy="label-VERIFICATION CHANNEL"]'
    labelSampleSize = 'div[data-cy="label-SAMPLE SIZE"]'
    labelReceived = 'div[data-cy="label-RECEIVED"]'
    labelNotReceived = 'div[data-cy="label-NOT RECEIVED"]'
    labelStatusDiv = 'div[data-cy="label-STATUS"]'
    labelActivationDateDiv = 'div[data-cy="label-ACTIVATION DATE"]'
    labelCompletionDateDiv = 'div[data-cy="label-COMPLETION DATE"]'
    buttonSubmit = 'button[data-cy="button-submit"]'
    buttonFinish = 'button[data-cy="button-ed-plan"]'
    rows = 'tr[role="checkbox"]'

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonNewPlan(self) -> WebElement:
        return self.wait_for(self.buttonNewPlan)

    def getButtonEditPlan(self) -> WebElement:
        return self.wait_for(self.buttonEditPlan)

    def getDivPaymentPlanDetails(self) -> WebElement:
        return self.wait_for(self.divPaymentPlanDetails)

    def getGridPaymentPlanDetails(self) -> WebElement:
        return self.wait_for(self.gridPaymentPlanDetails)

    def getLabelProgrammeName(self) -> WebElement:
        return self.wait_for(self.labelProgrammeName)

    def getLabelPaymentRecords(self) -> WebElement:
        return self.wait_for(self.labelPaymentRecords)

    def getLabelStartDate(self) -> WebElement:
        return self.wait_for(self.labelStartDate)

    def getLabelEndDate(self) -> WebElement:
        return self.wait_for(self.labelEndDate)

    def getGridBankReconciliation(self) -> WebElement:
        return self.wait_for(self.gridBankReconciliation)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getLabelSuccessful(self) -> WebElement:
        return self.wait_for(self.labelSuccessful)

    def getLabelErroneous(self) -> WebElement:
        return self.wait_for(self.labelErroneous)

    def getGridVerificationPlansSummary(self) -> WebElement:
        return self.wait_for(self.gridVerificationPlansSummary)

    def getLabelStatus(self) -> WebElement:
        return self.wait_for(self.labelStatus)

    def getVerificationPlansSummaryStatus(self) -> WebElement:
        return self.wait_for(self.verificationPlansSummaryStatus)

    def getLabelizedFieldContainerSummaryActivationDate(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerSummaryActivationDate)

    def getLabelActivationDate(self) -> WebElement:
        return self.wait_for(self.labelActivationDate)

    def getLabelizedFieldContainerSummaryCompletionDate(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerSummaryCompletionDate)

    def getLabelCompletionDate(self) -> WebElement:
        return self.wait_for(self.labelCompletionDate)

    def getLabelizedFieldContainerSummaryNumberOfPlans(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerSummaryNumberOfPlans)

    def getLabelNumberOfVerificationPlans(self) -> WebElement:
        return self.wait_for(self.labelNumberOfVerificationPlans)

    def getButtonDeletePlan(self) -> WebElement:
        return self.wait_for(self.buttonDeletePlan)

    def getButtonActivatePlan(self) -> WebElement:
        return self.wait_for(self.buttonActivatePlan)

    def getVerificationPlanStatus(self) -> WebElement:
        return self.wait_for(self.verificationPlanStatus)

    def getLabelSampling(self) -> WebElement:
        return self.wait_for(self.labelSampling)

    def getLabelResponded(self) -> WebElement:
        return self.wait_for(self.labelResponded)

    def getLabelReceivedWithIssues(self) -> WebElement:
        return self.wait_for(self.labelReceivedWithIssues)

    def getLabelVerificationChannel(self) -> WebElement:
        return self.wait_for(self.labelVerificationChannel)

    def getLabelSampleSize(self) -> WebElement:
        return self.wait_for(self.labelSampleSize)

    def getLabelReceived(self) -> WebElement:
        return self.wait_for(self.labelReceived)

    def getLabelNotReceived(self) -> WebElement:
        return self.wait_for(self.labelNotReceived)

    def getLabelActivationDateDiv(self) -> WebElement:
        return self.wait_for(self.labelActivationDateDiv)

    def getLabelCompletionDateDiv(self) -> WebElement:
        return self.wait_for(self.labelCompletionDateDiv)

    def getLabelStatusDiv(self) -> WebElement:
        return self.wait_for(self.labelStatusDiv)

    def getButtonSubmit(self) -> WebElement:
        return self.wait_for(self.buttonSubmit)

    def getButtonFinish(self) -> WebElement:
        return self.wait_for(self.buttonFinish)

    def getRows(self) -> [WebElement]:
        self.wait_for(self.rows)
        return self.get_elements(self.rows)
