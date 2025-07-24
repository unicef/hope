from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ProgrammeDetails(BaseComponents):
    headerTitle = 'h5[data-cy="page-header-title"]'
    copyProgram = 'a[data-cy="button-copy-program"]'
    programStatus = 'div[data-cy="status-container"]'
    labelStartDate = 'div[data-cy="label-START DATE"]'
    labelEndDate = 'div[data-cy="label-END DATE"]'
    labelSelector = 'div[data-cy="label-Sector"]'
    labelDataCollectingType = 'div[data-cy="label-Data Collecting Type"]'
    labelFreqOfPayment = 'div[data-cy="label-Frequency of Payment"]'
    labelAdministrativeAreas = 'div[data-cy="label-Administrative Areas of implementation"]'
    labelCashPlus = 'div[data-cy="label-CASH+"]'
    labelProgramSize = 'div[data-cy="label-Programme size"]'
    labelDescription = 'div[data-cy="label-Description"]'
    labelAreaAccess = 'div[data-cy="label-Area Access"]'
    labelAdminArea1 = 'div[data-cy="labelized-field-container-admin-area-1-total-count"]'
    labelAdminArea2 = 'div[data-cy="label-Admin Area 2"]'
    labelPartnerName = 'h6[data-cy="label-partner-name"]'
    labelPartnerAccess = 'div[data-cy="label-Partner Access"]'
    buttonRemoveProgram = 'button[data-cy="button-remove-program"]'
    buttonEditProgram = 'button[data-cy="button-edit-program"]'
    selectEditProgramDetails = 'li[data-cy="menu-item-edit-details"]'
    selectEditProgramPartners = 'li[data-cy="menu-item-edit-partners"]'
    buttonActivateProgram = 'button[data-cy="button-activate-program"]'
    buttonActivateProgramModal = 'button[data-cy="button-activate-program-modal"]'
    labelProgrammeCode = 'div[data-cy="label-Programme Code"]'
    buttonFinishProgram = 'button[data-cy="button-finish-program"]'
    tableTitle = 'h6[data-cy="table-title"]'
    buttonAddNewProgrammeCycle = 'button[data-cy="button-add-new-programme-cycle"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    programCycleRow = 'tr[data-cy="program-cycle-row"]'
    programCycleId = 'td[data-cy="program-cycle-id"]'
    programCycleTitle = 'td[data-cy="program-cycle-title"]'
    programCycleStatus = 'td[data-cy="program-cycle-status"]'
    statusContainer = 'div[data-cy="status-container"]'
    programCycleTotalEntitledQuantityUSD = 'td[data-cy="program-cycle-total-entitled-quantity-usd"]'
    programCycleTotalUndeliveredQuantityUSD = 'td[data-cy="program-cycle-total-undelivered-quantity-usd"]'
    programCycleTotalDeliveredQuantityUSD = 'td[data-cy="program-cycle-total-delivered-quantity-usd"]'
    programCycleStartDate = 'td[data-cy="program-cycle-start-date"]'
    programCycleEndDate = 'td[data-cy="program-cycle-end-date"]'
    programCycleDetailsBtn = 'td[data-cy="program-cycle-details-btn"]'
    buttonEditProgramCycle = 'button[data-cy="button-edit-program-cycle"]'
    startDateCycle = 'div[data-cy="start-date-cycle"]'
    dataPickerFilter = 'div[data-cy="date-picker-filter"]'
    endDateCycle = 'div[data-cy="end-date-cycle"]'
    buttonNext = 'button[data-cy="button-update-program-cycle-modal"]'
    buttonSave = 'button[data-cy="button-save"]'
    buttonCreateProgramCycle = 'button[data-cy="button-create-program-cycle"]'
    inputTitle = 'input[data-cy="input-title"]'
    deleteProgrammeCycle = 'button[data-cy="delete-programme-cycle"]'
    buttonDelete = 'button[data-cy="button-delete"]'
    buttonCancel = 'button[data-cy="button-cancel"]'

    def getProgramCycleRow(self) -> [WebElement]:
        self.wait_for(self.programCycleRow)
        return self.get_elements(self.programCycleRow)

    def getDeleteProgrammeCycle(self) -> [WebElement]:
        self.wait_for(self.deleteProgrammeCycle)
        return self.get_elements(self.deleteProgrammeCycle)

    def getProgramCycleId(self) -> [WebElement]:
        self.wait_for(self.programCycleId)
        return self.get_elements(self.programCycleId)

    def getProgramCycleTitle(self) -> [WebElement]:
        self.wait_for(self.programCycleTitle)
        return self.get_elements(self.programCycleTitle)

    def getProgramCycleStatus(self) -> [WebElement]:
        self.wait_for(self.programCycleStatus)
        return self.get_elements(self.programCycleStatus)

    def getStatusContainer(self) -> [WebElement]:
        self.wait_for(self.statusContainer)
        return self.get_elements(self.statusContainer)

    def getProgramCycleTotalEntitledQuantityUSD(self) -> [WebElement]:
        self.wait_for(self.programCycleTotalEntitledQuantityUSD)
        return self.get_elements(self.programCycleTotalEntitledQuantityUSD)

    def getProgramCycleTotalUndeliveredQuantityUSD(self) -> [WebElement]:
        self.wait_for(self.programCycleTotalUndeliveredQuantityUSD)
        return self.get_elements(self.programCycleTotalUndeliveredQuantityUSD)

    def getProgramCycleTotalDeliveredQuantityUSD(self) -> [WebElement]:
        self.wait_for(self.programCycleTotalDeliveredQuantityUSD)
        return self.get_elements(self.programCycleTotalDeliveredQuantityUSD)

    def getProgramCycleStartDate(self) -> [WebElement]:
        self.wait_for(self.programCycleStartDate)
        return self.get_elements(self.programCycleStartDate)

    def getProgramCycleEndDate(self) -> [WebElement]:
        self.wait_for(self.programCycleEndDate)
        return self.get_elements(self.programCycleEndDate)

    def getProgramCycleDetailsBtn(self) -> [WebElement]:
        self.wait_for(self.programCycleDetailsBtn)
        return self.get_elements(self.programCycleDetailsBtn)

    def getButtonEditProgramCycle(self) -> [WebElement]:
        self.wait_for(self.buttonEditProgramCycle)
        return self.get_elements(self.buttonEditProgramCycle)

    def getDataPickerFilter(self) -> WebElement:
        self.wait_for(self.dataPickerFilter)
        return self.get_elements(self.dataPickerFilter)[0].find_elements("tag name", "input")[0]

    def getButtonNext(self) -> WebElement:
        return self.wait_for(self.buttonNext)

    def getButtonSave(self) -> WebElement:
        return self.wait_for(self.buttonSave)

    def getInputTitle(self) -> WebElement:
        return self.wait_for(self.inputTitle)

    def getStartDateCycle(self) -> WebElement:
        return self.wait_for(self.startDateCycle).find_elements("tag name", "input")[0]

    def getEndDateCycle(self) -> WebElement:
        return self.wait_for(self.endDateCycle).find_elements("tag name", "input")[0]

    def getStartDateCycleDiv(self) -> WebElement:
        return self.wait_for(self.startDateCycle)

    def getEndDateCycleDiv(self) -> WebElement:
        return self.wait_for(self.endDateCycle)

    def getButtonCreateProgramCycle(self) -> WebElement:
        return self.wait_for(self.buttonCreateProgramCycle)

    def getLabelPartnerName(self) -> WebElement:
        return self.wait_for(self.labelPartnerName)

    def getLabelAreaAccess(self) -> WebElement:
        return self.wait_for(self.labelAreaAccess)

    def getLabelPartnerAccess(self) -> WebElement:
        return self.wait_for(self.labelPartnerAccess)

    def getLabelAdminArea1(self) -> WebElement:
        return self.wait_for(self.labelAdminArea1)

    def getLabelAdminArea2(self) -> WebElement:
        return self.wait_for(self.labelAdminArea2)

    def getProgramStatus(self) -> WebElement:
        return self.wait_for(self.programStatus)

    def getHeaderTitle(self) -> WebElement:
        return self.wait_for(self.headerTitle)

    def getLabelStartDate(self) -> WebElement:
        return self.wait_for(self.labelStartDate)

    def getLabelEndDate(self) -> WebElement:
        return self.wait_for(self.labelEndDate)

    def getLabelSelector(self) -> WebElement:
        return self.wait_for(self.labelSelector)

    def getLabelDataCollectingType(self) -> WebElement:
        return self.wait_for(self.labelDataCollectingType)

    def getLabelFreqOfPayment(self) -> WebElement:
        return self.wait_for(self.labelFreqOfPayment)

    def getLabelAdministrativeAreas(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeAreas)

    def getLabelCashPlus(self) -> WebElement:
        return self.wait_for(self.labelCashPlus)

    def getLabelProgramSize(self) -> WebElement:
        return self.wait_for(self.labelProgramSize)

    def getCopyProgram(self) -> WebElement:
        return self.wait_for(self.copyProgram)

    def getLabelDescription(self) -> WebElement:
        return self.wait_for(self.labelDescription)

    def getButtonRemoveProgram(self) -> WebElement:
        return self.wait_for(self.buttonRemoveProgram)

    def getButtonEditProgram(self) -> WebElement:
        return self.wait_for(self.buttonEditProgram)

    def getSelectEditProgramDetails(self) -> WebElement:
        return self.wait_for(self.selectEditProgramDetails)

    def getSselectEditProgramPartners(self) -> WebElement:
        return self.wait_for(self.selectEditProgramPartners)

    def getButtonActivateProgram(self) -> WebElement:
        return self.wait_for(self.buttonActivateProgram)

    def getButtonActivateProgramModal(self) -> WebElement:
        return self.wait_for(self.buttonActivateProgramModal)

    def getLabelProgrammeCode(self) -> WebElement:
        return self.wait_for(self.labelProgrammeCode)

    def getButtonFinishProgram(self) -> WebElement:
        return self.wait_for(self.buttonFinishProgram)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getButtonAddNewProgrammeCycle(self) -> WebElement:
        return self.wait_for(self.buttonAddNewProgrammeCycle)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getButtonDelete(self) -> WebElement:
        return self.wait_for(self.buttonDelete)

    def getButtonCancel(self) -> WebElement:
        return self.wait_for(self.buttonCancel)

    def clickButtonFinishProgramPopup(self) -> None:
        self.wait_for('[data-cy="dialog-actions-container"]')
        self.get_elements(self.buttonFinishProgram)[1].click()
        self.wait_for_disappear('[data-cy="dialog-actions-container"]')
