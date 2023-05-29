import PaymentVerification from "../../page-objects/pages/payment_veryfication/payment_veryfication.po";
import PVDetailsPage from "../../page-objects/pages/payment_veryfication/details_page.po";

let pv = new PaymentVerification()
let pvDetails = new PVDetailsPage()

describe("Payment Verification", () => {
  beforeEach(() => {
    cy.adminLogin()
    cy.navigateToHomePage();
    pv.clickMenuButtonPaymentVerification()
  });

  context("Smoke tests Payment Verification", () => {

    it("Check the Payment Verification page", () => {
      pv.checkPaymentVerificationTitle()
      pv.checkListOfCashPlansTitle()
      pv.checkAllSearchFieldsVisible()
      pv.checkCashPlansTableVisible()
    });

    pv.countCashPlanArray().forEach((row_no) => {
      it.only(`Check Cash Plan Details Page - Row: ${row_no}`, () => {
        pv.chooseCashPlan(row_no).click()
        pvDetails.checkPaymentVerificationTitle()
        pvDetails.checkGridPaymentDetails()
        pvDetails.checkBankReconciliationTitle()
        pvDetails.checkGridBankReconciliation()   
        pvDetails.checkVerificationPlansSummaryTitle()
        pvDetails.checkGridVerificationPlansSummary()
      });
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

  });
  context("E2E tests Payment Verification", () => {
    pv.countCashPlanArray().forEach((row_no) => {
    it.skip(`Compare data in Cash Plan Details Page - Row: ${row_no}`, () => {
      // pv.chooseCashPlan(row_no).click()

      return; // TODO: must seed with some cash plan
      cy.get('[data-cy="cash-plan-table-row"]').first().click();
      cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
      cy.get('[data-cy="page-header-container"]').contains("Payment Plan");
      cy.get("h6").contains("Cash Plan Details");
      cy.get("h6").contains("Verification Plans Summary");
    });});
  });
  context("Regression tests Payment Verification", () => {
    it.skip("BUG 161302 - The Status drop-down menu jumps.", () => {
      // ToDo
    });
  });
});
