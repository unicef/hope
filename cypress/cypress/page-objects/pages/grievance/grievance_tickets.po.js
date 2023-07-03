import BaseComponent from "../../base.component";

export default class Grievance extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  searchFilter = 'div[data-cy="filters-search"]';
  ticketTypeFilter = 'div[data-cy="filters-search-type"]';
  ticketId = 'li[data-value="ticket_id"]';
  householdId = 'li[data-value="ticket_hh_id"]';
  lastName = 'li[data-value="last_name"]';
  tabSystemGenerated = 'button[data-cy="tab-SYSTEM-GENERATED"]';
  tabUserGenerated = 'button[data-cy="tab-USER-GENERATED"]';
  creationDateFromFilter = 'div[data-cy="filters-creation-date-from"]';
  creationDateToFilter = 'div[data-cy="filters-creation-date-to"]';
  statusFilter = 'div[data-cy="filters-status"]';
  fspFilter = 'div[data-cy="filters-fsp"]';
  categoryFilter = 'div[data-cy="filters-category"]';
  assigneeFilter = 'div[data-cy="filters-assignee"]';
  adminLevelFilter = 'div[data-cy="filters-admin-level"]';
  registrationDataImportFilter =
    'div[data-cy="filters-registration-data-import"]';
  preferredLanguageFilter = 'div[data-cy="filters-preferred-language"]';
  priorityFilter = 'div[data-cy="filters-priority';
  urgencyFilter = 'div[data-cy="filters-urgency';
  activeTicketsFilter = 'div[data-cy="filters-active-tickets';
  similarityScoreFromFilter = 'div[data-cy="filters-similarity-score-from';
  similarityScoreToFilter = 'div[data-cy="filters-similarity-score-to';
  buttonApply = 'button[data-cy="button-filters-apply"]';
  buttonClear = 'button[data-cy="button-filters-clear"]';
  buttonNewTicket = 'a[data-cy="button-new-ticket"]';
  tabTitle = 'h6[data-cy="table-title"]';
  tabTicketID = 'th[data-cy="ticket-id"]';
  tabStatus = 'th[data-cy="status"]';
  tabAssignedTo = 'th[data-cy="assignedTo"]';
  tabCategory = 'th[data-cy="category"]';
  tabIssueType = 'th[data-cy="issueType"]';
  tabHouseholdID = 'th[data-cy="householdId"]';
  tabPriority = 'th[data-cy="priority"]';
  tabUrgency = 'th[data-cy="urgency"]';
  tabLinkedTickets = 'th[data-cy="linkedTickets"]';
  tabCreationData = 'th[data-cy="createdAt"]';
  tabLastModifiedDate = 'th[data-cy="userModified"]';
  tabTotalDays = 'th[data-cy="totalDays"]';
  ticketListRow = 'tr[role="checkbox"]';
  statusOptions = 'li[role="option"]';

  dateTitleFilterPopup =
    'div[class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]';
  daysFilterPopup =
    'div[class="MuiPickersSlideTransition-transitionContainer MuiPickersCalendar-transitionContainer"]';

  // Texts
  textTitle = "Grievance Tickets";
  textTabTitle = "Grievance Tickets List";

  // Elements
  getGrievanceTitle = () => cy.get(this.titlePage);
  getTabTitle = () => cy.get(this.tabTitle);
  getSearchFilter = () => cy.get(this.searchFilter);
  getTicketTypeFilter = () => cy.get(this.ticketTypeFilter);
  getCreationDateFromFilter = () => cy.get(this.creationDateFromFilter);
  getCreationDateToFilter = () => cy.get(this.creationDateToFilter);
  getStatusFilter = () => cy.get(this.statusFilter);
  getFspFilter = () => cy.get(this.fspFilter);
  getCategoryFilter = () => cy.get(this.categoryFilter);
  getAssigneeFilter = () => cy.get(this.assigneeFilter);
  getAdminLevelFilter = () => cy.get(this.adminLevelFilter);
  getRegistrationDataImportFilter = () =>
    cy.get(this.registrationDataImportFilter);
  getPreferredLanguageFilter = () => cy.get(this.preferredLanguageFilter);
  getPriorityFilter = () => cy.get(this.priorityFilter);
  getUrgencyFilter = () => cy.get(this.urgencyFilter);
  getActiveTicketsFilter = () => cy.get(this.activeTicketsFilter);
  getSimilarityScoreFromFilter = () => cy.get(this.similarityScoreFromFilter);
  getSimilarityScoreToFilter = () => cy.get(this.similarityScoreToFilter);
  getButtonApply = () => cy.get(this.buttonApply);
  getButtonClear = () => cy.get(this.buttonClear);
  getButtonNewTicket = () => cy.get(this.buttonNewTicket);
  getTicketID = () => cy.get(this.ticketId);
  getHouseholdID = () => cy.get(this.householdId);
  getLastName = () => cy.get(this.lastName);
  getTabTicketID = () => cy.get(this.tabTicketID);
  getTabStatus = () => cy.get(this.tabStatus);
  getTabAssignedTo = () => cy.get(this.tabAssignedTo);
  getTabCategory = () => cy.get(this.tabCategory);
  getTabIssueType = () => cy.get(this.tabIssueType);
  getTabHouseholdID = () => cy.get(this.tabHouseholdID);
  getTabPriority = () => cy.get(this.tabPriority);
  getTabUrgency = () => cy.get(this.tabUrgency);
  getTabLinkedTickets = () => cy.get(this.tabLinkedTickets);
  getTabCreationData = () => cy.get(this.tabCreationData);
  getTabLastModifiedDate = () => cy.get(this.tabLastModifiedDate);
  getTabTotalDays = () => cy.get(this.tabTotalDays);
  getTabSystemGenerated = () => cy.get(this.tabSystemGenerated);
  getTabUserGenerated = () => cy.get(this.tabUserGenerated);
  getTicketListRow = () => cy.get(this.ticketListRow);
  getDateTitleFilterPopup = () => cy.get(this.dateTitleFilterPopup);
  getDaysFilterPopup = () => cy.get(this.daysFilterPopup);
  getOptions = () => cy.get(this.statusOptions);

  checkElementsOnUserGeneratedPage() {
    this.getGrievanceTitle().contains(this.textTitle);
    this.getTabTitle().contains(this.textTabTitle);
    this.getTabUserGenerated().should("be.visible");
    this.getTabSystemGenerated().should("be.visible");
    this.checkAllSearchFieldsVisible();
    this.getButtonNewTicket().should("be.visible");
    this.checkAllColumnsVisibility();
  }

  chooseTicketListRow(num = 0, contains = "GRV-0000002") {
    // ToDo: Use after fix bug: 164824
    // return this.getTicketListRow().eq(num);
    return this.getTicketListRow().eq(num).find("a").contains(contains);
  }

  chooseCategoryFilter(category) {
    this.getCategoryFilter().click();
    this.getOptions().contains(category).click();
    this.getButtonApply().click();
  }

  chooseAdminFilter(name) {
    this.getAdminLevelFilter().click();
    this.getOptions().contains(name).click();
    this.getButtonApply().click();
  }

  chooseAssigneeFilter(mail) {
    this.getAssigneeFilter().click();
    this.getOptions().contains(mail).click();
    this.getButtonApply().click();
  }
  checkElementsOnSystemGeneratedPage() {
    this.getTabSystemGenerated().click();
    this.getGrievanceTitle().contains(this.textTitle);
    this.getTabTitle().contains(this.textTabTitle);
    this.checkAllSearchFieldsVisible();
    this.getSimilarityScoreFromFilter().should("be.visible");
    this.getSimilarityScoreToFilter().should("be.visible");
    this.checkAllColumnsVisibility();
    this.getTicketListRow().eq(0).should("be.visible");
  }

  checkElementsOfTicketTypeFilter() {
    this.getTicketTypeFilter().click();
    this.getTicketID().should("be.visible");
    this.getHouseholdID().should("be.visible");
    this.getLastName().should("be.visible").type("{esc}");
  }

  checkAllSearchFieldsVisible() {
    this.getSearchFilter().should("be.visible");
    this.getTicketTypeFilter().should("be.visible");
    this.getCreationDateFromFilter().should("be.visible");
    this.getCreationDateToFilter().should("be.visible");
    this.getStatusFilter().should("be.visible");
    this.getFspFilter().should("be.visible");
    this.getCategoryFilter().should("be.visible");
    this.getAssigneeFilter().should("be.visible");
    this.getAdminLevelFilter().should("be.visible");
    this.getRegistrationDataImportFilter().should("be.visible");
    this.getPreferredLanguageFilter().should("be.visible");
    this.getPriorityFilter().should("be.visible");
    this.getUrgencyFilter().should("be.visible");
    this.getActiveTicketsFilter().should("be.visible");
    this.checkElementsOfTicketTypeFilter();
    this.getButtonApply().should("be.visible");
    this.getButtonClear().should("be.visible");
  }
  checkAllColumnsVisibility() {
    this.getTabTicketID().should("be.visible");
    this.getTabStatus().should("be.visible");
    this.getTabAssignedTo().should("be.visible");
    this.getTabCategory().scrollIntoView().should("be.visible");
    this.getTabIssueType().scrollIntoView().should("be.visible");
    this.getTabHouseholdID().scrollIntoView().should("be.visible");
    this.getTabPriority().scrollIntoView().should("be.visible");
    this.getTabUrgency().scrollIntoView().should("be.visible");
    this.getTabLinkedTickets().scrollIntoView().should("be.visible");
    this.getTabCreationData().scrollIntoView().should("be.visible");
    this.getTabLastModifiedDate().scrollIntoView().should("be.visible");
    this.getTabTotalDays().scrollIntoView().should("be.visible");
  }

  useSearchFilter(text) {
    this.getSearchFilter().type(text);
    this.getButtonApply().click();
  }
  chooseTicketTypeHouseholdID() {
    this.getTicketTypeFilter().click();
    this.getHouseholdID().click().type("{esc}");
    this.getButtonApply().click();
  }

  chooseTicketTypeTicketID() {
    this.getTicketTypeFilter().click();
    this.getTicketID().click().type("{esc}");
    this.getButtonApply().click();
  }

  chooseTicketTypeLastName() {
    this.getTicketTypeFilter().click();
    this.getLastName().click().type("{esc}");
    this.getButtonApply().click();
  }

  checkTicketTypeFilterText(text) {
    this.getTicketTypeFilter()
      .find("div")
      .eq(0)
      .scrollIntoView()
      .contains(text);
  }

  changeCreationDateFrom(date) {
    // Date format (String): YYYY-MM-DD
    this.getCreationDateFromFilter().type(date);
  }

  openCreationDateFromFilter() {
    this.getCreationDateFromFilter().find("button").click();
  }

  chooseDayFilterPopup(day) {
    this.getDaysFilterPopup().contains("p", day).click();
  }

  checkDateFilterFrom(date) {
    // Date format (String): YYYY-MM-DD
    this.getCreationDateFromFilter().find("input").should("have.value", date);
  }

  changeCreationDateTo(date) {
    // Date format (String): YYYY-MM-DD
    this.getCreationDateToFilter().type(date);
  }

  openCreationDateToFilter() {
    this.getCreationDateToFilter().find("button").click();
  }

  checkDateFilterTo(date) {
    // Date format (String): YYYY-MM-DD
    this.getCreationDateToFilter().find("input").should("have.value", date);
  }

  checkDateTitleFilter(date) {
    // Date format (String): Www, Mmm D
    // Example: Sat, Jan 1
    this.getDateTitleFilterPopup().contains(date).type("{esc}");
  }
  chooseTab(tabName) {
    // Possibilities (String): USER-GENERATED, SYSTEM-GENERATED
    cy.get(`button[data-cy="tab-${tabName}"]`).click();
  }

  expectedNumberOfRows(num) {
    if (num === 0) {
      this.getTicketListRow().should("not.exist");
    } else {
      this.getTicketListRow().should("have.length", num);
    }
  }
}
