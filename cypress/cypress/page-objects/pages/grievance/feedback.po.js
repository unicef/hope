import BaseComponent from "../../base.component";

export default class Feedback extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  buttonSubmitNewFeedback = 'a[data-cy="button-submit-new-feedback"]';
  filterSearch = 'div[data-cy="filters-search"]';
  filterIssueType = 'div[data-cy="filters-issue-type"]';
  filterCreatedBy = 'div[data-cy="filters-created-by"]';
  filterCreationCateFrom = 'div[data-cy="filters-creation-date-from"]';
  filterCreationCateTo = 'div[data-cy="filters-creation-date-to"]';
  buttonClear = 'button[data-cy="button-filters-clear"]';
  buttonApply = 'button[data-cy="button-filters-apply"]';
  tableTitle = 'h6[data-cy="table-title"]';
  tableColumns = 'span[data-cy="table-label"]';
  tableRow = 'tr[data-cy="table-row"]';
  // Texts
  textTitle = "Feedback";
  textTableTitle = "Feedbacks List";
  textFeedbackID = "Feedback ID";
  textIssueType = "Issue Type";
  textHouseholdID = "Household ID";
  textLinkedGrievance = "Linked Grievance";
  textCreatedBy = "Created by";
  textCreationDate = "Creation date";
  // Elements
  getTitlePage = () => cy.get(this.titlePage);
  getButtonSubmitNewFeedback = () => cy.get(this.buttonSubmitNewFeedback);
  getFilterSearch = () => cy.get(this.filterSearch);
  getFilterIssueType = () => cy.get(this.filterIssueType);
  getFilterCreatedBy = () => cy.get(this.filterCreatedBy);
  getFilterCreationCateFrom = () => cy.get(this.filterCreationCateFrom);
  getFilterCreationCateTo = () => cy.get(this.filterCreationCateTo);
  getButtonClear = () => cy.get(this.buttonClear);
  getButtonApply = () => cy.get(this.buttonApply);
  getTableTitle = () => cy.get(this.tableTitle);
  getFeedbackID = () => cy.get(this.tableColumns).eq(0);
  getIssueType = () => cy.get(this.tableColumns).eq(1);
  getHouseholdID = () => cy.get(this.tableColumns).eq(2);
  getLinkedGrievance = () => cy.get(this.tableColumns).eq(3);
  getCreatedBy = () => cy.get(this.tableColumns).eq(4);
  getCreationDate = () => cy.get(this.tableColumns).eq(5);

  checkElementsOnPage() {
    this.getTitlePage().contains(this.textTitle);
    this.getButtonSubmitNewFeedback().should("be.visible");
    this.getFilterSearch().should("be.visible");
    this.getFilterIssueType().should("be.visible");
    this.getFilterCreatedBy().should("be.visible");
    this.getFilterCreationCateFrom().should("be.visible");
    this.getFilterCreationCateTo().should("be.visible");
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
}
