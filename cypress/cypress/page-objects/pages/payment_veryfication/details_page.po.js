import BaseComponent from "../../base.component";

export default class PVDetailsPage extends BaseComponent {
  // Locators
  paymentVerificationTitle = 'a[class="sc-kpOJdX bEMsyB"]';
  //data-cy='plan-link' data-cy='plan-id'
  createVerificationPlan = 'button[data-cy="button-new-plan"]';
  divPaymentDetails =
    'div[class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-9"]';
  //data-cy='div-payment-plan-details'
  gridPaymentDetails =
    'div[class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-4"]';
  //data-cy="grid-payment-plan-details"
  divBankReconciliation =
    'div[class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-3"]';
  //data-cy="grid-bank-reconciliation"
  divVerificationPlansSummary = 'div[class="sc-feJyhm GGSnz"]';
  //data-cy="grid-verification-plans-summary"
  tableTitle = 'h6[class="MuiTypography-root MuiTypography-h6"]';
  //data-cy="table-label"
  gridBankReconciliation =
    'div[class="MuiGrid-root MuiGrid-container MuiGrid-direction-xs-column"]';
  //data-cy='grid-bank-reconciliation'
  summaryStatus = 'div[data-cy="label-Status"]';
  //data-cy='verification-plans-summary-status'
  statusVP = 'div[data-cy="status-container"]';
  //data-cy='verification-plan-status'
  summaryActivationDate = 'div[data-cy="label-Activation Date"]';
  //data-cy="summary-activation-date"
  summaryCompletionDate = 'div[data-cy="label-Completion Date"]';
  //data-cy="summary-completion-date"
  summaryNumberOfPlans = 'div[data-cy="label-Number of Verification Plans"]';
  //data-cy="summary-number-of-plans"
  deletePlan = 'button[data-cy="button-delete-plan"]';
  deletePopUP = 'div[data-cy="dialog-actions-container"]';
  snackbarMessage = 'div[class="MuiSnackbarContent-message"]';
  activatePlan = 'button[data-cy="button-activate-plan"]';
  discardPlan = 'button[data-cy="button-discard-plan"]';
  finishPlan = 'button[data-cy="button-ed-plan"]';
  editVP = 'button[data-cy="button-new-plan"]';
  // Create Verification Plan
  cvp = 'div[aria-labelledby="form-dialog-title"]';
  //data-cy="dialog-title"
  cvpTabList = 'div[role="tablist"]';
  //data-cy="tabs"
  cvpTab = 'button[role="tab"]';
  cvpTitle = 'h2[class="MuiTypography-root MuiTypography-h6"]';
  cvpSubtitle = 'span[class="MuiTypography-root MuiTypography-caption"]';
  cvpSubmit = 'button[data-cy="button-submit"]';

  // Texts
  textTitle = "Payment Verification";
  textCreateVerificationPlan = "CREATE VERIFICATION PLAN";
  textProgrammeName = "PROGRAMME NAME";
  textProgrammeID = "PROGRAMME ID";
  textPaymentRecords = "PAYMENT RECORDS";
  textStartDate = "START DATE";
  textEndDate = "END DATE";
  textBankReconciliation = "Bank reconciliation";
  textSuccessful = "SUCCESSFUL";
  textErroneus = "ERRONEOUS";
  textVerificationPlansSummary = "Verification Plans Summary";
  textSummaryStatus = "Status";
  textSummaryActivationDate = "Activation Date";
  textSummaryCompletionDate = "Completion Date";
  textSummaryNumberOfPlans = "Number of Verification Plans";
  textCVPTitle = "Create Verification Plan";
  textCVPConfidenceInterval = "Confidence Interval";

