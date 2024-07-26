from selenium.webdriver.remote.webelement import WebElement

from page_object.base_components import BaseComponents


class PeriodicDatUpdateTemplates(BaseComponents):
    navProgramPopulation = 'a[data-cy="nav-Program Population"]'
    navHouseholdMembers = 'a[data-cy="nav-Household Members"]'
    navProgramDetails = 'a[data-cy="nav-Program Details"]'
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
    detailModal = 'h2[data-cy="periodic-data-update-detail"]'
    templateField = 'td[data-cy="template-field-{}"]'
    templateRoundNumber = 'td[data-cy="template-round-number-{}"]'
    templateRoundName = 'td[data-cy="template-round-name-{}"]'
    templateNumberOfIndividuals = 'td[data-cy="template-number-of-individuals-{}"]'

    def getNavProgramPopulation(self) -> WebElement:
        return self.wait_for(self.navProgramPopulation)

    def getNavHouseholdMembers(self) -> WebElement:
        return self.wait_for(self.navHouseholdMembers)

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
