from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class ManagerialConsole(BaseComponents):
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    title = 'h6[data-cy="title"]'
    approveButton = 'button[data-cy="approve-button"]'
    selectAllApproval = 'span[data-cy="select-all-approval"]'
    programSelectApproval = 'div[data-cy="program-select-approval"]'
    selectApproval = 'span[data-cy="select-approval"]'
    columnField = 'td[data-cy="column-field"]'
    authorizeButton = 'button[data-cy="authorize-button"]'
    selectAllAuthorization = 'span[data-cy="select-all-authorization"]'
    programSelectAuthorization = 'div[data-cy="program-select-authorization"]'
    selectAuthorization = 'span[data-cy="select-authorization"]'
    columnFieldAuthorization = 'td[data-cy="column-field-authorization"]'
    releaseButton = 'button[data-cy="release-button"]'
    selectAllRelease = 'span[data-cy="select-all-release"]'
    programSelectRelease = 'div[data-cy="program-select-release"]'
    selectRelease = 'span[data-cy="select-release"]'
    columnFieldRelease = 'td[data-cy="column-field-release"]'
    searchReleased = 'div[data-cy="search-released"]'
    programSelectReleased = 'div[data-cy="program-select-released"]'
    columnFieldReleased = 'td[data-cy="column-field-released"]'
    plansIds = 'span[data-cy="plans-ids"]'
    buttonCancel = 'button[data-cy="button-cancel"]'
    buttonSave = 'button[data-cy="button-save"]'
    commentApprove = 'div[data-cy="comment-approve"]'

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getTitle(self) -> WebElement:
        return self.wait_for(self.title)

    def getApproveButton(self) -> WebElement:
        return self.wait_for(self.approveButton)

    def getSelectAllApproval(self) -> WebElement:
        return self.wait_for(self.selectAllApproval)

    def getProgramSelectApproval(self) -> WebElement:
        return self.wait_for(self.programSelectApproval)

    def getSelectApproval(self) -> WebElement:
        return self.wait_for(self.selectApproval)

    def getColumnField(self) -> WebElement:
        return self.wait_for(self.columnField)

    def getAuthorizeButton(self) -> WebElement:
        return self.wait_for(self.authorizeButton)

    def getSelectAllAuthorization(self) -> WebElement:
        return self.wait_for(self.selectAllAuthorization)

    def getProgramSelectAuthorization(self) -> WebElement:
        return self.wait_for(self.programSelectAuthorization)

    def getSelectAuthorization(self) -> WebElement:
        return self.wait_for(self.selectAuthorization)

    def getColumnFieldAuthorization(self) -> WebElement:
        return self.wait_for(self.columnFieldAuthorization)

    def getReleaseButton(self) -> WebElement:
        return self.wait_for(self.releaseButton)

    def getSelectAllRelease(self) -> WebElement:
        return self.wait_for(self.selectAllRelease)

    def getProgramSelectRelease(self) -> WebElement:
        return self.wait_for(self.programSelectRelease)

    def getSelectRelease(self) -> WebElement:
        return self.wait_for(self.selectRelease)

    def getColumnFieldRelease(self) -> WebElement:
        return self.wait_for(self.columnFieldRelease)

    def getSearchReleased(self) -> WebElement:
        return self.wait_for(self.searchReleased)

    def getProgramSelectReleased(self) -> WebElement:
        return self.wait_for(self.programSelectReleased)

    def getColumnFieldReleased(self) -> WebElement:
        return self.wait_for(self.columnFieldReleased)

    def getPlansIds(self) -> WebElement:
        return self.wait_for(self.plansIds)

    def getButtonCancel(self) -> WebElement:
        return self.wait_for(self.buttonCancel)

    def getButtonSave(self) -> WebElement:
        return self.wait_for(self.buttonSave)

    def getCommentApprove(self) -> WebElement:
        return self.wait_for(self.commentApprove)
