import BaseComponent from "../../base.component";

export default class PVDetailsPage extends BaseComponent {
  // Locators
  paymentVerificationTitle = 'h5[data-cy="page-header-title"]';
  createVerificationPlan = 'button[data-cy="button-new-plan"]';
  divPaymentDetails = 'div[data-cy="div-payment-plan-details"]';
  gridPaymentDetails = 'div[data-cy="grid-payment-plan-details"]';
  divBankReconciliation = 'div[data-cy="grid-bank-reconciliation"]';
  divVerificationPlansSummary =
    'div[data-cy="grid-verification-plans-summary"]';
  tableTitle = 'h6[data-cy="table-label"]';
  gridBankReconciliation = 'div[data-cy="grid-bank-reconciliation"]';
  summaryStatus = 'div[data-cy="verification-plans-summary-status"]';
  statusVP = 'div[data-cy="verification-plan-status"]';
  summaryActivationDate =
    'div[data-cy="labelized-field-container-summary-activation-date"]';
  summaryCompletionDate =
    'div[data-cy="labelized-field-container-summary-completion-date"]';
  summaryNumberOfPlans =
    'div[data-cy="labelized-field-container-summary-number-of-plans"]';
  deletePlan = 'button[data-cy="button-delete-plan"]';
  deletePopUP = 'div[data-cy="dialog-actions-container"]';
  activatePlan = 'button[data-cy="button-activate-plan"]';
  discardPlan = 'button[data-cy="button-discard-plan"]';
  finishPlan = 'button[data-cy="button-ed-plan"]';
  editVP = 'button[data-cy="button-new-plan"]';
  // Create Verification Plan
  cvp = 'div[data-cy="dialog-title"]';
  cvpTabList = 'div[data-cy="tabs"]';
  cvpTab = 'button[role="tab"]';
  cvpTitle = 'div[data-cy="dialog-title"]';
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
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails);
  getProgrammeID = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails);
  getPaymentRecords = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails);
  getStartDate = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails);
  getEndDate = () =>
    cy.get(this.divPaymentDetails).get(this.gridPaymentDetails);
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
    this.getPaymentVerificationTitle().should("be.visible");
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
    this.getStatus().get("span").contains(this.textSummaryStatus);
    this.getActivationDate().contains(this.textSummaryActivationDate);
    this.getCompletionDate().contains(this.textSummaryCompletionDate);
    this.getNumberOfPlans().contains(this.textSummaryNumberOfPlans);
  }

  checkCVPTitle() {
    this.getCVPTitle().contains(this.textCVPTitle);
  }

  checkVerificationPlan() {
    this.checkVerificationPlansSummaryTitle();
  }

  deleteVerificationPlan(num = 0) {
    this.getDeletePlan().click();
    this.getDelete().click();
    this.getNumberOfPlans().contains(num);
  }

  discardVerificationPlan(num = 0) {
    this.getDiscardPlan().eq(num).click();
    this.getDiscard().click();
    this.getDeletePlan();
  }

  createNewVerificationPlan(num = 0) {
    this.checkPaymentVerificationTitle();
    this.getNumberOfPlans().then(($el) => {
      if ($el.find("div").text() === num.toString()) {
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
