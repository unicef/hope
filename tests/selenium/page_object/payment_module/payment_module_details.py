from time import sleep

from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.page_object.base_components import BaseComponents


class PaymentModuleDetails(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    ppUnicefId = 'span[data-cy="pp-unicef-id"]'
    statusContainer = 'div[data-cy="status-container"]'
    buttonExportXlsx = 'button[data-cy="button-export-xlsx"]'
    buttonDownloadXlsx = 'a[data-cy="button-download-xlsx"]'
    labelCreatedBy = 'div[data-cy="label-Created By"]'
    labelTargetPopulation = 'div[data-cy="label-Target Population"]'
    labelCurrency = 'div[data-cy="label-Currency"]'
    labelStartDate = 'div[data-cy="label-Start Date"]'
    labelEndDate = 'div[data-cy="label-End Date"]'
    labelDispersionStartDate = 'div[data-cy="label-Dispersion Start Date"]'
    labelDispersionEndDate = 'div[data-cy="label-Dispersion End Date"]'
    labelRelatedFollowUpPaymentPlans = 'div[data-cy="label-Related Follow-Up Payment Plans"]'
    buttonSetUpFsp = 'a[data-cy="button-set-up-fsp"]'
    buttonCreateExclusions = 'button[data-cy="button-create-exclusions"]'
    buttonSaveExclusions = 'button[data-cy="button-save-exclusions"]'
    supportingDocumentsTitle = 'h6[data-cy="supporting-documents-title"]'
    supportingDocumentsEmpty = 'div[data-cy="supporting-documents-empty"]'
    inputExclusion = 'textarea[data-cy="input-exclusion"]'
    inputExclusionReason = 'textarea[data-cy="input-exclusionReason"]'
    inputHouseholdsIds = '[data-cy="input-households-ids"]'
    inputBeneficiariesIds = '[data-cy="input-beneficiaries-ids"]'
    buttonApplyExclusions = 'button[data-cy="button-apply-exclusions"]'
    labelFemaleChildren = 'div[data-cy="label-Female Children"]'
    labelFemaleAdults = 'div[data-cy="label-Female Adults"]'
    labelMaleChildren = 'div[data-cy="label-Male Children"]'
    labelMaleAdults = 'div[data-cy="label-Male Adults"]'
    chartContainer = 'div[data-cy="chart-container"]'
    labelTotalNumberOfHouseholds = 'div[data-cy="label-Total Number of Households"]'
    labelTotalNumberOfPeople = 'div[data-cy="label-Total Number of People"]'
    labelTargetedIndividuals = 'div[data-cy="label-Targeted Individuals"]'
    tableTitle = 'h6[data-cy="table-title"]'
    buttonImport = 'button[data-cy="button-import"]'
    tableLabel = 'span[data-cy="table-label"]'
    tableRow = 'tr[data-cy="table-row"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    labelDeliveredFully = 'div[data-cy="label-Delivered fully"]'
    labelDeliveredPartially = 'div[data-cy="label-Delivered partially"]'
    labelNotDelivered = 'div[data-cy="label-Not delivered"]'
    labelUnsuccessful = 'div[data-cy="label-Unsuccessful"]'
    labelPending = 'div[data-cy="label-Pending"]'
    labelNumberOfPayments = 'div[data-cy="label-Number of payments"]'
    labelReconciled = 'div[data-cy="label-Reconciled"]'
    labelTotalEntitledQuantity = 'div[data-cy="label-Total Entitled Quantity"]'
    buttonLockPlan = 'button[data-cy="button-lock-plan"'
    buttonSubmit = 'button[data-cy="button-submit"]'
    inputEntitlementFormula = 'div[data-cy="input-entitlement-formula"]'
    buttonApplySteficon = 'button[data-cy="button-apply-steficon"]'
    selectDeliveryMechanism = 'div[data-cy="select-deliveryMechanisms[0].deliveryMechanism"]'
    selectDeliveryMechanismsFSP = 'div[data-cy="select-deliveryMechanisms[0].fsp"]'
    buttonNextSave = 'button[data-cy="button-next-save"]'
    buttonSendForApproval = 'button[data-cy="button-send-for-approval"]'
    buttonApprove = 'button[data-cy="button-approve"]'
    buttonAuthorize = 'button[data-cy="button-authorize"]'
    buttonMarkAsReleased = 'button[data-cy="button-mark-as-released"]'
    buttonUploadReconciliationInfo = 'button[data-cy="button-import"]'
    buttonImportSubmit = 'button[data-cy="button-import-submit"]'
    errorsContainer = 'div[data-cy="errors-container"]'
    deleteButton = '[data-cy="button-delete-payment-plan"]'
    uploadFileButton = 'button[data-cy="upload-file-button"]'
    titleInput = 'div[data-cy="title-input"]'

    def getButtonLockPlan(self) -> WebElement:
        return self.wait_for(self.buttonLockPlan)

    def getButtonSubmit(self) -> WebElement:
        return self.wait_for(self.buttonSubmit)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getPpUnicefId(self) -> WebElement:
        return self.wait_for(self.ppUnicefId)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getButtonExportXlsx(self) -> WebElement:
        return self.wait_for(self.buttonExportXlsx)

    def getButtonDownloadXlsx(self) -> WebElement:
        return self.wait_for(self.buttonDownloadXlsx)

    def getButtonUploadReconciliationInfo(self) -> WebElement:
        return self.wait_for(self.buttonUploadReconciliationInfo)

    def getErrorsContainer(self) -> WebElement:
        return self.wait_for(self.errorsContainer)

    def getButtonImportSubmit(self) -> WebElement:
        return self.wait_for(self.buttonImportSubmit)

    def getDeleteButton(self) -> WebElement:
        return self.wait_for(self.deleteButton)

    def getUploadFileButton(self) -> WebElement:
        return self.wait_for(self.uploadFileButton)

    def getTitleInput(self) -> WebElement:
        return self.wait_for(self.titleInput)

    def getLabelCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelCreatedBy)

    def getLabelTargetPopulation(self) -> WebElement:
        return self.wait_for(self.labelTargetPopulation)

    def getLabelCurrency(self) -> WebElement:
        return self.wait_for(self.labelCurrency)

    def getLabelStartDate(self) -> WebElement:
        return self.wait_for(self.labelStartDate)

    def getLabelEndDate(self) -> WebElement:
        return self.wait_for(self.labelEndDate)

    def getLabelDispersionStartDate(self) -> WebElement:
        return self.wait_for(self.labelDispersionStartDate)

    def getLabelDispersionEndDate(self) -> WebElement:
        return self.wait_for(self.labelDispersionEndDate)

    def getLabelRelatedFollowUpPaymentPlans(self) -> WebElement:
        return self.wait_for(self.labelRelatedFollowUpPaymentPlans)

    def getButtonSetUpFsp(self) -> WebElement:
        return self.wait_for(self.buttonSetUpFsp)

    def getButtonCreateExclusions(self) -> WebElement:
        return self.wait_for(self.buttonCreateExclusions)

    def getButtonSaveExclusions(self) -> WebElement:
        return self.wait_for(self.buttonSaveExclusions)

    def getInputHouseholdsIds(self) -> WebElement:
        return self.wait_for(self.inputHouseholdsIds)

    def getInputBeneficiariesIds(self) -> WebElement:
        return self.wait_for(self.inputBeneficiariesIds)

    def getInputExclusionReason(self) -> WebElement:
        return self.wait_for(self.inputExclusionReason)

    def getButtonApplyExclusions(self) -> WebElement:
        return self.wait_for(self.buttonApplyExclusions)

    def getLabelFemaleChildren(self) -> WebElement:
        return self.wait_for(self.labelFemaleChildren)

    def getLabelFemaleAdults(self) -> WebElement:
        return self.wait_for(self.labelFemaleAdults)

    def getLabelMaleChildren(self) -> WebElement:
        return self.wait_for(self.labelMaleChildren)

    def getLabelMaleAdults(self) -> WebElement:
        return self.wait_for(self.labelMaleAdults)

    def getChartContainer(self) -> WebElement:
        return self.wait_for(self.chartContainer)

    def getLabelTotalNumberOfHouseholds(self) -> WebElement:
        return self.wait_for(self.labelTotalNumberOfHouseholds)

    def getLabelTotalNumberOfPeople(self) -> WebElement:
        return self.wait_for(self.labelTotalNumberOfPeople)

    def getLabelTargetedIndividuals(self) -> WebElement:
        return self.wait_for(self.labelTargetedIndividuals)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getButtonImport(self) -> WebElement:
        return self.wait_for(self.buttonImport)

    def getTableLabel(self) -> [WebElement]:
        return self.get_elements(self.tableLabel)

    def getTableRow(self) -> WebElement:
        return self.wait_for(self.tableRow)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getLabelDeliveredFully(self) -> WebElement:
        return self.wait_for(self.labelDeliveredFully)

    def getLabelDeliveredPartially(self) -> WebElement:
        return self.wait_for(self.labelDeliveredPartially)

    def getLabelNotDelivered(self) -> WebElement:
        return self.wait_for(self.labelNotDelivered)

    def getLabelUnsuccessful(self) -> WebElement:
        return self.wait_for(self.labelUnsuccessful)

    def getLabelPending(self) -> WebElement:
        return self.wait_for(self.labelPending)

    def getLabelNumberOfPayments(self) -> WebElement:
        return self.wait_for(self.labelNumberOfPayments)

    def getLabelReconciled(self) -> WebElement:
        return self.wait_for(self.labelReconciled)

    def getLabelTotalEntitledQuantity(self) -> WebElement:
        return self.wait_for(self.labelTotalEntitledQuantity)

    def getInputEntitlementFormula(self) -> WebElement:
        return self.wait_for(self.inputEntitlementFormula)

    def getButtonApplySteficon(self) -> WebElement:
        return self.wait_for(self.buttonApplySteficon)

    def getSelectDeliveryMechanism(self) -> WebElement:
        return self.wait_for(self.selectDeliveryMechanism)

    def getSelectDeliveryMechanismFSP(self) -> WebElement:
        return self.wait_for(self.selectDeliveryMechanismsFSP)

    def getButtonNextSave(self) -> WebElement:
        return self.wait_for(self.buttonNextSave)

    def getButtonSendForApproval(self) -> WebElement:
        return self.wait_for(self.buttonSendForApproval)

    def getButtonApprove(self) -> WebElement:
        return self.wait_for(self.buttonApprove)

    def getButtonAuthorize(self) -> WebElement:
        return self.wait_for(self.buttonAuthorize)

    def getButtonMarkAsReleased(self) -> WebElement:
        return self.wait_for(self.buttonMarkAsReleased)

    def checkStatus(self, status: str) -> None:
        for _ in range(30):
            if status == self.getStatusContainer().text:
                break
            sleep(1)
        assert status in self.getStatusContainer().text

    def getSupportingDocumentsTitle(self) -> WebElement:
        return self.wait_for(self.supportingDocumentsTitle)

    def getSupportingDocumentsEmpty(self) -> WebElement:
        return self.wait_for(self.supportingDocumentsEmpty)
