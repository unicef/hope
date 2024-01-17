import BaseComponent from "../../base.component";

export default class ProgramDetails extends BaseComponent {
  // Locators
  buttonActivateProgram = 'button[data-cy="button-activate-program"]';
  buttonRemoveProgram = 'button[data-cy="button-remove-program"]';
  buttonEditProgram = '[data-cy="button-edit-program"]';
  buttonCopyProgram = '[data-cy="button-copy-program"]';
  buttonFinishProgram = 'button[data-cy="button-finish-program"]';
  dialogPopupActivate = 'div[data-cy="dialog-actions-container"]';
  buttonDataCyButtonReactivateProgram =
    'button[data-cy="button-reactivate-program"]';
  buttonDataCyButtonReactivateProgramPopup =
    'button[data-cy="button-reactivate-program-popup"]';
  labelTotalNumberOfHouseholds =
    'div[data-cy="label-Total Number of Households"]';
  labelCASH = 'div[data-cy="label-CASH+"]';
  labelDescription = 'div[data-cy="label-Description"]';
  labelAdministrativeAreasOfImplementation =
    'div[data-cy="label-Administrative Areas of implementation"]';
  labelFrequencyOfPayment = 'div[data-cy="label-Frequency of Payment"]';
  labelScope = 'div[data-cy="label-Scope"]';
  labelSector = 'div[data-cy="label-Sector"]';
  labelENDDATE = 'div[data-cy="label-END DATE"]';
  labelSTARTDATE = 'div[data-cy="label-START DATE"]';
  statusContainer = 'div[data-cy="status-container"]';
  labelStatus = 'div[data-cy="label-status"]';
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';

  tablePagination = 'div[data-cy="table-pagination"]';
  cashPlanTableRow = 'tr[data-cy="cash-plan-table-row"]';
  tableLabel = 'span[data-cy="table-label"]';
  tableTitle = 'h6[data-cy="table-title"]';
  buttonActivateProgramModal =
    'button[data-cy="button-activate-program-modal"]';

  // Texts

  // Elements
  getButtonActivateProgram = () => cy.get(this.buttonActivateProgram);
  getButtonRemoveProgram = () => cy.get(this.buttonRemoveProgram);
  getButtonEditProgram = () => cy.get(this.buttonEditProgram);
  getButtonCopyProgram = () => cy.get(this.buttonCopyProgram);
  getButtonFinishProgram = () => cy.get(this.buttonFinishProgram);
  getDialogPopupActivate = () => cy.get(this.dialogPopupActivate);
  getLabelTotalNumberOfHouseholds = () =>
    cy.get(this.labelTotalNumberOfHouseholds);
  getLabelCASH = () => cy.get(this.labelCASH);
  getLabelDescription = () => cy.get(this.labelDescription);
  getLabelAdministrativeAreasOfImplementation = () =>
    cy.get(this.labelAdministrativeAreasOfImplementation);
  getLabelFrequencyOfPayment = () => cy.get(this.labelFrequencyOfPayment);
  getLabelScope = () => cy.get(this.labelScope);
  getLabelSector = () => cy.get(this.labelSector);
  getLabelENDDATE = () => cy.get(this.labelENDDATE);
  getLabelSTARTDATE = () => cy.get(this.labelSTARTDATE);
  getStatusContainer = () => cy.get(this.statusContainer);
  getLabelStatus = () => cy.get(this.labelStatus);
  getPageHeaderTitle = () => cy.get(this.pageHeaderTitle);
  getTablePagination = () => cy.get(this.tablePagination);
  getCashPlanTableRow = () => cy.get(this.cashPlanTableRow);
  getTableLabel = () => cy.get(this.tableLabel);
  getTableTitle = () => cy.get(this.tableTitle);
  getButtonActivateProgramModal = () => cy.get(this.buttonActivateProgramModal);
  getButtonDataCyButtonReactivateProgram = () =>
    cy.get(this.buttonDataCyButtonReactivateProgram);
  getButtonDataCyButtonReactivateProgramPopup = () =>
    cy.get(this.buttonDataCyButtonReactivateProgramPopup);
}
