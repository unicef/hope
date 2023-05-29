import BaseComponent from '../../base.component';

export default class PaymentVerification extends BaseComponent {

    // Locators
    paymentVerificationTitle = 'h5[class="MuiTypography-root MuiTypography-h5"]'
    paymentPlanID = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    status = 'div[class="MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiSelect-outlined MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    FSP = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    modality = 'div[class="MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiSelect-outlined MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    startDate = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedEnd MuiOutlinedInput-inputAdornedEnd MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    endDate = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedEnd MuiOutlinedInput-inputAdornedEnd MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    programme = 'div[class="MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiSelect-outlined MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    
    listOfCashPlansTitle = 'h6[data-cy="table-title"]'
    tableTitle = 'table[aria-labelledby="tableTitle"]'
    tableColumn = 'span[class="MuiButtonBase-root MuiTableSortLabel-root sc-fBuWsC dHSJjy"]'
    rowsPerPage = 'id[id="mui-33182"]'
    table = 'tbody[class="MuiTableBody-root"]'
    rows = 'tr[class="MuiTableRow-root sc-RefOD isLSKU MuiTableRow-hover"]'

    // Texts
    textTitle = "Payment Verification"
    textTabTitle = "List of Cash Plans"
    textPaymentPlanID = "Cash/Payment Plan ID"
    textStatus = "Status"
    textFSP = "FSP"
    textModality = "Modality"
    textStartDate = "Start Date"
    textEndDate = "End Date"
    textProgramme = "Programme"
    textCashPlanID = "Cash Plan ID"
    textVerificationStatus = "Verification Status"
    textCashAmount = "Cash Amount"
    textTimeframe = "Timeframe"
    textColumnProgramme = "Programme"
    textLastModifiedDate = "Last Modified Date"

    // Elements
    getPaymentVerificationTitle = () => cy.get(this.paymentVerificationTitle)
    getListOfCashPlansTitle = () => cy.get(this.listOfCashPlansTitle)
    getPaymentPlanID = () => cy.get(this.paymentPlanID).eq(0)
    getStatus = () => cy.get(this.status)
    getFSP = () => cy.get(this.FSP).eq(1)
    getModality = () => cy.get(this.modality).eq(1)
    getStartDate = () => cy.get(this.startDate)
    getEndDate = () => cy.get(this.endDate)
    getProgramme = () => cy.get(this.programme)
    getTable = () => cy.get(this.tableTitle)
    getCashPlanID = () => cy.get(this.tableColumn).eq(0)
    getVerificationStatus = () => cy.get(this.tableColumn).eq(1)
    getCashAmount = () => cy.get(this.tableColumn).eq(2)
    getTimeFrame = () => cy.get(this.tableColumn).eq(3)
    getColumnProgramme = () => cy.get(this.tableColumn).eq(4)
    getLastModifiedDate = () => cy.get(this.tableColumn).eq(5)
    getCashPlanRows = () => cy.get(this.table).get(this.rows)

    checkPaymentVerificationTitle(){
        return this.getPaymentVerificationTitle().contains(this.textTitle)
    }

    checkListOfCashPlansTitle(){
        return this.getListOfCashPlansTitle().contains(this.textTabTitle)
    }

    checkAllSearchFieldsVisible(){
        this.getPaymentPlanID().should('be.visible')
        this.getPaymentPlanID().get("span").contains(this.textPaymentPlanID)
        this.getStatus().should('be.visible')
        this.getStatus().get('span').contains(this.textStatus)
        this.getFSP().should('be.visible')
        this.getFSP().get("span").contains(this.textFSP)
        this.getModality().should('be.visible')
        this.getModality().get("span").contains(this.textModality)
        this.getStartDate().should('be.visible')
        this.getStartDate().get("span").contains(this.textStartDate)
        this.getEndDate().should('be.visible')
        this.getEndDate().get("span").contains(this.textEndDate)
        this.getProgramme().should('be.visible')
        this.getProgramme().get("span").contains(this.textProgramme)
    }

    checkCashPlansTableVisible(){
        this.getTable().should('be.visible')
        this.getCashPlanID().should('be.visible').contains(this.textCashPlanID)
        this.getVerificationStatus().should('be.visible').contains(this.textVerificationStatus)
        this.getCashAmount().should('be.visible').contains(this.textCashAmount)
        this.getTimeFrame().should('be.visible').contains(this.textTimeframe)
        this.getColumnProgramme().should('be.visible').contains(this.textColumnProgramme)
        this.getLastModifiedDate().should('be.visible').contains(this.textLastModifiedDate)
    }

    countCashPlanArray() {
        return Array.from(Array(4).keys())
    }

    chooseCashPlan(row){
        return this.getCashPlanRows().eq(row)
    }


}