from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PeriodicDatUpdateTemplates(BaseComponents):
    navProgramPopulation = 'a[data-cy="nav-Programme Population"]'
    navProgramDetails = 'a[data-cy="nav-Programme Details"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    tabIndividuals = 'button[data-cy="tab-individuals"]'
    tabPeriodicDataUpdates = 'button[data-cy="tab-periodic-data-updates"]'
    title = 'h6[data-cy="title"]'
    newTemplateButton = 'a[data-cy="new-template-button"]'
    buttonImport = 'button[data-cy="button-import"]'
    pduTemplatesBtn = 'button[data-cy="pdu-templates"]'
    pduUpdatesBtn = 'button[data-cy="pdu-updates"]'
    headCellTemplateId = 'th[data-cy="head-cell-template-id"]'
    tableLabel = 'span[data-cy="table-label"]'
    headCellNumberOfRecords = 'th[data-cy="head-cell-number-of-records"]'
    headCellCreatedAt = 'th[data-cy="head-cell-created-at"]'
    headCellCreatedBy = 'th[data-cy="head-cell-created-by"]'
    headCellDetails = 'th[data-cy="head-cell-details"]'
    headCellStatus = 'th[data-cy="head-cell-status"]'
    headCellEmpty = 'th[data-cy="head-cell-empty"]'
    templateRow = 'tr[data-cy="template-row-{}"]'
    templateId = 'td[data-cy="template-id-{}"]'
    templateRecords = 'td[data-cy="template-records-{}"]'
    templateCreatedAt = 'td[data-cy="template-created-at-{}"]'
    templateCreatedBy = 'td[data-cy="template-created-by-{}"]'
    templateDetailsBtn = 'td[data-cy="template-details-btn-{}"]'
    templateStatus = 'td[data-cy="template-status-{}"]'
    statusContainer = 'div[data-cy="status-container"]'
    templateAction = 'td[data-cy="template-action-{}"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    # details
    detailModal = 'div[data-cy="periodic-data-update-detail"]'
    templateField = 'td[data-cy="template-field-{}"]'
    templateRoundNumber = 'td[data-cy="template-round-number-{}"]'
    templateRoundName = 'td[data-cy="template-round-name-{}"]'
    templateNumberOfIndividuals = 'td[data-cy="template-number-of-individuals-{}"]'

    def getNavProgramPopulation(self) -> WebElement:
        return self.wait_for(self.navProgramPopulation)

    def getNavProgramDetails(self) -> WebElement:
        return self.wait_for(self.navProgramDetails)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getTabIndividuals(self) -> WebElement:
        return self.wait_for(self.tabIndividuals)

    def getTabPeriodicDataUpdates(self) -> WebElement:
        return self.wait_for(self.tabPeriodicDataUpdates)

    def getTitle(self) -> WebElement:
        return self.wait_for(self.title)

    def getNewTemplateButton(self) -> WebElement:
        return self.wait_for(self.newTemplateButton)

    def getButtonImport(self) -> WebElement:
        return self.wait_for(self.buttonImport)

    def getPduTemplatesBtn(self) -> WebElement:
        return self.wait_for(self.pduTemplatesBtn)

    def getPduUpdatesBtn(self) -> WebElement:
        return self.wait_for(self.pduUpdatesBtn)

    def getHeadCellTemplateId(self) -> WebElement:
        return self.wait_for(self.headCellTemplateId)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getHeadCellNumberOfRecords(self) -> WebElement:
        return self.wait_for(self.headCellNumberOfRecords)

    def getHeadCellCreatedAt(self) -> WebElement:
        return self.wait_for(self.headCellCreatedAt)

    def getHeadCellCreatedBy(self) -> WebElement:
        return self.wait_for(self.headCellCreatedBy)

    def getHeadCellDetails(self) -> WebElement:
        return self.wait_for(self.headCellDetails)

    def getHeadCellStatus(self) -> WebElement:
        return self.wait_for(self.headCellStatus)

    def getHeadCellEmpty(self) -> WebElement:
        return self.wait_for(self.headCellEmpty)

    def getTemplateRow(self) -> WebElement:
        return self.wait_for(self.templateRow)

    def getTemplateId(self, index: int) -> WebElement:
        locator = self.templateId.format(index)
        return self.wait_for(locator)

    def getTemplateRecords(self, index: int) -> WebElement:
        locator = self.templateRecords.format(index)
        return self.wait_for(locator)

    def getTemplateCreatedAt(self, index: int) -> WebElement:
        locator = self.templateCreatedAt.format(index)
        return self.wait_for(locator)

    def getTemplateCreatedBy(self, index: int) -> WebElement:
        locator = self.templateCreatedBy.format(index)
        return self.wait_for(locator)

    def getTemplateDetailsBtn(self, index: int) -> WebElement:
        locator = self.templateDetailsBtn.format(index)
        return self.wait_for(locator)

    def getTemplateStatus(self, index: int) -> WebElement:
        locator = self.templateStatus.format(index)
        return self.wait_for(locator)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)

    def getTemplateAction(self) -> WebElement:
        return self.wait_for(self.templateAction)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getTemplateField(self, index: int) -> WebElement:
        locator = self.templateField.format(index)
        return self.wait_for(locator)

    def getTemplateRoundNumber(self, index: int) -> WebElement:
        locator = self.templateRoundNumber.format(index)
        return self.wait_for(locator)

    def getTemplateRoundName(self, index: int) -> WebElement:
        locator = self.templateRoundName.format(index)
        return self.wait_for(locator)

    def getTemplateNumberOfIndividuals(self, index: int) -> WebElement:
        locator = self.templateNumberOfIndividuals.format(index)
        return self.wait_for(locator)

    def getDetailModal(self) -> WebElement:
        return self.wait_for(self.detailModal)


