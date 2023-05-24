import BaseComponent from '../../base.component';

export default class PaymentVerification extends BaseComponent {

    // Locators
    paymentVerificationTitle = 'h5[class="MuiTypography-root MuiTypography-h5"]'
    listOfCashPlansTitle = 'h6[data-cy="table-title"]'
    PaymentPlanID = 'input[class="MuiInputBase-input MuiOutlinedInput-input MuiInputBase-inputAdornedStart MuiOutlinedInput-inputAdornedStart MuiInputBase-inputMarginDense MuiOutlinedInput-inputMarginDense"]'
    listOfCashPlansTitle = 'h6[data-cy="table-title"]'
    listOfCashPlansTitle = 'h6[data-cy="table-title"]'


    // Texts
    textTitle = "Payment Verification"
    textTabTitle = "List of Cash Plans"
    textPaymentPlanID = "Cash/Payment Plan ID"

    // Elements
    getPaymentVerificationTitle = () => cy.get(this.paymentVerificationTitle)
    getListOfCashPlansTitle = () => cy.get(this.listOfCashPlansTitle)
    getPaymentPlanID = () => cy.get(this.PaymentPlanID)

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
        this.getPaymentPlanID().should('be.visible')
        this.getPaymentPlanID().should('be.visible')
        this.getPaymentPlanID().should('be.visible')
        this.getPaymentPlanID().should('be.visible')

        return this
    }

    checkChachPlansTableVisible(){
        // ToDo
        return this
    }

}