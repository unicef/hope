import BaseComponent from "../../base.component";

export default class FeedbackDetailsPage extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  buttonEdit = 'a[data-cy="button-edit"]';
  labelCategory = 'div[data-cy="label-Category"]';
  labelIssueType = 'div[data-cy="label-Issue Type"]';
  labelHouseholdID = 'div[data-cy="label-Household ID"]';
  labelIndividualID = 'div[data-cy="label-Individual ID"]';
  labelCreatedBy = 'div[data-cy="label-Created By"]';
  labelDateCreated = 'div[data-cy="label-Date Created"]';
  labelLastModifiedDate = 'div[data-cy="label-Last Modified Date"]';
  labelAdministrativeLevel2 = 'div[data-cy="label-Administrative Level 2"]';
  labelAreaVillagePayPoint = 'div[data-cy="label-Area / Village / Pay point"]';
  labelLanguagesSpoken = 'div[data-cy="label-Languages Spoken"  ]';
  labelDescription = 'div[data-cy="label-Description"]';
  labelComments = 'div[data-cy="label-Comments"]';
  // Texts
  textTitle = "Feedback ID: ";
  textCategory = "Feedback";
  textIssueType = "Negative Feedback";
  textDescription = "Negative Feedback";
  // Elements
  getTitlePage = () => cy.get(this.titlePage);
  getButtonEdit = () => cy.get(this.buttonEdit);
  getCategory = () => cy.get(this.labelCategory);
  getIssueType = () => cy.get(this.labelIssueType);
  getHouseholdID = () => cy.get(this.labelHouseholdID);
  getIndividualID = () => cy.get(this.labelIndividualID);
  getCreatedBy = () => cy.get(this.labelCreatedBy);
  getDateCreated = () => cy.get(this.labelDateCreated);
  getLastModifiedDate = () => cy.get(this.labelLastModifiedDate);
  getAdministrativeLevel2 = () => cy.get(this.labelAdministrativeLevel2);
  getAreaVillagePayPoint = () => cy.get(this.labelAreaVillagePayPoint);
  getLanguagesSpoken = () => cy.get(this.labelLanguagesSpoken);
  getDescription = () => cy.get(this.labelDescription);
  getComments = () => cy.get(this.labelComments);
  checkElementsOnPage() {
    this.getTitlePage().contains(this.textTitle);
    this.getButtonEdit().should("be.visible");
    this.getCategory().contains(this.textCategory);
    this.getIssueType().contains(this.textIssueType);
    this.getHouseholdID().should("be.visible");
    this.getIndividualID().should("be.visible");
    this.getCreatedBy().should("be.visible");
    this.getDateCreated().should("be.visible");
    this.getLastModifiedDate().should("be.visible");
    this.getAdministrativeLevel2().should("be.visible");
    this.getAreaVillagePayPoint().should("be.visible");
    this.getLanguagesSpoken().should("be.visible");
    this.getDescription().contains(this.textDescription);
    this.getComments().should("be.visible");
  }
}
