from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PaymentModuleDetails(BaseComponents):
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    ppUnicefId = 'span[data-cy="pp-unicef-id"]'
    statusContainer = 'div[data-cy="status-container"]'
    buttonExportXlsx = 'button[data-cy="button-export-xlsx"]'
    labelCreatedBy = 'div[data-cy="label-Created By"]'
    labelProgramme = 'div[data-cy="label-Programme"]'
    labelTargetPopulation = 'div[data-cy="label-Target Population"]'
    labelCurrency = 'div[data-cy="label-Currency"]'
    labelStartDate = 'div[data-cy="label-Start Date"]'
    labelEndDate = 'div[data-cy="label-End Date"]'
    labelDispersionStartDate = 'div[data-cy="label-Dispersion Start Date"]'
    labelDispersionEndDate = 'div[data-cy="label-Dispersion End Date"]'
    labelRelatedFollowUpPaymentPlans = 'div[data-cy="label-Related Follow-Up Payment Plans"]'
    buttonSetUpFsp = 'a[data-cy="button-set-up-fsp"]'
    buttonCreateExclusions = 'button[data-cy="button-create-exclusions"]'
    inputExclusionreason = 'textarea[data-cy="input-exclusionReason"]'
    buttonApplyExclusions = 'button[data-cy="button-apply-exclusions"]'
    labelFemaleChildren = 'div[data-cy="label-Female Children"]'
    labelFemaleAdults = 'div[data-cy="label-Female Adults"]'
    labelMaleChildren = 'div[data-cy="label-Male Children"]'
    labelMaleAdults = 'div[data-cy="label-Male Adults"]'
    chartContainer = 'div[data-cy="chart-container"]'
    labelTotalNumberOfHouseholds = 'div[data-cy="label-Total Number of Households"]'
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

    def getLabelCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelCreatedBy)

    def getLabelProgramme(self) -> WebElement:
        return self.wait_for(self.labelProgramme)

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

    def getInputExclusionreason(self) -> WebElement:
        return self.wait_for(self.inputExclusionreason)

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

    def getLabelTargetedIndividuals(self) -> WebElement:
        return self.wait_for(self.labelTargetedIndividuals)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getButtonImport(self) -> WebElement:
        return self.wait_for(self.buttonImport)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

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

