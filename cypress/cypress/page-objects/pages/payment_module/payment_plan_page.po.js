import BaseComponent from "../../base.component";

export default class PaymentPlanPage extends BaseComponent {
  // Locators
  tableLabel = 'span[data-cy="table-label"]';
  statusContainer = 'div[data-cy="status-container"]';
  tableTitle = 'h6[data-cy="table-title"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  paymentPlanRow = 'tr[class="MuiTableRow-root sc-fMiknA fHXcHH"]';
  buttonFiltersClear = 'button[data-cy="button-filters-clear"]';
  buttonFiltersApply = 'button[data-cy="button-filters-apply"]';
  buttonNewPaymentPlan = 'a[data-cy="button-new-payment-plan"]';

  // Texts
  // Elements
  getTableLabel = () => cy.get(this.tableLabel);
  getStatusContainer = () => cy.get(this.statusContainer);
  getTableTitle = () => cy.get(this.tableTitle);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);
  getPaymentPlanRow = () => cy.get(this.paymentPlanRow);
  getButtonFiltersClear = () => cy.get(this.buttonFiltersClear);
  getButtonFiltersApply = () => cy.get(this.buttonFiltersApply);
  getButtonNewPaymentPlan = () => cy.get(this.buttonNewPaymentPlan);
  getButtonFiltersClear = () => cy.get(this.buttonFiltersClear);
  getButtonFiltersApply = () => cy.get(this.buttonFiltersApply);
}
