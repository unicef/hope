import BaseComponent from "../../base.component";

export default class SurveysPage extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  rows = 'tr[role="checkbox"]';

  // Texts

  textTitlePage = "Surveys";
  textNewSurvey = "New Survey";
  textTargetPopulationFilter = "Target Population";
  textTabCreatedBy = "Created by";
  buttonApply = 'button[data-cy="button-filters-apply"]';
  buttonClear = 'button[data-cy="button-filters-clear"]';

  // Elements

  getTitlePage = () => cy.get(this.titlePage);
  getMessageID = () => cy.get(this.tabColumnLabel).eq(0);
  getApply = () => cy.get(this.buttonApply);
  getClear = () => cy.get(this.buttonClear);
  getTargetPopulationsRows = () => cy.get(this.rows);

  checkElementsOnPage() {
    this.getTitlePage().should("be.visible").contains(this.textTitlePage);
  }
}
