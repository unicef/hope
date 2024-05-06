import BaseComponent from "../../base.component";

export default class ProgramManagement extends BaseComponent {
  // Locators
  buttonNewProgram = '[data-cy="button-new-program"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  dialogTitle = '[data-cy="page-header-title"]';
  inputProgrammeName = 'div[data-cy="input-programme-name"]';
  inputCashAssistScope = 'div[data-cy="input-cash-assist-scope"]';
  selectOptionUnicef = 'li[data-cy="select-option-Unicef"]';
  selectOptionForPartners = 'li[data-cy="select-option-For partners"]';
  inputSector = 'div[data-cy="input-sector"]';
  selectOptionX = 'li[data-cy="select-option-';
  inputStartDate = 'div[data-cy="input-start-date"]';
  inputEndDate = 'div[data-cy="input-end-date"]';
  inputDescription = 'div[data-cy="input-description"]';
  inputBudget = 'input[data-cy="input-budget"]';
  inputAdminArea = 'div[data-cy="input-admin-area"]';
  inputPopulationGoal = 'div[data-cy="input-population-goal"]';
  inputDataCollectingType = 'div[data-cy="input-data-collecting-type"]';
  buttonSave = 'button[data-cy="button-save"]';
  buttonNext = 'button[data-cy="button-next"]'
  statusFilter = 'div[data-cy="filters-status"]';
  option = ' li[role = "option"]';
  buttonApply = 'button[data-cy="button-filters-apply"]';
  statusContainer = 'div[data-cy="status-container"]';
  tableRowX = 'tr[data-cy="table-row-';
  inputFrequencyOfPayment = 'div[data-cy="input-frequency-of-payment"]';
  inputCashPlus = 'span[data-cy="input-cashPlus"]';
  selectDataCollectingTypeCode =
    'input[data-cy="select-dataCollectingTypeCode"]';
  // Texts

  // Elements
  getButtonNewProgram = () => cy.get(this.buttonNewProgram);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);
  getDialogTitle = () => cy.get(this.dialogTitle);

  getInputProgrammeName = () => cy.get(this.inputProgrammeName);
  getSelectOptionUnicef = () => cy.get(this.selectOptionUnicef);
  getSelectOptionForPartners = () => cy.get(this.selectOptionForPartners);
  getInputSector = () => cy.get(this.inputSector).first();
  getSelectOptionByName = (name) => cy.get(this.selectOptionX + name + '"]');
  getInputStartDate = () => cy.get(this.inputStartDate);
  getInputEndDate = () => cy.get(this.inputEndDate);
  getInputDescription = () => cy.get(this.inputDescription);
  getInputBudget = () => cy.get(this.inputBudget);

  getInputAdminArea = () => cy.get(this.inputAdminArea);
  getInputPopulationGoal = () => cy.get(this.inputPopulationGoal);
  getButtonSave = () => cy.get(this.buttonSave);
  getButtonNext = () => cy.get(this.buttonNext)
  getStatusFilter = () => cy.get(this.statusFilter);
  getOption = () => cy.get(this.option);
  getButtonApply = () => cy.get(this.buttonApply);
  getStatusContainer = () => cy.get(this.statusContainer);
  getInputFrequencyOfPayment = () => cy.get(this.inputFrequencyOfPayment);
  getInputCashPlus = () => cy.get(this.inputCashPlus).find("input");
  getTableRowByName = (name) => cy.get(this.tableRowX + name + '"]');
  getInputDataCollectingType = () =>
    cy.get(this.inputDataCollectingType).first();
  getSelectDataCollectingTypeCode = () =>
    cy.get(this.selectDataCollectingTypeCode);
}
