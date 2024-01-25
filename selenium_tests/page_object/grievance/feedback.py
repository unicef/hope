from page_object.base_components import BaseComponents


class Feedback(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    buttonSubmitNewFeedback = 'a[data-cy="button-submit-new-feedback"]'
    filterSearch = 'div[data-cy="filters-search"]'
    filterIssueType = 'div[data-cy="filters-issue-type"]'
    filterCreatedBy = 'div[data-cy="filters-created-by"]'
    filterCreationDateFrom = 'div[data-cy="filters-creation-date-from"]'
    filterCreationDateTo = 'div[data-cy="filters-creation-date-to"]'
    buttonClear = 'button[data-cy="button-filters-clear"]'
    buttonApply = 'button[data-cy="button-filters-apply"]'
    tableTitle = 'h6[data-cy="table-title"]'
    tableColumns = 'span[data-cy="table-label"]'
    tableRow = 'tr[role="checkbox"]'
    searchFilter = 'div[data-cy="filters-search"]'
    daysFilterPopup = 'div[class="MuiPickersSlideTransition-transitionContainer MuiPickersCalendar-transitionContainer"]'
    creationDateToFilter = 'div[data-cy="filters-creation-date-to"]'
    dateTitleFilterPopup = 'div[class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]'
    issueTypeFilter = 'div[data-cy="filters-issue-type"]'
    option = 'li[role="option"]'

    # Texts
    textTitle = "Feedback"
    textTableTitle = "Feedbacks List"
    textFeedbackID = "Feedback ID"
    textIssueType = "Issue Type"
    textHouseholdID = "Household ID"
    textLinkedGrievance = "Linked Grievance"
    textCreatedBy = "Created by"
    textCreationDate = "Creation Date"

    # Elements
    def getTitlePage(self):
        return self.wait_for(self.titlePage)

    def getButtonSubmitNewFeedback(self):
        return self.wait_for(self.buttonSubmitNewFeedback)

    def getFilterSearch(self):
        return self.wait_for(self.filterSearch)

    def getFilterIssueType(self):
        return self.wait_for(self.filterIssueType)

    def getFilterCreatedBy(self):
        return self.wait_for(self.filterCreatedBy)

    def getFilterCreationDateFrom(self):
        return self.wait_for(self.filterCreationDateFrom)

    def getFilterCreationDateTo(self):
        return self.wait_for(self.filterCreationDateTo)

    def getButtonClear(self):
        return self.wait_for(self.buttonClear)

    def getButtonApply(self):
        return self.wait_for(self.buttonApply)

    def getSearchFilter(self):
        return self.wait_for(self.searchFilter)

    def getTableTitle(self):
        return self.wait_for(self.tableTitle)

    def getFeedbackID(self):
        return self.wait_for(self.tableColumns).eq(0)

    def getIssueType(self):
        return self.wait_for(self.tableColumns).eq(1)

    def getHouseholdID(self):
        return self.wait_for(self.tableColumns).eq(2)

    def getLinkedGrievance(self):
        return self.wait_for(self.tableColumns).eq(3)

    def getCreatedBy(self):
        return self.wait_for(self.tableColumns).eq(4)

    def getCreationDate(self):
        return self.wait_for(self.tableColumns).eq(5)

    def getRows(self):
        return self.wait_for(self.tableRow)

    def getDaysFilterPopup(self):
        return self.wait_for(self.daysFilterPopup)

    def getCreationDateToFilter(self):
        return self.wait_for(self.creationDateToFilter)

    def getDateTitleFilterPopup(self):
        return self.wait_for(self.dateTitleFilterPopup)

    def getIssueTypeFilter(self):
        return self.wait_for(self.issueTypeFilter)

    def getOption(self):
        return self.wait_for(self.option)
