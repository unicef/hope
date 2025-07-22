from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ProgramLog(BaseComponents):
    mainActivityLogTable = 'div[data-cy="main-activity-log-table"]'
    tableCollapse = 'div[data-cy="table-collapse"]'
    activityLogTable = 'div[data-cy="activity-log-table"]'
    tableHeaderRow = 'div[data-cy="table-header-row"]'
    headerCellDate = 'div[data-cy="header-cell-date"]'
    headerCellUser = 'div[data-cy="header-cell-user"]'
    headerCellContent_type__name = 'div[data-cy="header-cell-content_type__name"]'
    headerCellObject = 'div[data-cy="header-cell-object"]'
    headerCellAction = 'div[data-cy="header-cell-action"]'
    headerCellChanges = 'div[data-cy="header-cell-changes"]'
    headerCellChangefrom = 'div[data-cy="header-cell-changeFrom"]'
    headerCellChangeto = 'div[data-cy="header-cell-changeTo"]'
    logRowSingleChange = 'div[data-cy="log-row-single-change"]'
    timestampCell = 'div[data-cy="timestamp-cell"]'
    userCell = 'div[data-cy="user-cell"]'
    contentTypeCell = 'div[data-cy="content-type-cell"]'
    objectRepresentationCell = 'div[data-cy="object-representation-cell"]'
    actionCell = 'div[data-cy="action-cell"]'
    changeKeyCell = 'div[data-cy="change-key-cell"]'
    fromValueCell = 'div[data-cy="from-value-cell"]'
    toValueCell = 'div[data-cy="to-value-cell"]'
    tablePagination = 'div[data-cy="table-pagination"]'
    paginationActions = 'div[data-cy="pagination-actions"]'
    previousPageButton = 'button[data-cy="previous-page-button"]'
    nextPageButton = 'button[data-cy="next-page-button"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getMainActivityLogTable(self) -> WebElement:
        return self.wait_for(self.mainActivityLogTable)

    def getTableCollapse(self) -> WebElement:
        return self.wait_for(self.tableCollapse)

    def getActivityLogTable(self) -> WebElement:
        return self.wait_for(self.activityLogTable)

    def getTableHeaderRow(self) -> WebElement:
        return self.wait_for(self.tableHeaderRow)

    def getHeaderCellDate(self) -> WebElement:
        return self.wait_for(self.headerCellDate)

    def getHeaderCellUser(self) -> WebElement:
        return self.wait_for(self.headerCellUser)

    def getHeaderCellContent_type__name(self) -> WebElement:
        return self.wait_for(self.headerCellContent_type__name)

    def getHeaderCellObject(self) -> WebElement:
        return self.wait_for(self.headerCellObject)

    def getHeaderCellAction(self) -> WebElement:
        return self.wait_for(self.headerCellAction)

    def getHeaderCellChanges(self) -> WebElement:
        return self.wait_for(self.headerCellChanges)

    def getHeaderCellChangefrom(self) -> WebElement:
        return self.wait_for(self.headerCellChangefrom)

    def getHeaderCellChangeto(self) -> WebElement:
        return self.wait_for(self.headerCellChangeto)

    def getLogRowSingleChange(self) -> WebElement:
        return self.wait_for(self.logRowSingleChange)

    def getTimestampCell(self) -> WebElement:
        return self.wait_for(self.timestampCell)

    def getUserCell(self) -> WebElement:
        return self.wait_for(self.userCell)

    def getContentTypeCell(self) -> WebElement:
        return self.wait_for(self.contentTypeCell)

    def getObjectRepresentationCell(self) -> WebElement:
        return self.wait_for(self.objectRepresentationCell)

    def getActionCell(self) -> WebElement:
        return self.wait_for(self.actionCell)

    def getChangeKeyCell(self) -> WebElement:
        return self.wait_for(self.changeKeyCell)

    def getFromValueCell(self) -> WebElement:
        return self.wait_for(self.fromValueCell)

    def getToValueCell(self) -> WebElement:
        return self.wait_for(self.toValueCell)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getPaginationActions(self) -> WebElement:
        return self.wait_for(self.paginationActions)

    def getPreviousPageButton(self) -> WebElement:
        return self.wait_for(self.previousPageButton)

    def getNextPageButton(self) -> WebElement:
        return self.wait_for(self.nextPageButton)