class PeriodicDatUpdateTemplatesDetails(BaseComponents):
    navProgramPopulation = 'a[data-cy="nav-Programme Population"]'
    navProgramDetails = 'a[data-cy="nav-Programme Details"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    arrow_back = 'div[data-cy="arrow_back"]'
    breadcrumbsContainer = 'div[data-cy="breadcrumbs-container"]'
    breadcrumbsElementContainer = 'span[data-cy="breadcrumbs-element-container"]'
    breadcrumbsLink = 'a[data-cy="breadcrumbs-link"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    title = 'h6[data-cy="title"]'
    labelKey = 'div[data-cy="label-key"]'
    filtersRegistrationDataImport = 'div[data-cy="filters-registration-data-import"]'
    registrationDataImportInput = 'div[data-cy="Registration Data Import-input"]'
    filtersTargetPopulationAutocomplete = 'div[data-cy="filters-target-population-autocomplete"]'
    targetPopulationInput = 'div[data-cy="Target Population-input"]'
    selectFilter = 'div[data-cy="select-filter"]'
    indFiltersGender = 'div[data-cy="ind-filters-gender"]'
    hhFiltersAgeFrom = 'div[data-cy="hh-filters-age-from"]'
    hhFiltersAgeTo = 'div[data-cy="hh-filters-age-to"]'
    indFiltersRegDateFrom = 'div[data-cy="ind-filters-reg-date-from"]'
    indFiltersRegDateTo = 'div[data-cy="ind-filters-reg-date-to"]'
    indFiltersGrievanceTicket = 'div[data-cy="ind-filters-grievance-ticket"]'
    filterAdministrativeArea = 'div[data-cy="filter-administrative-area"]'
    adminLevel1Input = 'div[data-cy="Admin Level 1-input"]'
    adminLevel2Input = 'div[data-cy="Admin Level 2-input"]'
    indFiltersReceivedAssistance = 'div[data-cy="ind-filters-received-assistance"]'
    buttonFiltersClear = 'button[data-cy="button-filters-clear"]'
    buttonFiltersApply = 'button[data-cy="button-filters-apply"]'
    cancelButton = 'a[data-cy="cancel-button"]'
    submitButton = 'button[data-cy="submit-button"]'
    tableContainer = 'div[data-cy="table-container"]'
    table = 'table[data-cy="table"]'
    tableHeaderCheckbox = 'th[data-cy="table-header-checkbox"]'
    tableHeaderField = 'th[data-cy="table-header-field"]'
    tableHeaderRoundnumber = 'th[data-cy="table-header-roundNumber"]'
    tableRow = 'tr[data-cy="table-row-{}"]'
    checkbox = 'span[data-cy="checkbox-{}"]'
    tableCellField = 'td[data-cy="table-cell-field-{}"]'
    tableCellRoundnumber = 'td[data-cy="table-cell-roundNumber-{}"]'
    selectRoundnumber = 'div[data-cy="select-roundNumber-{}"]'
    backButton = 'button[data-cy="back-button"]'

    def getNavProgramPopulation(self) -> WebElement:
        return self.wait_for(self.navProgramPopulation)

    def getNavProgramDetails(self) -> WebElement:
        return self.wait_for(self.navProgramDetails)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getArrow_back(self) -> WebElement:
        return self.wait_for(self.arrow_back)

    def getBreadcrumbsContainer(self) -> WebElement:
        return self.wait_for(self.breadcrumbsContainer)

    def getBreadcrumbsElementContainer(self) -> WebElement:
        return self.wait_for(self.breadcrumbsElementContainer)

    def getBreadcrumbsLink(self) -> WebElement:
        return self.wait_for(self.breadcrumbsLink)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getTitle(self) -> WebElement:
        return self.wait_for(self.title)

    def getLabelKey(self) -> WebElement:
        return self.wait_for(self.labelKey)

    def getFiltersRegistrationDataImport(self) -> WebElement:
        return self.wait_for(self.filtersRegistrationDataImport)

    def getRegistrationDataImportInput(self) -> WebElement:
        return self.wait_for(self.registrationDataImportInput)

    def getFiltersTargetPopulationAutocomplete(self) -> WebElement:
        return self.wait_for(self.filtersTargetPopulationAutocomplete)

    def getTargetPopulationInput(self) -> WebElement:
        return self.wait_for(self.targetPopulationInput)

    def getSelectFilter(self) -> WebElement:
        return self.wait_for(self.selectFilter)

    def getIndFiltersGender(self) -> WebElement:
        return self.wait_for(self.indFiltersGender)

    def getHhFiltersAgeFrom(self) -> WebElement:
        return self.wait_for(self.hhFiltersAgeFrom)

    def getHhFiltersAgeTo(self) -> WebElement:
        return self.wait_for(self.hhFiltersAgeTo)

    def getIndFiltersRegDateFrom(self) -> WebElement:
        return self.wait_for(self.indFiltersRegDateFrom)

    def getIndFiltersRegDateTo(self) -> WebElement:
        return self.wait_for(self.indFiltersRegDateTo)

    def getIndFiltersGrievanceTicket(self) -> WebElement:
        return self.wait_for(self.indFiltersGrievanceTicket)

    def getFilterAdministrativeArea(self) -> WebElement:
        return self.wait_for(self.filterAdministrativeArea)

    def getAdminLevel1Input(self) -> WebElement:
        return self.wait_for(self.adminLevel1Input)

    def getAdminLevel2Input(self) -> WebElement:
        return self.wait_for(self.adminLevel2Input)

    def getIndFiltersReceivedAssistance(self) -> WebElement:
        return self.wait_for(self.indFiltersReceivedAssistance)

    def getButtonFiltersClear(self) -> WebElement:
        return self.wait_for(self.buttonFiltersClear)

    def getButtonFiltersApply(self) -> WebElement:
        return self.wait_for(self.buttonFiltersApply)

    def getCancelButton(self) -> WebElement:
        return self.wait_for(self.cancelButton)

    def getSubmitButton(self) -> WebElement:
        return self.wait_for(self.submitButton)

    def getTableContainer(self) -> WebElement:
        return self.wait_for(self.tableContainer)

    def getTable(self) -> WebElement:
        return self.wait_for(self.table)

    def getTableHeaderCheckbox(self) -> WebElement:
        return self.wait_for(self.tableHeaderCheckbox)

    def getTableHeaderField(self) -> WebElement:
        return self.wait_for(self.tableHeaderField)

    def getTableHeaderRoundnumber(self) -> WebElement:
        return self.wait_for(self.tableHeaderRoundnumber)

    def getTableRow(self, index: str) -> WebElement:
        locator = self.tableRow.format(index)
        return self.wait_for(locator)

    def getCheckbox(self, index: str) -> WebElement:
        locator = self.checkbox.format(index)
        return self.wait_for(locator)

    def getTableCellField(self, index: str) -> WebElement:
        locator = self.tableCellField.format(index)
        return self.wait_for(locator)

    def getTableCellRoundnumber(self, index: str) -> WebElement:
        locator = self.tableCellRoundnumber.format(index)
        return self.wait_for(locator)

    def getSelectRoundnumber(self, index: str) -> WebElement:
        locator = self.selectRoundnumber.format(index)
        return self.wait_for(locator)

    def getBackButton(self) -> WebElement:
        return self.wait_for(self.backButton)
