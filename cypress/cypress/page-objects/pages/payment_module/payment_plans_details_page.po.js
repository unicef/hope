import BaseComponent from "../../base.component";

export default class ProgramPlanDetailsPage extends BaseComponent {
  // Locators
  tableTitle = 'h6[data-cy="table-title"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  labelReconciled = 'div[data-cy="label-Reconciled"]';
  labelNumberOfPayments = 'div[data-cy="label-Number of payments"]';
  chartContainer = 'div[data-cy="chart-container"]';
  labelPending = 'div[data-cy="label-Pending"]';
  labelUnsuccessful = 'div[data-cy="label-Unsuccessful"]';
  labelNotDelivered = 'div[data-cy="label-Not delivered"]';
  labelDeliveredPartially = 'div[data-cy="label-Delivered partially"]';
  labelDeliveredFully = 'div[data-cy="label-Delivered fully"]';
  dataCyDeliveredQuantityCell = 'div[data-cy="delivered-quantity-cell"]';
  buttonImport = 'button[data-cy="button-import"]';
  buttonDataCyButtonSetUpPaymentInstructions =
    'a[data-cy="button-set-up-payment-instructions"]';
  labelTargetedIndividuals = 'div[data-cy="label-Targeted Individuals"]';
  labelTotalNumberOfHouseholds =
    'div[data-cy="label-Total Number of Households"]';
  labelMaleAdults = 'div[data-cy="label-Male Adults"]';
  labelMaleChildren = 'div[data-cy="label-Male Children"]';
  labelFemaleAdults = 'div[data-cy="label-Female Adults"]';
  labelFemaleChildren = 'div[data-cy="label-Female Children"]';
  tooltip = 'div[data-cy="tooltip"]';
  inputExclusionReason = 'div[data-cy="input-exclusionReason"]';
  buttonSaveExclusions = 'button[data-cy="button-save-exclusions"]';
  buttonCancelExclusions = 'button[data-cy="button-cancel-exclusions"]';
  labelCashVasquezSexton = 'div[data-cy="label-Cash (Vasquez-Sexton)"]';
  labelCash = 'div[data-cy="label-Cash"]';
  buttonDataCyButtonExportXlsx = 'button[data-cy="button-export-xlsx"]';
  buttonApplySteficon = 'button[data-cy="button-apply-steficon"]';
  inputEntitlementFormula = 'div[data-cy="input-entitlement-formula"]';
  labelRelatedFollowUpPaymentPlans =
    'div[data-cy="label-Related Follow-Up Payment Plans"]';
  labelDispersionEndDate = 'div[data-cy="label-Dispersion End Date"]';
  labelDispersionStartDate = 'div[data-cy="label-Dispersion Start Date"]';
  labelEndDate = 'div[data-cy="label-End Date"]';
  labelStartDate = 'div[data-cy="label-Start Date"]';
  labelCurrency = 'div[data-cy="label-Currency"]';
  labelTargetPopulation = 'div[data-cy="label-Target Population"]';
  labelProgramme = 'div[data-cy="label-Programme"]';
  labelCreatedBy = 'div[data-cy="label-Created By"]';
  buttonDataCyButtonShow = 'button[data-cy="button-show"]';
  buttonExportXlsx = 'dibuttonv[data-cy="button-export-xlsx"]';
  statusContainer = 'div[data-cy="status-container"]';

  // Texts
  // Elements
  getTableTitle = () => cy.get(this.tableTitle);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);
  getLabelReconciled = () => cy.get(this.labelReconciled);
  getLabelNumberOfPayments = () => cy.get(this.labelNumberOfPayments);
  getChartContainer = () => cy.get(this.chartContainer);
  getLabelPending = () => cy.get(this.labelPending);
  getLabelUnsuccessful = () => cy.get(this.labelUnsuccessful);
  getLabelNotDelivered = () => cy.get(this.labelNotDelivered);
  getLabelDeliveredPartially = () => cy.get(this.labelDeliveredPartially);
  getLabelDeliveredFully = () => cy.get(this.labelDeliveredFully);
  getDataCyDeliveredQuantityCell = () =>
    cy.get(this.dataCyDeliveredQuantityCell);
  getButtonImport = () => cy.get(this.buttonImport);
  getButtonDataCyButtonSetUpPaymentInstructions = () =>
    cy.get(this.buttonDataCyButtonSetUpPaymentInstructions).scrollIntoView();
  getLabelTargetedIndividuals = () => cy.get(this.labelTargetedIndividuals);
  getLabelTotalNumberOfHouseholds = () =>
    cy.get(this.labelTotalNumberOfHouseholds);
  getLabelMaleAdults = () => cy.get(this.labelMaleAdults);
  getLabelMaleChildren = () => cy.get(this.labelMaleChildren);
  getLabelFemaleAdults = () => cy.get(this.labelFemaleAdults);
  getLabelFemaleChildren = () => cy.get(this.labelFemaleChildren);
  getTooltip = () => cy.get(this.tooltip);
  getInputExclusionReason = () => cy.get(this.inputExclusionReason);
  getButtonSaveExclusions = () => cy.get(this.buttonSaveExclusions);
  getButtonCancelExclusions = () => cy.get(this.buttonCancelExclusions);
  getLabelCashVasquezSexton = () => cy.get(this.labelCashVasquezSexton);
  getLabelCash = () => cy.get(this.labelCash);
  getButtonDataCyButtonExportXlsx = () =>
    cy.get(this.buttonDataCyButtonExportXlsx);
  getButtonApplySteficon = () => cy.get(this.buttonApplySteficon);
  getInputEntitlementFormula = () => cy.get(this.inputEntitlementFormula);
  getLabelRelatedFollowUpPaymentPlans = () =>
    cy.get(this.labelRelatedFollowUpPaymentPlans);
  getLabelDispersionEndDate = () => cy.get(this.labelDispersionEndDate);
  getLabelDispersionStartDate = () => cy.get(this.labelDispersionStartDate);
  getLabelEndDate = () => cy.get(this.labelEndDate);
  getLabelStartDate = () => cy.get(this.labelStartDate);
  getLabelCurrency = () => cy.get(this.labelCurrency);
  getLabelTargetPopulation = () => cy.get(this.labelTargetPopulation);
  getLabelProgramme = () => cy.get(this.labelProgramme);
  getLabelCreatedBy = () => cy.get(this.labelCreatedBy);
  getButtonDataCyButtonShow = () => cy.get(this.buttonDataCyButtonShow);
  getButtonExportXlsx = () => cy.get(this.buttonExportXlsx);
  getStatusContainer = () => cy.get(this.statusContainer);
}
