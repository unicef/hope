import BaseComponent from '../../base.component';

export default class PaymentVerification extends BaseComponent {

    // Locators
    paymentVerificationTitle = 'h5[class="MuiTypography-root MuiTypography-h5"]'
    listOfCashPlansTitle = 'h6[data-cy="table-title"]'

    // Texts
    title = "Payment Verification"
    tabTitle = "List of Cash Plans"

    // Elements
    getPaymentVerificationTitle = () => cy.get(this.paymentVerificationTitle)
    getListOfCashPlansTitle = () => cy.get(this.listOfCashPlansTitle)

    checkPaymentVerificationTitle(){
        this.getPaymentVerificationTitle().contains(this.title)
        return this
    }

    checkListOfCashPlansTitle(){
        this.getListOfCashPlansTitle().contains(this.tabTitle)
        return this
    }

    checkAllSearchFieldsVisible(){
        // ToDo
        return this
    }

    checkChachPlansTableVisible(){
        // ToDo
        return this
    }

}