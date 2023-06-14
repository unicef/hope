import BaseComponent from "../../base.component";

export default class Targeting extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  searchFilter = 'div[data-cy="filters-search"]';
  statusFilter = 'div[data-cy="filters-status"]';
  programFilter = 'div[data-cy="filters-program"]';
  minNumberOfHouseholds = 'div[data-cy="filters-num-individuals-min"]';
  maxNumberOfHouseholds = 'div[data-cy="filters-num-individuals-max"]';
  buttonCreateNew = 'div[data-cy="button-target-population-create-new"]';
  tabTitle = 'h6[data-cy="table-title"]';
  tabColumnLabel = 'span[data-cy="table-label"]';

  // Texts

  textTitlePage = "Targeting";

  // Elements

  getTitlePage = () => cy.get(this.titlePage);
  getSearchFilter = () => cy.get(this.searchFilter);
  getStatusFilter = () => cy.get(this.statusFilter);
  getProgramFilter = () => cy.get(this.programFilter);
  getMinNumberOfHouseholdsFilter = () => cy.get(this.minNumberOfHouseholds);
  getMaxNumberOfHouseholdsFilter = () => cy.get(this.maxNumberOfHouseholds);
  getButtonCreateNew = () => cy.get(this.buttonCreateNew);
  getTabTitle = () => cy.get(this.tabTitle);
  // getTabColumnLabel = () => cy.get(this.tabColumnLabel);

  checkElementsOnPage() {
    cy.get(this.getTitlePage).contains(this.textTitlePage);
    cy.get(this.getSearchFilter).contains(this.textTitlePage);
    cy.get(this.getStatusFilter).contains(this.textTitlePage);
    cy.get(this.getProgramFilter).contains(this.textTitlePage);
    cy.get(this.getMinNumberOfHouseholdsFilter).contains(this.textTitlePage);
    cy.get(this.getMaxNumberOfHouseholdsFilter).contains(this.textTitlePage);
    cy.get(this.getButtonCreateNew).contains(this.textTitlePage);
    cy.get(this.getTabTitle).contains(this.textTitlePage);
  }
}
