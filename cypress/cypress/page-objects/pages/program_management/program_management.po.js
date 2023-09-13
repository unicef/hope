import BaseComponent from "../../base.component";

export default class ProgramManagement extends BaseComponent {
  // Locators
  buttonNewProgram = 'button[data-cy="button-new-program"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  dialogTitle = 'h6[data-cy="dialog-title"]';
  inputProgrammeName = 'div[data-cy="input-programme-name"]';
  inputCashAssistScope = 'div[data-cy="input-cash-assist-scope"]';
  selectOptionUnicef = 'li[data-cy="select-option-Unicef"]';
  inputSector = 'div[data-cy="input-sector"]';
  selectOptionMultiPurpose = 'li[data-cy="select-option-Multi Purpose"]';
  inputStartDate = 'div[data-cy="input-start-date"]';
  inputEndDate = 'div[data-cy="input-end-date"]';
  inputDescription = 'div[data-cy="input-description"]';
  inputBudget = 'input[data-cy="input-budget"]';
  inputAdminArea = 'div[data-cy="input-admin-area"]';
  inputPopulationGoal = 'div[data-cy="input-population-goal"]';
  buttonSave = 'button[data-cy="button-save"]';
  // Texts

  // Elements
  getButtonNewProgram = () => cy.get(this.buttonNewProgram);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);
  getDialogTitle = () => cy.get(this.dialogTitle);

  getInputProgrammeName = () => cy.get(this.inputProgrammeName);
  getInputCashAssistScope = () => cy.get(this.inputCashAssistScope);
  getSelectOptionUnicef = () => cy.get(this.selectOptionUnicef);
  getInputSector = () => cy.get(this.inputSector);
  getSelectOptionMultiPurpose = () => cy.get(this.selectOptionMultiPurpose);
  getInputStartDate = () => cy.get(this.inputStartDate);
  getInputEndDate = () => cy.get(this.inputEndDate);
  getInputDescription = () => cy.get(this.inputDescription);
  getInputBudget = () => cy.get(this.inputBudget);

  getInputAdminArea = () => cy.get(this.inputAdminArea);
  getInputPopulationGoal = () => cy.get(this.inputPopulationGoal);
  getButtonSave = () => cy.get(this.buttonSave);
}
