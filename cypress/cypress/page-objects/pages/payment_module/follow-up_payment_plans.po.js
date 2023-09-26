import BaseComponent from "../../base.component";

export default class FollowUpPage extends BaseComponent {
  // Locators
  programCycleTableRow = 'tr[data-cy="program-cycle-table-row"]';
  tableLabel = 'span[data-cy="table-label"]';
  tableTitle = 'h6[data-cy="table-title"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  buttonNewPaymentPlan = 'a[data-cy="button-new-payment-plan"]';
  buttonFiltersClear = 'button[data-cy="button-filters-clear"]';
  buttonFiltersApply = 'button[data-cy="button-filters-apply"]';

  // Texts

  // Elements
  getProgramCycleTableRow = () => cy.get(this.programCycleTableRow);
  getTableLabel = () => cy.get(this.tableLabel);
  getTableTitle = () => cy.get(this.tableTitle);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);
  getButtonNewPaymentPlan = () => cy.get(this.buttonNewPaymentPlan);
}