  // Elements
  getPaymentVerificationTitle = () => cy.get(this.paymentVerificationTitle);
  getCreateVerificationPlan = () => cy.get(this.createVerificationPlan);
  getProgrammeName = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(0);
  getProgrammeID = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(1);
  getPaymentRecords = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(2);
  getStartDate = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(3);
  getEndDate = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(4);
  getBankReconciliationTitle = () =>
    cy.get(this.divBankReconciliation).get(this.tableTitle);
  getSuccessful = () =>
    cy
      .get(this.divBankReconciliation)
      .eq(0)
      .get(this.gridBankReconciliation)
      .get("div")
      .eq(0);
  getErroneus = () =>
    cy
      .get(this.divBankReconciliation)
      .eq(0)
      .get(this.gridBankReconciliation)
      .get("div")
      .eq(1);
  getVerificationPlansSummary = () =>
    cy.get(this.divVerificationPlansSummary).get(this.tableTitle);
  getStatus = () => cy.get(this.summaryStatus);
  getActivationDate = () => cy.get(this.summaryActivationDate);
  getCompletionDate = () => cy.get(this.summaryCompletionDate);
  getNumberOfPlans = () => cy.get(this.summaryNumberOfPlans);
  getDeletePlan = () => cy.get(this.deletePlan);
  getDelete = () => cy.get(this.deletePopUP).get(this.cvpSubmit);
  getSnackbarMessage = () => cy.get(this.snackbarMessage);
  getActivatePlan = () => cy.get(this.activatePlan);
  getActivate = () => cy.get(this.cvpSubmit);
  getDiscardPlan = () => cy.get(this.discardPlan);
  getDiscard = () => cy.get(this.cvpSubmit);
  getStatusVP = () => cy.get(this.statusVP);
  getFinishPlan = () => cy.get(this.finishPlan);
  getFinish = () => cy.get(this.cvpSubmit);
  getEditVP = () => cy.get(this.editVP);

  // Create Verification Plan
  getCVPTitle = () => cy.get(this.cvp).get(this.cvpTitle);
  getFullList = () => cy.get(this.cvp).get(this.cvpTab).eq(0);
  getRandomSampling = () => cy.get(this.cvp).get(this.cvpTab).eq(1);
  getCVPConfidenceInterval = () => cy.get(this.cvp).get(this.cvpSubtitle);
  getCVPSave = () => cy.get(this.cvp).get(this.cvpSubmit);

  checkPaymentVerificationTitle() {
    this.getPaymentVerificationTitle().contains(this.textTitle);
    this.getCreateVerificationPlan()
      .get("span")
      .contains(this.textCreateVerificationPlan);
  }

  checkGridPaymentDetails() {
    this.getProgrammeName().get("span").contains(this.textProgrammeName);
    this.getProgrammeID().get("span").contains(this.textProgrammeName);
    this.getPaymentRecords().get("span").contains(this.textProgrammeName);
    this.getStartDate().get("span").contains(this.textProgrammeName);
    this.getEndDate().get("span").contains(this.textProgrammeName);
  }

  checkBankReconciliationTitle() {
    this.getBankReconciliationTitle().contains(this.textBankReconciliation);
  }

  checkGridBankReconciliation() {
    this.getSuccessful().contains(this.textSuccessful);
    this.getErroneus().contains(this.textErroneus);
  }

  checkVerificationPlansSummaryTitle() {
    this.getVerificationPlansSummary().contains(
      this.textVerificationPlansSummary
    );
  }

  checkGridVerificationPlansSummary() {
    this.getStatus().prev().contains(this.textSummaryStatus);
    this.getActivationDate().prev().contains(this.textSummaryActivationDate);
    this.getCompletionDate().prev().contains(this.textSummaryCompletionDate);
    this.getNumberOfPlans().prev().contains(this.textSummaryNumberOfPlans);
  }

  checkCVPTitle() {
    this.getCVPTitle().contains(this.textCVPTitle);
  }

  checkVerificationPlan() {
    this.checkVerificationPlansSummaryTitle();
  }

  deleteVerificationPlan() {
    this.getDeletePlan().click();
    this.getDelete().click();
    this.getNumberOfPlans().contains(0);
  }

  discardVerificationPlan() {
    this.getDiscardPlan().click();
    this.getDiscard().click();
    this.getDeletePlan();
  }

  createNewVerificationPlan() {
    this.checkPaymentVerificationTitle();
    this.getNumberOfPlans().then(($el) => {
      if ($el.text() == "0") {
        this.getCreateVerificationPlan().click();
        this.checkCVPTitle();
        this.getRandomSampling().click();
        this.getCVPConfidenceInterval().contains(
          this.textCVPConfidenceInterval
        );
        this.getCVPSave().click();
        this.checkVerificationPlan();
      }
    });
  }
}
