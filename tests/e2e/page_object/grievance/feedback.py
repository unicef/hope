from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class Feedback(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    buttonSubmitNewFeedback = 'a[data-cy="button-submit-new-feedback"]'
    filterSearch = 'div[data-cy="filters-search"]'
    filterIssueType = 'div[data-cy="filters-issue-type"]'
    filterCreatedBy = 'div[data-cy="Created by-input"]'
    filterCreationDateFrom = 'div[data-cy="filters-creation-date-from"]'
    filterCreationDateTo = 'div[data-cy="filters-creation-date-to"]'
    buttonClear = 'button[data-cy="button-filters-clear"]'
    buttonApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableColumns = 'span[data-cy="table-label"]'
    tableRow = 'tr[role="checkbox"]'
    searchFilter = 'div[data-cy="filters-search"]'
    daysFilterPopup = (
        'div[class="MuiPickersSlideTransition-transitionContainer MuiPickersCalendar-transitionContainer"]'
    )
    creationDateToFilter = 'div[data-cy="filters-creation-date-to"]'
    dateTitleFilterPopup = 'div[class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]'
    issueTypeFilter = 'div[data-cy="filters-issue-type"]'
    option = 'li[role="option"]'
    tableRowLoading = 'tr[data-cy="table-row"]'

    # Texts
    textTitle = "Feedback"
    textTableTitle = "Feedbacks List"
    textFeedbackID = "Feedback ID"
    textIssueType = "Issue Type"
    textHouseholdID = "Group ID"
    textLinkedGrievance = "Linked Grievance"
    textCreatedBy = "Created by"
    textCreationDate = "Creation Date"

    # Elements
    def getTitlePage(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getButtonSubmitNewFeedback(self) -> WebElement:
        return self.wait_for(self.buttonSubmitNewFeedback)

    def getFilterSearch(self) -> WebElement:
        return self.wait_for(self.filterSearch)

    def getFilterIssueType(self) -> WebElement:
        return self.wait_for(self.filterIssueType)

    def getFilterCreatedBy(self) -> WebElement:
        return self.wait_for(self.filterCreatedBy)

    def getFilterCreationDateFrom(self) -> WebElement:
        return self.get_elements(self.filterCreationDateFrom)

    def getFilterCreationDateTo(self) -> WebElement:
        return self.get_elements(self.filterCreationDateTo)

    def getButtonClear(self) -> WebElement:
        return self.wait_for(self.buttonClear)

    def getButtonApply(self) -> WebElement:
        return self.wait_for(self.buttonApply)

    def getSearchFilter(self) -> WebElement:
        return self.wait_for(self.searchFilter)

    def getTableTitle(self) -> WebElement:
        return self.wait_for(self.tableTitle)

    def getFeedbackID(self) -> WebElement:
        return self.get_elements(self.tableColumns)[0]

    def getIssueType(self) -> WebElement:
        return self.get_elements(self.tableColumns)[1]

    def getHouseholdID(self) -> WebElement:
        return self.get_elements(self.tableColumns)[2]

    def getLinkedGrievance(self) -> WebElement:
        return self.get_elements(self.tableColumns)[3]

    def getCreatedBy(self) -> WebElement:
        return self.get_elements(self.tableColumns)[4]

    def getCreationDate(self) -> WebElement:
        return self.get_elements(self.tableColumns)[5]

    def getRows(self) -> list[WebElement]:
        return self.get_elements(self.tableRow)

    def getRow(self, number: int) -> WebElement:
        for _ in range(10):
            if len(self.get_elements(self.tableRow)) == number + 1:
                break
            sleep(1)
        return self.get_elements(self.tableRow)[number]

    def getDaysFilterPopup(self) -> WebElement:
        return self.wait_for(self.daysFilterPopup)

    def getCreationDateToFilter(self) -> WebElement:
        return self.wait_for(self.creationDateToFilter)

    def getDateTitleFilterPopup(self) -> WebElement:
        return self.wait_for(self.dateTitleFilterPopup)

    def getIssueTypeFilter(self) -> WebElement:
        return self.wait_for(self.issueTypeFilter)

    def disappearTableRowLoading(self) -> WebElement:
        return self.wait_for_disappear(self.tableRowLoading)

    def getTableRowLoading(self) -> WebElement:
        return self.wait_for(self.tableRowLoading)

    def getOption(self) -> WebElement:
        return self.wait_for(self.option)
