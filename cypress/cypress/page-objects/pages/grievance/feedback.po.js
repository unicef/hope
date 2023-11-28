import BaseComponent from "../../base.component";

export default class Feedback extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  buttonSubmitNewFeedback = 'a[data-cy="button-submit-new-feedback"]';
  filterSearch = 'div[data-cy="filters-search"]';
  filterIssueType = 'div[data-cy="filters-issue-type"]';
  filterCreatedBy = 'div[data-cy="Created by-input"]';
  filterCreationDateFrom = 'div[data-cy="filters-creation-date-from"]';
  filterCreationDateTo = 'div[data-cy="filters-creation-date-to"]';
  buttonClear = 'button[data-cy="button-filters-clear"]';
  buttonApply = 'button[data-cy="button-filters-apply"]';
  tableTitle = 'h6[data-cy="table-title"]';
  tableColumns = 'span[data-cy="table-label"]';
  tableRow = 'tr[role="checkbox"]';
  searchFilter = 'div[data-cy="filters-search"]';
  daysFilterPopup =
    'div[class="MuiPickersSlideTransition-transitionContainer MuiPickersCalendar-transitionContainer"]';
  creationDateToFilter = 'div[data-cy="filters-creation-date-to"]';
  dateTitleFilterPopup =
    'div[class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]';
  issueTypeFilter = 'div[data-cy="filters-issue-type"]';
  option = 'li[role="option"]';

  // Texts
  textTitle = "Feedback";
  textTableTitle = "Feedbacks List";
  textFeedbackID = "Feedback ID";
  textIssueType = "Issue Type";
  textHouseholdID = "Household ID";
  textLinkedGrievance = "Linked Grievance";
  textCreatedBy = "Created by";
  textCreationDate = "Creation Date";
  // Elements
  getTitlePage = () => cy.get(this.titlePage);
  getButtonSubmitNewFeedback = () => cy.get(this.buttonSubmitNewFeedback);
  getFilterSearch = () => cy.get(this.filterSearch);
  getFilterIssueType = () => cy.get(this.filterIssueType);
  getFilterCreatedBy = () => cy.get(this.filterCreatedBy);
  getFilterCreationDateFrom = () => cy.get(this.filterCreationDateFrom);
  getFilterCreationDateTo = () => cy.get(this.filterCreationDateTo);
  getButtonClear = () => cy.get(this.buttonClear);
  getButtonApply = () => cy.get(this.buttonApply);
  getSearchFilter = () => cy.get(this.searchFilter);
  getTableTitle = () => cy.get(this.tableTitle);
  getFeedbackID = () => cy.get(this.tableColumns).eq(0);
  getIssueType = () => cy.get(this.tableColumns).eq(1);
  getHouseholdID = () => cy.get(this.tableColumns).eq(2);
  getLinkedGrievance = () => cy.get(this.tableColumns).eq(3);
  getCreatedBy = () => cy.get(this.tableColumns).eq(4);
  getCreationDate = () => cy.get(this.tableColumns).eq(5);
  getRows = () => cy.get(this.tableRow);
  getDaysFilterPopup = () => cy.get(this.daysFilterPopup);
  getCreationDateToFilter = () => cy.get(this.creationDateToFilter);
  getDateTitleFilterPopup = () => cy.get(this.dateTitleFilterPopup);
  getIssueTypeFilter = () => cy.get(this.issueTypeFilter);
  getOption = () => cy.get(this.option);

  checkElementsOnPage() {
    this.getTitlePage().contains(this.textTitle);
    this.getButtonSubmitNewFeedback().should("be.visible");
    this.getFilterSearch().should("be.visible");
    this.getFilterIssueType().should("be.visible");
    this.getFilterCreatedBy().should("be.visible");
    this.getFilterCreationDateFrom().should("be.visible");
    this.getFilterCreationDateTo().should("be.visible");
    this.getButtonClear().should("be.visible");
    this.getButtonApply().should("be.visible");
    this.getTableTitle().contains(this.textTableTitle);
    this.getFeedbackID().contains(this.textFeedbackID);
    this.getIssueType().contains(this.textIssueType);
    this.getHouseholdID().contains(this.textHouseholdID);
    this.getLinkedGrievance().contains(this.textLinkedGrievance);
    this.getCreatedBy().contains(this.textCreatedBy);
    this.getCreationDate().contains(this.textCreationDate);
  }

  clickButtonSubmitNewFeedback() {
    this.getButtonSubmitNewFeedback().click();
  }

  chooseTableRow(num) {
    this.getRows().eq(num).click();
  }

  useSearchFilter(text) {
    this.getSearchFilter().type(text);
    this.getButtonApply().click();
  }

  chooseTicketListRow(num = 0, contains = "FED-23-0001") {
    return this.getRows().eq(num).find("a").contains(contains);
  }

  expectedNumberOfRows(num) {
    if (num === 0) {
      this.getRows().should("not.exist");
    } else {
      this.getRows().should("have.length", num);
    }
  }

  changeCreationDateTo(date) {
    // Date format (String): YYYY-MM-DD
    this.getCreationDateToFilter().type(date);
  }

  useCreatedByFilter(mail) {
    this.getFilterCreatedBy().click();
    this.getFilterCreatedBy().type(mail).type("{enter}");
    this.getOption().first().contains(mail).click();
    this.getButtonApply().click();
  }

  useIssueTypeFilter(issueType) {
    this.getIssueTypeFilter().click();
    this.getOption().contains(issueType).click();
    this.getButtonApply().click();
  }

  checkDateFilterTo(date) {
    // Date format (String): YYYY-MM-DD
    this.getCreationDateToFilter().find("input").should("have.value", date);
  }

  openCreationDateToFilter() {
    this.getCreationDateToFilter().find("button").click();
  }

  checkDateTitleFilter(date) {
    // Date format (String): Www, Mmm D
    // Example: Sat, Jan 1
    this.getDateTitleFilterPopup().contains(date).type("{esc}");
  }

  chooseDayFilterPopup(day) {
    this.getDaysFilterPopup().contains("p", day).click();
  }
}
