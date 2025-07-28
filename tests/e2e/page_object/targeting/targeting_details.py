from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class TargetingDetails(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    status = 'div[data-cy="target-population-status"]'
    criteria_container = 'div[data-cy="criteria-container"]'
    lock_button = 'button[data-cy="button-target-population-lock"]'
    lockPopupButton = 'button[data-cy="button-target-population-modal-lock"]'
    household_table_cell = "table tr:nth-of-type({}) td:nth-of-type({})"
    household_table_rows = '[data-cy="target-population-household-row"]'
    people_table_rows = '[data-cy="target-population-people-row"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonTargetPopulationDuplicate = 'button[data-cy="button-target-population-duplicate"]'
    inputName = 'input[data-cy="input-name"]'
    buttonDelete = 'button[data-cy="button-delete"]'
    buttonEdit = 'a[data-cy="button-edit"]'
    buttonSave = 'button[data-cy="button-save"]'
    buttonIconEdit = 'button[data-cy="button-edit"]'
    buttonRebuild = 'button[data-cy="button-rebuild"]'
    buttonTargetPopulationLock = 'button[data-cy="button-target-population-lock"]'
    detailsTitle = 'div[data-cy="details-title"]'
    detailsGrid = 'div[data-cy="details-grid"]'
    labelStatus = 'div[data-cy="label-Status"]'
    buttonMarkReady = 'button[data-cy="button-target-population-send-to-hope"]'
    buttonPopupMarkReady = 'button[data-cy="button-target-population-modal-send-to-hope"]'
    targetPopulationStatus = 'div[data-cy="target-population-status"]'
    labelizedFieldContainerCreatedBy = 'div[data-cy="labelized-field-container-created-by"]'
    labelCreatedBy = 'div[data-cy="label-created by"]'
    labelizedFieldContainerCloseDate = 'div[data-cy="labelized-field-container-close-date"]'
    labelProgrammePopulationCloseDate = 'div[data-cy="label-Programme population close date"]'
    labelizedFieldContainerProgramName = 'div[data-cy="labelized-field-container-program-name"]'
    labelProgramme = 'div[data-cy="label-Programme"]'
    labelizedFieldContainerSendBy = 'div[data-cy="labelized-field-container-send-by"]'
    labelSendBy = 'div[data-cy="label-Send by"]'
    labelizedFieldContainerSendDate = 'div[data-cy="labelized-field-container-send-date"]'
    labelSendDate = 'div[data-cy="label-Send date"]'
    criteriaContainer = 'div[data-cy="criteria-container"]'
    checkboxExcludeIfActiveAdjudicationTicket = 'span[data-cy="checkbox-exclude-if-active-adjudication-ticket"]'
    checkboxExcludePeopleIfActiveAdjudicationTicket = (
        'span[data-cy="checkbox-exclude-people-if-active-adjudication-ticket"]'
    )
    checkboxExcludeIfOnSanctionList = 'span[data-cy="checkbox-exclude-if-on-sanction-list"]'
    iconSelected = '[data-testid="CheckBoxIcon"]'
    labelFemaleChildren = 'div[data-cy="label-Female Children"]'
    labelFemaleAdults = 'div[data-cy="label-Female Adults"]'
    labelMaleChildren = 'div[data-cy="label-Male Children"]'
    labelMaleAdults = 'div[data-cy="label-Male Adults"]'
    labelTotalNumberOfHouseholds = 'div[data-cy="label-Total Number of Items Groups"]'
    labelTargetedIndividuals = 'div[data-cy="label-Targeted Items"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableLabel = 'span[data-cy="table-label"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    statusContainer = 'div[data-cy="status-container"]'
    householdSizeFrom = 'input[data-cy="input-householdsFiltersBlocks[0].value.from"]'
    householdSizeTo = 'input[data-cy="input-householdsFiltersBlocks[0].value.to"]'
    dialogBox = 'div[role="dialog"]'
    buttonTargetPopulationAddCriteria = 'div[data-cy="button-target-population-add-criteria"]'

    # Texts
    # Elements

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def waitForTextTitlePage(self, text: str) -> bool:
        return self.wait_for_text(text, self.titlePage)

    def getButtonTargetPopulationDuplicate(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationDuplicate)

    def getInputName(self) -> WebElement:
        return self.wait_for(self.inputName)

    def disappearInputName(self) -> WebElement:
        return self.wait_for_disappear(self.inputName)

    def getButtonDelete(self) -> WebElement:
        return self.wait_for(self.buttonDelete)

    def getButtonEdit(self) -> WebElement:
        return self.wait_for(self.buttonEdit)

    def getButtonSave(self) -> WebElement:
        return self.wait_for(self.buttonSave)

    def getButtonIconEdit(self) -> WebElement:
        return self.wait_for(self.buttonIconEdit)

    def getButtonRebuild(self) -> WebElement:
        return self.wait_for(self.buttonRebuild)

    def getButtonTargetPopulationLock(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationLock)

    def getDetailsTitle(self) -> WebElement:
        return self.wait_for(self.detailsTitle)

    def getDetailsGrid(self) -> WebElement:
        return self.wait_for(self.detailsGrid)

    def getLabelStatus(self) -> WebElement:
        return self.wait_for(self.labelStatus)

    def waitForLabelStatus(self, status: str) -> WebElement:
        for _ in range(20):
            sleep(1)
            if status.upper() in self.getLabelStatus().text:
                return self.wait_for(self.labelStatus)
        else:
            raise Exception(f"Status: {status.capitalize()} does not occur.")

    def getTargetPopulationStatus(self) -> WebElement:
        return self.wait_for(self.targetPopulationStatus)

    def getButtonMarkReady(self) -> WebElement:
        return self.wait_for(self.buttonMarkReady)

    def getButtonPopupMarkReady(self) -> WebElement:
        return self.wait_for(self.buttonPopupMarkReady)

    def getLabelizedFieldContainerCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerCreatedBy)

    def getLabelCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelCreatedBy)

    def getLabelizedFieldContainerCloseDate(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerCloseDate)

    def getLabelProgrammePopulationCloseDate(self) -> WebElement:
        return self.wait_for(self.labelProgrammePopulationCloseDate)

    def getLabelizedFieldContainerProgramName(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerProgramName)

    def getLabelProgramme(self) -> WebElement:
        return self.wait_for(self.labelProgramme)

    def getLabelizedFieldContainerSendBy(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerSendBy)

    def getLabelSendBy(self) -> WebElement:
        return self.wait_for(self.labelSendBy)

    def getLabelizedFieldContainerSendDate(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerSendDate)

    def getLabelSendDate(self) -> WebElement:
        return self.wait_for(self.labelSendDate)

    def getCriteriaContainer(self) -> WebElement:
        return self.wait_for(self.criteriaContainer)

    def getCheckboxExcludeIfActiveAdjudicationTicket(self) -> WebElement:
        return self.get(self.checkboxExcludeIfActiveAdjudicationTicket)

    def getCheckboxExcludePeopleIfActiveAdjudicationTicket(self) -> WebElement:
        return self.get(self.checkboxExcludePeopleIfActiveAdjudicationTicket)

    def getCheckboxExcludeIfOnSanctionList(self) -> WebElement:
        return self.wait_for(self.checkboxExcludeIfOnSanctionList)

    def getIconSelected(self) -> WebElement:
        return self.wait_for(self.iconSelected)

    def getLabelFemaleChildren(self) -> WebElement:
        return self.wait_for(self.labelFemaleChildren)

    def getLabelFemaleAdults(self) -> WebElement:
        return self.wait_for(self.labelFemaleAdults)

    def getLabelMaleChildren(self) -> WebElement:
        return self.wait_for(self.labelMaleChildren)

    def getLabelMaleAdults(self) -> WebElement:
        return self.wait_for(self.labelMaleAdults)

    def getLabelTotalNumberOfHouseholds(self) -> WebElement:
        return self.wait_for(self.labelTotalNumberOfHouseholds)

    def getLabelTargetedIndividuals(self) -> WebElement:
        return self.wait_for(self.labelTargetedIndividuals)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getTableLabel(self) -> [WebElement]:
        return self.get_elements(self.tableLabel)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getTitlePage(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getStatus(self) -> WebElement:
        return self.wait_for(self.status)

    def getLockButton(self) -> WebElement:
        return self.wait_for(self.lock_button)

    def getLockPopupButton(self) -> WebElement:
        return self.wait_for(self.lockPopupButton)

    def getHouseholdTableCell(self, row: int, column: int) -> WebElement:
        return self.wait_for(self.household_table_cell.format(row, column))

    def getPeopleTableRows(self) -> list[WebElement]:
        return self.get_elements(self.people_table_rows)

    def getHouseholdTableRows(self) -> list[WebElement]:
        return self.get_elements(self.household_table_rows)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def disappearStatusContainer(self) -> bool:
        return self.wait_for_disappear(self.statusContainer)

    def getHouseholdSizeFrom(self) -> WebElement:
        return self.wait_for(self.householdSizeFrom)

    def getHouseholdSizeTo(self) -> WebElement:
        return self.wait_for(self.householdSizeTo)

    def getDialogBox(self) -> WebElement:
        return self.wait_for(self.dialogBox)

    def getButtonTargetPopulationAddCriteria(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationAddCriteria)
