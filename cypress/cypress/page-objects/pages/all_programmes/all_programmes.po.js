import BaseComponent from "../../base.component";

export default class AllProgrammes extends BaseComponent {
  // Locators
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  buttonNewProgram = 'button[data-cy="button-new-program"]';
  filtersSearch = 'div[data-cy="filters-search"]';
  filtersStatus = 'div[data-cy="filters-status"]';
  filtersStartDate = 'div[data-cy="filters-start-date"]';
  filtersEndDate = 'div[data-cy="filters-end-date"]';
  filtersSector = 'div[data-cy="filters-sector"]';
  filtersNumberOfHouseholdsMin =
    'div[data-cy="filters-number-of-households-min"]';
  filtersNumberOfHouseholdsMax =
    'div[data-cy="filters-number-of-households-max"]';
  filtersBudgetMin = 'div[data-cy="filters-budget-min"]';
  filtersBudgetMax = 'div[data-cy="filters-budget-max"]';
  buttonClear = 'button[data-cy="button-filters-clear"]';
  buttonApply = 'button[data-cy="button-filters-apply"]';
  tabTitle = 'h6[data-cy="table-title"]';
  tableColumns = 'span[data-cy="table-label"]';
  rows = 'tr[role="checkbox"]';

  // Texts
  textAllProgrammes = "All Programmes";
  textPageHeaderTitle = "Programme Management";
  textProgrammes = "Programmes";

  // Elements
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);
  getButtonNewProgram = () => cy.get(this.buttonNewProgram);
  getFiltersSearch = () => cy.get(this.filtersSearch);
  getFiltersStatus = () => cy.get(this.filtersStatus);
  getFiltersStartDate = () => cy.get(this.filtersStartDate);
  getFiltersEndDate = () => cy.get(this.filtersEndDate);
  getFiltersSector = () => cy.get(this.filtersSector);
  getFiltersNumberOfHouseholdsMin = () =>
    cy.get(this.filtersNumberOfHouseholdsMin);
  getFiltersNumberOfHouseholdsMax = () =>
    cy.get(this.filtersNumberOfHouseholdsMax);
  getFiltersBudgetMin = () => cy.get(this.filtersBudgetMin);
  getFiltersBudgetMax = () => cy.get(this.filtersBudgetMax);
  getButtonClear = () => cy.get(this.buttonClear);
  getButtonApply = () => cy.get(this.buttonApply);
  getTabTitle = () => cy.get(this.tabTitle);
  getName = () => cy.get(this.tableColumns).eq(0);
  getStatus = () => cy.get(this.tableColumns).eq(1);
  getTimeframe = () => cy.get(this.tableColumns).eq(2);
  getSelector = () => cy.get(this.tableColumns).eq(3);
  getNumOfouseholds = () => cy.get(this.tableColumns).eq(4);
  getBudget = () => cy.get(this.tableColumns).eq(5);
  getProgrammesRows = () => cy.get(this.rows);
}
