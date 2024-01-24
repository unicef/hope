from page_object.base_components import BaseComponents


class NewFeedback extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  labelCategory = 'div[data-cy="label-Category"]';
  selectIssueType = 'div[data-cy="select-issueType"]';
  issueType = 'div[data-cy="label-Issue Type"]';
  inputIssueType = 'div[data-cy="input-issue-type"]';
  buttonCancel = 'a[data-cy="button-cancel"]';
  buttonBack = 'button[data-cy="button-back"]';
  buttonNext = 'button[data-cy="button-submit"]';
  option = 'li[role="option"]';
  householdTableRow = 'tr[data-cy="household-table-row"]';
  individualTableRow = 'tr[data-cy="individual-table-row"';
  lookUpTabs = 'button[role="tab"]';
  receivedConsent = 'span[data-cy="input-consent"]';
  description = 'textarea[data-cy="input-description"]';
  comments = 'textarea[data-cy="input-comments"]';
  adminAreaAutocomplete = 'div[data-cy="input-admin2"]';
  inputLanguage = 'textarea[data-cy="input-language"]';
  inputArea = 'input[data-cy="input-area"]';

  // Texts
  textTitle = "New Feedback";
  textCategory = "Feedback";
  textLookUpHousehold = "LOOK UP HOUSEHOLD";
  textLookUpIndividual = "LOOK UP INDIVIDUAL";
  // Elements
  getTitlePage = () => cy.get(this.titlePage);
  getLabelCategory = () => cy.get(this.labelCategory);
  getSelectIssueType = () => cy.get(this.selectIssueType);
  getButtonCancel = () => cy.get(this.buttonCancel);
  getButtonBack = () => cy.get(this.buttonBack);
  getButtonNext = () => cy.get(this.buttonNext);
  getOption = () => cy.get(this.option);
  getHouseholdTab = () =>
    cy.get(this.lookUpTabs).contains(this.textLookUpHousehold);
  getLookUpIndividual = () =>
    cy.get(this.lookUpTabs).contains(this.textLookUpIndividual);
  getHouseholdTableRows = (number) => cy.get(this.householdTableRow).eq(number);
  getIndividualTableRow = (number) =>
    cy.get(this.individualTableRow).eq(number);

  getReceivedConsent = () => cy.get(this.receivedConsent);
  getDescription = () => cy.get(this.description);
  getComments = () => cy.get(this.comments);
  getInputLanguage = () => cy.get(this.inputLanguage);
  getInputArea = () => cy.get(this.inputArea);
  getAdminAreaAutocomplete = () => cy.get(this.adminAreaAutocomplete);
  getIssueType = () => cy.get(this.issueType);
  getInputIssueType = () => cy.get(this.inputIssueType);

  checkElementsOnPage() {
    this.getTitlePage().contains(this.textTitle);
    this.getLabelCategory().contains(this.textCategory);
    this.getSelectIssueType().should("be.visible");
    this.getButtonCancel().should("be.visible");
    this.getButtonBack().should("be.visible");
    this.getButtonNext().should("be.visible");
  }

  chooseOptionByName(name) {
    this.getSelectIssueType().click();
    this.getOption().contains(name).click();
  }
}
