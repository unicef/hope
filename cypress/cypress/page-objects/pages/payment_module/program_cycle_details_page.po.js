import BaseComponent from "../../base.component";

export default class ProgramCycleDetailsPage extends BaseComponent {
  // Locators
  tableTitle = 'h6[data-cy="table-title"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  buttonCreatePaymentPlan = 'a[data-cy="button-create-payment-plan"]';
  statusContainer = 'div[data-cy="status-container"]';
  labelCreatedBy = 'div[data-cy="label-Created By"]';
  labelStartDate = 'div[data-cy="label-Start Date"]';
  labelEndDate = 'div[data-cy="label-End Date"]';
  labelProgrammeStartDate = 'div[data-cy="label-Programme Start Date"]';
  labelProgrammeEndDate = 'div[data-cy="label-Programme End Date"]';
  labelFrequencyOfPayment = 'div[data-cy="label-Frequency of Payment"]';

  buttonFiltersClear = 'button[data-cy="button-filters-clear"]';
  buttonFiltersApply = 'button[data-cy="button-filters-apply"]';

  // Texts
  // Elements
  getTableTitle = () => cy.get(this.tableTitle);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);

  getButtonCreatePaymentPlan = () => cy.get(this.buttonCreatePaymentPlan);
  getStatusContainer = () => cy.get(this.statusContainer);
  getLabelCreatedBy = () => cy.get(this.labelCreatedBy);
  getLabelStartDate = () => cy.get(this.labelStartDate);
  getLabelEndDate = () => cy.get(this.labelEndDate);
  getLabelProgrammeStartDate = () => cy.get(this.labelProgrammeStartDate);
  getLabelProgrammeEndDate = () => cy.get(this.labelProgrammeEndDate);
  getLabelFrequencyOfPayment = () => cy.get(this.labelFrequencyOfPayment);
  getButtonFiltersClear = () => cy.get(this.buttonFiltersClear);
  getButtonFiltersApply = () => cy.get(this.buttonFiltersApply);
}
