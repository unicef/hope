import BaseComponent from "../../base.component";

export default class NewFeedback extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  labelCategory = 'div[data-cy="label-Category"]';
  selectIssueType = 'div[data-cy="select-issueType"]';
  buttonCancel = 'a[data-cy="button-cancel"]';
  buttonBack = 'button[data-cy="button-back"]';
  buttonNext = 'button[data-cy="button-submit"]';
  // Texts
  textTitle = "New Feedback";
  textCategory = "Feedback";
  // Elements
  getTitlePage = () => cy.get(this.titlePage);
  getLabelCategory = () => cy.get(this.labelCategory);
  getSelectIssueType = () => cy.get(this.selectIssueType);
  getButtonCancel = () => cy.get(this.buttonCancel);
  getButtonBack = () => cy.get(this.buttonBack);
  getButtonNext = () => cy.get(this.buttonNext);

  checkElementsOnPage() {
    this.getTitlePage().contains(this.textTitle);
    this.getLabelCategory().contains(this.textCategory);
    this.getSelectIssueType().should("be.visible");
    this.getButtonCancel().should("be.visible");
    this.getButtonBack().should("be.visible");
    this.getButtonNext().should("be.visible");
  }
}
