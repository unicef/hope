import PaymentVerification from "../../page-objects/pages/payment_veryfication/payment_veryfication.po";

let pv = new PaymentVerification()
describe("Payment Verification", () => {
  beforeEach(() => {
    cy.adminLogin()
    cy.navigateToHomePage();
    pv.clickMenuButtonPaymentVerification()
  });

  context("Smoke tests Payment Verification", () => {

    it("Check Payment Verification Page is loaded", () => {
      pv.checkPaymentVerificationTitle()
      pv.checkListOfCashPlansTitle()

      pv.checkAllSearchFieldsVisible()
      pv.checkChachPlansTableVisible()
    });
  });

  context("Component tests Payment Verification", () => {
    it.skip("Create Verification Plan", () => {
      // ToDo
    });

    it.skip("Verification Plan Settings", () => {
      // ToDo
    });

    it.skip("Edit Verification Plan", () => {
      // ToDo
    });

    it.skip("Delete Verification Plan", () => {
      // ToDo
    });

    it.skip("Activate Verification Plan", () => {
      // ToDo
    });

    it.skip("Finish Verification Plan", () => {
      // ToDo
    });

    it.skip("Grievance creation/preview", () => {
      // ToDo
    });

    it.skip("Verify Payment Record - Verify Manually", () => {
      // ToDo
    });

    it.skip("Verify Payment Record - Verify using RapidPro", () => {
      // ToDo
    });

    it.skip("Verify Payment Record - Verify using XLSX", () => {
      // ToDo
    });

    it.skip("Business Requirements", () => {
      // ToDo
    });

    
    it.skip("Can see the Cash Plan Details Page", () => {

      return; // TODO: must seed with some cash plan
      cy.get('[data-cy="cash-plan-table-row"]').first().click();
      cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
      cy.get('[data-cy="page-header-container"]').contains("Payment Plan");
      cy.get("h6").contains("Cash Plan Details");
      cy.get("h6").contains("Verification Plans Summary");
    });
  });
  context("E2E tests Payment Verification", () => {
  });
  context("Regression tests Payment Verification", () => {
  });
});
