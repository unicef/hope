import BaseComponent from '../../base.component';

export default class PaymentVerification extends BaseComponent {

    // Locators
    paymentVerificationTitle = 'h5[class="MuiTypography-root MuiTypography-h5"]'
    listOfCashPlansTitle = 'h6[data-cy="table-title"]'
    paymentPlanID = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    status = 'div[class="MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiSelect-outlined MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    FSP = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    modality = 'div[class="MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiSelect-outlined MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    startDate = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedEnd MuiOutlinedInput-inputAdornedEnd MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    endDate = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedEnd MuiOutlinedInput-inputAdornedEnd MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    programme = 'div[class="MuiSelect-root MuiSelect-select MuiSelect-selectMenu MuiSelect-outlined MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    
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

    checkPaymentVerificationTitle(){
        this.getPaymentVerificationTitle().contains(this.textTitle)
        return this
    }

    checkListOfCashPlansTitle(){
        this.getListOfCashPlansTitle().contains(this.textTabTitle)
        return this
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
        return this
    }

    checkChachPlansTableVisible(){
        // ToDo
        return this
    }

}