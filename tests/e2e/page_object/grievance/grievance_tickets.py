from time import sleep

from e2e.page_object.base_components import BaseComponents
from e2e.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException


class GrievanceTickets(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    searchFilter = 'div[data-cy="filters-search"]'
    documentTypeFilter = 'div[data-cy="filters-document-type"]'
    ticketId = 'li[data-value="ticket_id"]'
    householdId = 'li[data-value="ticket_hh_id"]'
    familyName = 'li[data-value="full_name"]'
    tabSystemGenerated = 'button[data-cy="tab-SYSTEM-GENERATED"]'
    tabUserGenerated = 'button[data-cy="tab-USER-GENERATED"]'
    buttonCloseTicket = 'button[data-cy="button-close-ticket"]'
    buttonConfirm = 'button[data-cy="button-confirm"]'
    creationDateFromFilter = 'div[data-cy="filters-creation-date-from"]'
    creationDateToFilter = 'div[data-cy="filters-creation-date-to"]'
    statusFilter = 'div[data-cy="filters-status"]'
    fspFilter = 'div[data-cy="filters-fsp"]'
    categoryFilter = 'div[data-cy="filters-category"]'
    assigneeFilter = 'div[data-cy="filters-assignee"]'
    adminLevelFilter = 'div[data-cy="filters-admin-level-2"]'
    registrationDataImportFilter = 'div[data-cy="filters-registration-data-import"]'
    preferredLanguageFilter = 'div[data-cy="filters-preferred-language"]'
    priorityFilter = 'div[data-cy="filters-priority'
    urgencyFilter = 'div[data-cy="filters-urgency'
    activeTicketsFilter = 'div[data-cy="filters-active-tickets'
    similarityScoreFromFilter = 'div[data-cy="filters-similarity-score-from'
    similarityScoreToFilter = 'div[data-cy="filters-similarity-score-to'
    buttonApply = 'button[data-cy="button-filters-apply"]'
    buttonClear = 'button[data-cy="button-filters-clear"]'
    buttonNewTicket = 'a[data-cy="button-new-ticket"]'
    tabTitle = 'h6[data-cy="table-title"]'
    tabTicketID = 'th[data-cy="ticket-id"]'
    tabStatus = 'th[data-cy="status"]'
    tabAssignedTo = 'th[data-cy="assignedTo"]'
    tabCategory = 'th[data-cy="category"]'
    tabIssueType = 'th[data-cy="issueType"]'
    tabHouseholdID = 'th[data-cy="householdId"]'
    tabPriority = 'th[data-cy="priority"]'
    tabUrgency = 'th[data-cy="urgency"]'
    tabLinkedTickets = 'th[data-cy="linkedTickets"]'
    tabCreationData = 'th[data-cy="createdAt"]'
    tabLastModifiedDate = 'th[data-cy="userModified"]'
    tabTotalDays = 'th[data-cy="totalDays"]'
    ticketListRow = 'tr[role="checkbox"]'
    statusOptions = 'li[role="option"]'
    filtersCreatedBy = 'div[data-cy="filters-created-by-input"]'
    selectAll = 'span[data-cy="checkbox-select-all"]'
    tableLabel = 'span[data-cy="table-label"]'
    buttonAssign = 'button[data-cy="button-Assign"]'
    buttonSetPriority = 'button[data-cy="button-Set priority"]'
    buttonSetUrgency = 'button[data-cy="button-Set Urgency"]'
    buttonAddNote = 'button[data-cy="button-add note"]'
    selectedTickets = 'span[data-cy="selected-tickets"]'
    buttonCancel = 'button[data-cy="button-cancel"]'
    buttonSave = 'button[data-cy="button-save"]'
    dropdown = 'tbody[data-cy="dropdown"]'
    statusContainer = '[data-cy="status-container"]'
    dateTitleFilterPopup = 'div[class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]'
    daysFilterPopup = (
        'div[class="MuiPickersSlideTransition-transitionContainer MuiPickersCalendar-transitionContainer"]'
    )

    # Texts
    textTitle = "Grievance Tickets"
    textTabTitle = "Grievance Tickets List"

    # Elements
    def getDropdown(self) -> WebElement:
        return self.wait_for(self.dropdown)

    def getStatusContainer(self) -> [WebElement]:
        self.wait_for(self.statusContainer)
        return self.get_elements(self.statusContainer)

    def getButtonCancel(self) -> WebElement:
        return self.wait_for(self.buttonCancel)

    def getButtonSave(self) -> WebElement:
        return self.wait_for(self.buttonSave)

    def getSelectedTickets(self) -> WebElement:
        return self.wait_for(self.selectedTickets)

    def getGrievanceTitle(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getTabTitle(self) -> WebElement:
        return self.wait_for(self.tabTitle)

    def getSearchFilter(self) -> WebElement:
        return self.wait_for(self.searchFilter)

    def getTicketTypeFilter(self) -> WebElement:
        return self.wait_for(self.documentTypeFilter)

    def getCreationDateFromFilter(self) -> WebElement:
        return self.wait_for(self.creationDateFromFilter)

    def getCreationDateToFilter(self) -> WebElement:
        return self.wait_for(self.creationDateToFilter)

    def getStatusFilter(self) -> WebElement:
        return self.wait_for(self.statusFilter)

    def getFspFilter(self) -> WebElement:
        return self.wait_for(self.fspFilter)

    def getCategoryFilter(self) -> WebElement:
        return self.wait_for(self.categoryFilter)

    def getAssigneeFilter(self) -> WebElement:
        return self.wait_for(self.assigneeFilter)

    def getAdminLevelFilter(self) -> WebElement:
        return self.wait_for(self.adminLevelFilter)

    def getRegistrationDataImportFilter(self) -> WebElement:
        return self.wait_for(self.registrationDataImportFilter)

    def getPreferredLanguageFilter(self) -> WebElement:
        return self.wait_for(self.preferredLanguageFilter)

    def getPriorityFilter(self) -> WebElement:
        return self.wait_for(self.priorityFilter)

    def getUrgencyFilter(self) -> WebElement:
        return self.wait_for(self.urgencyFilter)

    def getActiveTicketsFilter(self) -> WebElement:
        return self.wait_for(self.activeTicketsFilter)

    def getFiltersCreatedBy(self) -> WebElement:
        return self.wait_for(self.filtersCreatedBy)

    def getSimilarityScoreFromFilter(self) -> WebElement:
        return self.wait_for(self.similarityScoreFromFilter)

    def getSimilarityScoreToFilter(self) -> WebElement:
        return self.wait_for(self.similarityScoreToFilter)

    def getButtonApply(self) -> WebElement:
        return self.wait_for(self.buttonApply)

    def getButtonClear(self) -> WebElement:
        return self.wait_for(self.buttonClear)

    def getButtonNewTicket(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.get(self.buttonNewTicket)

    def getTicketID(self) -> WebElement:
        return self.wait_for(self.ticketId)

    def getHouseholdID(self) -> WebElement:
        return self.wait_for(self.householdId)

    def getFamilyName(self) -> WebElement:
        return self.wait_for(self.familyName)

    def getTabTicketID(self) -> WebElement:
        return self.wait_for(self.tabTicketID)

    def getTabStatus(self) -> WebElement:
        return self.wait_for(self.tabStatus)

    def getTabAssignedTo(self) -> WebElement:
        return self.wait_for(self.tabAssignedTo)

    def getTabCategory(self) -> WebElement:
        return self.wait_for(self.tabCategory)

    def getTabIssueType(self) -> WebElement:
        return self.wait_for(self.tabIssueType)

    def getTabHouseholdID(self) -> WebElement:
        return self.wait_for(self.tabHouseholdID)

    def getTabPriority(self) -> WebElement:
        return self.wait_for(self.tabPriority)

    def getTabUrgency(self) -> WebElement:
        return self.wait_for(self.tabUrgency)

    def getTabLinkedTickets(self) -> WebElement:
        return self.wait_for(self.tabLinkedTickets)

    def getTabCreationData(self) -> WebElement:
        return self.wait_for(self.tabCreationData)

    def getTabLastModifiedDate(self) -> WebElement:
        return self.wait_for(self.tabLastModifiedDate)

    def getTabTotalDays(self) -> WebElement:
        return self.wait_for(self.tabTotalDays)

    def getTabSystemGenerated(self) -> WebElement:
        return self.wait_for(self.tabSystemGenerated)

    def getTabUserGenerated(self) -> WebElement:
        return self.wait_for(self.tabUserGenerated)

    def getTicketListRow(self) -> [WebElement]:
        self.wait_for(self.ticketListRow)
        return self.get_elements(self.ticketListRow)

    def getTableLabel(self) -> [WebElement]:
        return self.get_elements(self.tableLabel)

    def getDateTitleFilterPopup(self) -> WebElement:
        return self.wait_for(self.dateTitleFilterPopup)

    def getDaysFilterPopup(self) -> WebElement:
        return self.wait_for(self.daysFilterPopup)

    def getOptions(self) -> WebElement:
        return self.wait_for(self.statusOptions)

    def getSelectAll(self) -> WebElement:
        return self.wait_for(self.selectAll)

    def getButtonAssign(self) -> WebElement:
        return self.wait_for(self.buttonAssign)

    def getButtonSetPriority(self) -> WebElement:
        return self.wait_for(self.buttonSetPriority)

    def getButtonSetUrgency(self) -> WebElement:
        return self.wait_for(self.buttonSetUrgency)

    def getButtonAddNote(self) -> WebElement:
        return self.wait_for(self.buttonAddNote)

    def getButtonCloseTicket(self) -> WebElement:
        return self.wait_for(self.buttonCloseTicket)

    def getButtonConfirm(self) -> WebElement:
        return self.wait_for(self.buttonConfirm)

    def checkIfTextExistInArow(self, row_index: int, text: str, max_attempts: int = 5) -> None:
        attempt = 0
        exception = None
        while attempt < max_attempts:
            try:
                self.waitForRows()
                self.waitForRowWithText(row_index, text)
                return
            except StaleElementReferenceException as e:
                attempt += 1
                exception = e
        raise exception
