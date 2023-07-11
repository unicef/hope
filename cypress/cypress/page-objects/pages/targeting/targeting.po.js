import BaseComponent from "../../base.component";

export default class Targeting extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  searchFilter = 'div[data-cy="filters-search"]';
  statusFilter = 'div[data-cy="filters-status"]';
  minNumberOfHouseholds = 'div[data-cy="filters-num-individuals-min"]';
  maxNumberOfHouseholds = 'div[data-cy="filters-num-individuals-max"]';
  buttonCreateNew = 'a[data-cy="button-target-population-create-new"]';
  tabTitle = 'h6[data-cy="table-title"]';
  tabColumnLabel = 'span[data-cy="table-label"]';
  statusOptions = 'li[role="option"]';
  rows = 'tr[role="checkbox"]';

  // Texts

  textTitlePage = "Targeting";
  textCreateNew = "Create new";
  textTabTitle = "Target Populations";
  textTabName = "Name";
  textTabStatus = "Status";
  textTabProgramme = "Programme";
  textTabNOHouseholds = "Num. of Households";
  textTabDateCreated = "Date Created";
  textTabLastEdited = "Last Edited";
  textTabCreatedBy = "Created by";
  buttonApply = 'button[data-cy="button-filters-apply"]';

  // Elements

  getTitlePage = () => cy.get(this.titlePage);
  getSearchFilter = () => cy.get(this.searchFilter);
  getStatusFilter = () => cy.get(this.statusFilter);
  getMinNumberOfHouseholdsFilter = () => cy.get(this.minNumberOfHouseholds);
  getMaxNumberOfHouseholdsFilter = () => cy.get(this.maxNumberOfHouseholds);
  getButtonCreateNew = () => cy.get(this.buttonCreateNew);
  getTabTitle = () => cy.get(this.tabTitle);
  getTabColumnName = () => cy.get(this.tabColumnLabel).eq(0);
  getTabColumnStatus = () => cy.get(this.tabColumnLabel).eq(1);
  getTabColumnProgramme = () => cy.get(this.tabColumnLabel).eq(2);
  getTabColumnNOHouseholds = () => cy.get(this.tabColumnLabel).eq(3);
  getTabColumnDateCreated = () => cy.get(this.tabColumnLabel).eq(4);
  getTabColumnLastEdited = () => cy.get(this.tabColumnLabel).eq(5);
  getTabColumnCreatedBy = () => cy.get(this.tabColumnLabel).eq(6);
  getStatusOption = () => cy.get(this.statusOptions);
  getApply = () => cy.get(this.buttonApply);
  getTargetPopulationsRows = () => cy.get(this.rows);

  checkElementsOnPage() {
    this.getTitlePage().should("be.visible").contains(this.textTitlePage);
    this.getSearchFilter().should("be.visible");
    this.getStatusFilter().should("be.visible");
    this.getMinNumberOfHouseholdsFilter().should("be.visible");
    this.getMaxNumberOfHouseholdsFilter().should("be.visible");
    this.getButtonCreateNew().should("be.visible").contains(this.textCreateNew);
    this.getTabTitle().should("be.visible").contains(this.textTabTitle);
    this.getTabColumnName().should("be.visible").contains(this.textTabName);
    this.getTabColumnStatus().should("be.visible").contains(this.textTabStatus);
    this.getTabColumnProgramme().should("be.visible").contains(this.textTabProgramme);
    this.getTabColumnNOHouseholds()
      .should("be.visible")
      .contains(this.textTabNOHouseholds);
    this.getTabColumnDateCreated()
      .scrollIntoView()
      .should("be.visible")
      .contains(this.textTabDateCreated);
    this.getTabColumnLastEdited()
      .scrollIntoView()
      .should("be.visible")
      .contains(this.textTabLastEdited);
    this.getTabColumnCreatedBy()
      .scrollIntoView()
      .should("be.visible")
      .contains(this.textTabCreatedBy);
  }

  selectStatus(status) {
    this.getStatusFilter().click();
    this.getStatusOption().contains(status).click();
    this.pressEscapeFromElement(this.getStatusOption().contains(status));
    this.getApply().click();
  }

  chooseTargetPopulationRow(row) {
    return this.getTargetPopulationsRows().eq(row);
  }
}
