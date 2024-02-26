from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class Grievance(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    searchFilter = 'div[data-cy="filters-search"]'
    ticketTypeFilter = 'div[data-cy="filters-search-type"]'
    ticketId = 'li[data-value="ticket_id"]'
    householdId = 'li[data-value="ticket_hh_id"]'
    familyName = 'li[data-value="full_name"]'
    tabSystemGenerated = 'button[data-cy="tab-SYSTEM-GENERATED"]'
    tabUserGenerated = 'button[data-cy="tab-USER-GENERATED"]'
    creationDateFromFilter = 'div[data-cy="filters-creation-date-from"]'
    creationDateToFilter = 'div[data-cy="filters-creation-date-to"]'
    statusFilter = 'div[data-cy="filters-status"]'
    fspFilter = 'div[data-cy="filters-fsp"]'
    categoryFilter = 'div[data-cy="filters-category"]'
    assigneeFilter = 'div[data-cy="filters-assignee"]'
    adminLevelFilter = 'div[data-cy="filters-admin-level"]'
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

    dateTitleFilterPopup = 'div[class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]'
    daysFilterPopup = (
        'div[class="MuiPickersSlideTransition-transitionContainer MuiPickersCalendar-transitionContainer"]'
    )

    # Texts
    textTitle = "Grievance Tickets"
    textTabTitle = "Grievance Tickets List"

    # Elements

    def getGrievanceTitle(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getTabTitle(self) -> WebElement:
        return self.wait_for(self.tabTitle)

    def getSearchFilter(self) -> WebElement:
        return self.wait_for(self.searchFilter)

    def getTicketTypeFilter(self) -> WebElement:
        return self.wait_for(self.ticketTypeFilter)

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
        return self.wait_for(self.buttonNewTicket)

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

    def getTicketListRow(self) -> WebElement:
        return self.wait_for(self.ticketListRow)

    def getDateTitleFilterPopup(self) -> WebElement:
        return self.wait_for(self.dateTitleFilterPopup)

    def getDaysFilterPopup(self) -> WebElement:
        return self.wait_for(self.daysFilterPopup)

    def getOptions(self) -> WebElement:
        return self.wait_for(self.statusOptions)

    def checkElementsOnUserGeneratedPage(self) -> None:
        self.getGrievanceTitle().contains(self.textTitle)
        self.getTabTitle().contains(self.textTabTitle)
        self.getTabUserGenerated().should("be.visible")
        self.getTabSystemGenerated().should("be.visible")
        self.checkAllSearchFieldsVisible()
        self.getButtonNewTicket().should("be.visible")
        self.checkAllColumnsVisibility()

    def chooseCategoryFilter(self, category: str) -> None:
        self.getCategoryFilter().click()
        self.getOptions().contains(category).click()
        self.getButtonApply().click()

    def chooseStatusFilter(self, status: str) -> None:
        self.getStatusFilter().click()
        self.getOptions().contains(status).click()
        self.getButtonApply().click()

    def choosePriorityFilter(self, prio: str) -> None:
        self.getPriorityFilter().click()
        self.getOptions().contains(prio).click()
        self.getButtonApply().click()

    def chooseUrgencyFilter(self, urgency: str) -> None:
        self.getUrgencyFilter().click()
        self.getOptions().contains(urgency).click()
        self.getButtonApply().click()

    def chooseRDIFilter(self, rdi: str) -> None:
        self.getRegistrationDataImportFilter().click()
        self.getOptions().contains(rdi).click()
        self.getButtonApply().click()

    def chooseAdminFilter(self, name: str) -> None:
        self.getAdminLevelFilter().click()
        self.getOptions().contains(name).click()
        self.getButtonApply().click()

    def chooseAssigneeFilter(self, mail: str) -> None:
        self.getAssigneeFilter().click()
        self.getOptions().contains(mail).click()
        self.getButtonApply().click()

    def checkElementsOnSystemGeneratedPage(self) -> None:
        self.getTabSystemGenerated().click()
        self.getGrievanceTitle().contains(self.textTitle)
        self.getTabTitle().contains(self.textTabTitle)
        self.checkAllSearchFieldsVisible()
        self.getSimilarityScoreFromFilter().should("be.visible")
        self.getSimilarityScoreToFilter().should("be.visible")
        self.checkAllColumnsVisibility()
        self.getTicketListRow().eq(0).should("be.visible")

    def checkElementsOfTicketTypeFilter(self) -> None:
        self.getTicketTypeFilter().click()
        self.getTicketID().should("be.visible")
        self.getHouseholdID().should("be.visible")
        self.pressEscapeFromElement(self.getFamilyName().should("be.visible"))

    def checkAllSearchFieldsVisible(self) -> None:
        self.getSearchFilter().should("be.visible")
        self.getTicketTypeFilter().should("be.visible")
        self.getCreationDateFromFilter().should("be.visible")
        self.getCreationDateToFilter().should("be.visible")
        self.getStatusFilter().should("be.visible")
        self.getFspFilter().should("be.visible")
        self.getCategoryFilter().should("be.visible")
        self.getAssigneeFilter().should("be.visible")
        self.getAdminLevelFilter().should("be.visible")
        self.getRegistrationDataImportFilter().should("be.visible")
        self.getPreferredLanguageFilter().should("be.visible")
        self.getPriorityFilter().should("be.visible")
        self.getUrgencyFilter().should("be.visible")
        self.getActiveTicketsFilter().should("be.visible")
        self.checkElementsOfTicketTypeFilter()
        self.getButtonApply().should("be.visible")
        self.getButtonClear().should("be.visible")

    def checkAllColumnsVisibility(self) -> None:
        self.getTabTicketID().should("be.visible")
        self.getTabStatus().should("be.visible")
        self.getTabAssignedTo().should("be.visible")
        self.getTabCategory().scrollIntoView().should("be.visible")
        self.getTabIssueType().scrollIntoView().should("be.visible")
        self.getTabHouseholdID().scrollIntoView().should("be.visible")
        self.getTabPriority().scrollIntoView().should("be.visible")
        self.getTabUrgency().scrollIntoView().should("be.visible")
        self.getTabLinkedTickets().scrollIntoView().should("be.visible")
        self.getTabCreationData().scrollIntoView().should("be.visible")
        self.getTabLastModifiedDate().scrollIntoView().should("be.visible")
        self.getTabTotalDays().scrollIntoView().should("be.visible")

    def useSearchFilter(self, text: str) -> None:
        self.getSearchFilter().type(text)
        self.getButtonApply().click()

    def chooseTicketTypeHouseholdID(self) -> None:
        self.getTicketTypeFilter().click()
        self.getHouseholdID().click()
        self.pressEscapeFromElement(self.getHouseholdID())
        self.getButtonApply().click()

    def chooseTicketTypeTicketID(self) -> None:
        self.getTicketTypeFilter().click()
        self.getTicketID().click()
        self.pressEscapeFromElement(self.getTicketID())
        self.getButtonApply().click()

    def chooseTicketTypeLastName(self) -> None:
        self.getTicketTypeFilter().click()
        self.getFamilyName().click()
        self.pressEscapeFromElement(self.getFamilyName())
        self.getButtonApply().click()

    def checkTicketTypeFilterText(self, text: str) -> WebElement:
        return self.getTicketTypeFilter().find("div").eq(0).scrollIntoView().contains(text)

    def changeCreationDateFrom(self, date: str) -> WebElement:
        # Date format (String): YYYY-MM-DD
        return self.getCreationDateFromFilter().type(date)

    def openCreationDateFromFilter(self) -> WebElement:
        return self.getCreationDateFromFilter().find("button").click()

    def chooseDayFilterPopup(self, day: str) -> WebElement:
        return self.getDaysFilterPopup().contains("p", day).click()

    def checkDateFilterFrom(self, date: str) -> WebElement:
        # Date format (String): YYYY-MM-DD
        return self.getCreationDateFromFilter().find("input").should("have.value", date)

    def changeCreationDateTo(self, date: str) -> WebElement:
        # Date format (String): YYYY-MM-DD
        return self.getCreationDateToFilter().type(date)

    def openCreationDateToFilter(self) -> WebElement:
        return self.getCreationDateToFilter().find("button").click()

    def checkDateFilterTo(self, date: str) -> WebElement:
        # Date format (String): YYYY-MM-DD
        return self.getCreationDateToFilter().find("input").should("have.value", date)

    def checkDateTitleFilter(self, date: str) -> WebElement:
        # Date format (String): Www, Mmm D
        # Example: Sat, Jan 1
        return self.getDateTitleFilterPopup().contains(date).type("{esc}")
