from e2e.page_object.base_components import BaseComponents
from e2e.webdriver.remote.webelement import WebElement


class PeriodicDataUpdateUploads(BaseComponents):
    navProgramPopulation = 'a[data-cy="nav-Programme Population"]'
    navProgramDetails = 'a[data-cy="nav-Programme Details"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    tabIndividuals = 'button[data-cy="tab-individuals"]'
    tabPeriodicDataUpdates = 'button[data-cy="tab-periodic-data-updates"]'
    title = 'h6[data-cy="title"]'
    newTemplateButton = 'a[data-cy="new-template-button"]'
    buttonImport = 'button[data-cy="button-import"]'
    pduTemplates = 'button[data-cy="pdu-templates"]'
    pduUpdates = 'button[data-cy="pdu-updates"]'
    headCellImportId = 'th[data-cy="head-cell-import-id"]'
    tableLabel = 'span[data-cy="table-label"]'
    headCellTemplateId = 'th[data-cy="head-cell-template-id"]'
    headCellImportDate = 'th[data-cy="head-cell-import-date"]'
    headCellImportedBy = 'th[data-cy="head-cell-imported-by"]'
    headCellDetails = 'th[data-cy="head-cell-details"]'
    headCellStatus = 'th[data-cy="head-cell-status"]'
    updateRow = 'tr[data-cy="update-row-{}"]'
    updateId = 'td[data-cy="update-id-{}"]'
    updateTemplate = 'td[data-cy="update-template-{}"]'
    updateCreatedAt = 'td[data-cy="update-created-at-{}"]'
    updateCreatedBy = 'td[data-cy="update-created-by-{}"]'
    updateDetails = 'td[data-cy="update-details-{}"]'
    updateStatus = 'td[data-cy="update-status-{}"]'
    statusContainer = 'div[data-cy="status-container"]'
    tablePagination = 'div[data-cy="table-pagination"]'

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

    def getPduTemplates(self) -> WebElement:
        return self.wait_for(self.pduTemplates)

    def getPduUpdates(self) -> WebElement:
        return self.wait_for(self.pduUpdates)

    def getHeadCellImportId(self) -> WebElement:
        return self.wait_for(self.headCellImportId)

    def getTableLabel(self) -> WebElement:
        return self.wait_for(self.tableLabel)

    def getHeadCellTemplateId(self) -> WebElement:
        return self.wait_for(self.headCellTemplateId)

    def getHeadCellImportDate(self) -> WebElement:
        return self.wait_for(self.headCellImportDate)

    def getHeadCellImportedBy(self) -> WebElement:
        return self.wait_for(self.headCellImportedBy)

    def getHeadCellDetails(self) -> WebElement:
        return self.wait_for(self.headCellDetails)

    def getHeadCellStatus(self) -> WebElement:
        return self.wait_for(self.headCellStatus)

    def getupdateRow(self, index: int) -> WebElement:
        locator = self.updateRow.format(index)
        return self.wait_for(locator)

    def getUpdateId(self, index: int) -> WebElement:
        locator = self.updateId.format(index)
        return self.wait_for(locator, timeout=120)

    def getUpdateTemplate(self, index: int) -> WebElement:
        locator = self.updateTemplate.format(index)
        return self.wait_for(locator)

    def getUpdateCreatedAt(self, index: int) -> WebElement:
        locator = self.updateCreatedAt.format(index)
        return self.wait_for(locator)

    def getUpdateCreatedBy(self, index: int) -> WebElement:
        locator = self.updateCreatedBy.format(index)
        return self.wait_for(locator)

    def getUpdateDetails(self, index: int) -> WebElement:
        locator = self.updateDetails.format(index)
        return self.wait_for(locator)

    def getUpdateStatus(self, index: int) -> WebElement:
        locator = self.updateStatus.format(index)
        return self.wait_for(locator)

    def getStatusContainer(self) -> WebElement:
        return self.wait_for(self.statusContainer)
