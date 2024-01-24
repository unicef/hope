from page_object.base_components import BaseComponents


class PopulationHouseholds extends BaseComponent {
  // Locators
  householdTableRow = 'tr[data-cy="household-table-row"]';
  statusContainer = 'div[data-cy="status-container"]';
  householdId = 'th[data-cy="household-id"]';
  labelStatus = 'th[data-cy="status"]';
  householdHeadName = 'th[data-cy="household-head-name"]';
  householdSize = 'th[data-cy="household-size"]';
  householdLocation = 'th[data-cy="household-location"]';
  householdResidenceStatus = 'th[data-cy="household-residence-status"]';
  householdTotalCashReceived = 'th[data-cy="household-total-cash-received"]';
  householdRegistrationDate = 'th[data-cy="household-registration-date"]';
  tableTitle = 'h6[data-cy="table-title"]';
  buttonFiltersApply = 'button[data-cy="button-filters-apply"]';
  buttonFiltersClear = 'button[data-cy="button-filters-clear"]';
  hhFiltersStatus = 'div[data-cy="hh-filters-status"]';
  hhFiltersOrderBy = 'div[data-cy="hh-filters-order-by"]';
  hhFiltersHouseholdSizeTo = 'div[data-cy="hh-filters-household-size-to"]';
  hhFiltersHouseholdSizeFrom = 'div[data-cy="hh-filters-household-size-from"]';
  hhFiltersResidenceStatus = 'div[data-cy="hh-filters-residence-status"]';
  filterSearchType = 'div[data-cy="filter-search-type"]';
  filterSearchType1 = 'div[data-cy="filter-search-type"]';
  hhFiltersSearch = 'div[data-cy="hh-filters-search"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  // ToDo: Add data-cy
  filterAdminLevel2 = "brak";

  // Texts
  textTitle = "Households";
  // Elements
  getHouseholdTableRow = () => cy.get(this.householdTableRow);
  getStatusContainer = () => cy.get(this.statusContainer);
  getHouseholdId = () => cy.get(this.householdId);
  getLabelStatus = () => cy.get(this.labelStatus);
  getHouseholdHeadName = () => cy.get(this.householdHeadName);
  getHouseholdSize = () => cy.get(this.householdSize);
  getHouseholdLocation = () => cy.get(this.householdLocation);
  getHouseholdResidenceStatus = () => cy.get(this.householdResidenceStatus);
  getHouseholdTotalCashReceived = () => cy.get(this.householdTotalCashReceived);
  getHouseholdRegistrationDate = () => cy.get(this.householdRegistrationDate);
  getTableTitle = () => cy.get(this.tableTitle);
  getButtonFiltersApply = () => cy.get(this.buttonFiltersApply);
  getButtonFiltersClear = () => cy.get(this.buttonFiltersClear);
  getHhFiltersStatus = () => cy.get(this.hhFiltersStatus);
  getHhFiltersOrderBy = () => cy.get(this.hhFiltersOrderBy);
  getHhFiltersHouseholdSizeTo = () => cy.get(this.hhFiltersHouseholdSizeTo);
  getHhFiltersHouseholdSizeFrom = () => cy.get(this.hhFiltersHouseholdSizeFrom);
  getHhFiltersResidenceStatus = () => cy.get(this.hhFiltersResidenceStatus);
  getFilterSearchType = () => cy.get(this.filterSearchType);
  getFilterSearchType1 = () => cy.get(this.filterSearchType1);
  getHhFiltersSearch = () => cy.get(this.hhFiltersSearch);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);

  checkElementsOnPage() {
    this.getHouseholdTableRow().should("be.visible");
    this.getStatusContainer().should("be.visible");
    this.getHouseholdId().should("be.visible");
    this.getLabelStatus().should("be.visible");
    this.getHouseholdHeadName().should("be.visible");
    this.getHouseholdSize().should("be.visible");
    this.getHouseholdLocation().should("be.visible");
    this.getHouseholdResidenceStatus().should("be.visible");
    this.getHouseholdTotalCashReceived().should("be.visible");
    this.getHouseholdRegistrationDate().should("be.visible");
    this.getTableTitle().should("be.visible");
    this.getButtonFiltersApply().should("be.visible");
    this.getButtonFiltersClear().should("be.visible");
    this.getHhFiltersStatus().should("be.visible");
    this.getHhFiltersOrderBy().should("be.visible");
    this.getHhFiltersHouseholdSizeTo().should("be.visible");
    this.getHhFiltersHouseholdSizeFrom().should("be.visible");
    this.getHhFiltersResidenceStatus().should("be.visible");
    this.getFilterSearchType().should("be.visible");
    this.getFilterSearchType1().should("be.visible");
    this.getHhFiltersSearch().should("be.visible");
    this.getPageHeaderTitle().should("be.visible");
  }
  clickNavHouseholds() {
    this.getMenuButtonProgrammePopulation().click();
    this.getMenuButtonHouseholds().should("be.visible");
    this.getMenuButtonHouseholds().click();
  }
}
