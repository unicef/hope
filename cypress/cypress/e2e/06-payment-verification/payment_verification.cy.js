import PaymentVerification from "../../page-objects/pages/payment_veryfication/payment_veryfication.po";

let pv = new PaymentVerification()

context("Payment Verification", () => {
  beforeEach(() => {
    cy.adminLogin()
    cy.navigateToHomePage();
    pv.clickMenuButtonPaymentVerification()
  });

  it("Check Payment Verification Page is loaded", () => {
    pv.checkPaymentVerificationTitle()
    pv.checkListOfCashPlansTitle()

    pv.checkAllSearchFieldsVisible()
    pv.checkChachPlansTableVisible()
  });


  it("Can see the Cash Plan Details Page", () => {

    return; // TODO: must seed with some cash plan
    cy.get('[data-cy="cash-plan-table-row"]').first().click();
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.get('[data-cy="page-header-container"]').contains("Payment Plan");
    cy.get("h6").contains("Cash Plan Details");
    cy.get("h6").contains("Verification Plans Summary");
  });
});
