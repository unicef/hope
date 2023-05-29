import BaseComponent from '../../base.component';

export default class PVDetailsPage extends BaseComponent {

    // Locators
    paymentVerificationTitle = 'a[class="sc-kpOJdX bEMsyB"]'
    createVerificationPlan = 'button[data-cy="button-new-plan"]'
    divPaymentDetails = 'div[class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-9"]'
    gridPaymentDetails = 'div[class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-4"]'
    divBankReconciliation = 'div[class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-3"]'
    divVerificationPlansSummary = 'div[class="sc-feJyhm GGSnz"]'
    tableTitle = 'h6[class="MuiTypography-root MuiTypography-h6"]'
    gridBankReconciliation = 'div[class="MuiGrid-root MuiGrid-container MuiGrid-direction-xs-column"]'

    // Texts
    textTitle = "Payment Verification"
    textCreateVerificationPlan = "CREATE VERIFICATION PLAN"
    textProgrammeName = "PROGRAMME NAME"
    textProgrammeID = "PROGRAMME ID"
    textPaymentRecords = "PAYMENT RECORDS"
    textStartDate = "START DATE"
    textEndDate = "END DATE"
    textBankReconciliation = "Bank reconciliation"
    textSuccessful = "SUCCESSFUL"
    textErroneus = "ERRONEOUS"
    textVerificationPlansSummary = "Verification Plans Summary"

    // Elements
    getPaymentVerificationTitle = () => cy.get(this.paymentVerificationTitle)
    getCreateVerificationPlan = () => cy.get(this.createVerificationPlan)
    getProgrammeName = () => cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(0)
    getProgrammeID = () => cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(1)
    getPaymentRecords = () => cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(2)
    getStartDate = () => cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(3)
    getEndDate = () => cy.get(this.divPaymentDetails).get(this.gridPaymentDetails).eq(4)
    getBankReconciliationTitle = () => cy.get(this.divBankReconciliation).get(this.tableTitle)
    getSuccessful = () => cy.get(this.divBankReconciliation).eq(0).get(this.gridBankReconciliation).get("div").eq(0)
    getErroneus = () => cy.get(this.divBankReconciliation).eq(0).get(this.gridBankReconciliation).get("div").eq(1)
    getVerificationPlansSummary = () => cy.get(this.divVerificationPlansSummary).get(this.tableTitle)

    checkPaymentVerificationTitle(){
        this.getPaymentVerificationTitle().contains(this.textTitle)
        this.getCreateVerificationPlan().get('span').contains(this.textCreateVerificationPlan)
    }

    checkGridPaymentDetails(){
        this.getProgrammeName().get('span').contains(this.textProgrammeName)  
        this.getProgrammeID().get('span').contains(this.textProgrammeName)  
        this.getPaymentRecords().get('span').contains(this.textProgrammeName)  
        this.getStartDate().get('span').contains(this.textProgrammeName)  
        this.getEndDate().get('span').contains(this.textProgrammeName)  
    }
    
    checkBankReconciliationTitle(){
        this.getBankReconciliationTitle().contains(this.textBankReconciliation)
    }

    checkGridBankReconciliation(){
        this.getSuccessful().contains(this.textSuccessful)
        this.getErroneus().contains(this.textErroneus)
    }

    checkVerificationPlansSummaryTitle(){
        this.getVerificationPlansSummary().contains(this.textVerificationPlansSummary)
    }

    checkGridVerificationPlansSummary(){

    }
}