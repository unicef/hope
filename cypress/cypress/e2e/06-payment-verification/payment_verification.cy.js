import PaymentVerification from "../../page-objects/pages/payment_verification/payment_verification.po";
import PVDetailsPage from "../../page-objects/pages/payment_verification/details_page.po";

let paymentVerificationPage = new PaymentVerification();
let paymentVerificationDetailsPage = new PVDetailsPage();
let defaultNumberOfVPlans016 = 0;

describe("Payment Verification", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
    paymentVerificationPage.clickMenuButtonPaymentVerification();
  });

  describe("Smoke tests Payment Verification", () => {
    it("Check Payment Verification page", () => {
      cy.scenario([
        "Go to Payment Verification page",
        "Check if all elements on page exist"
      ]);
      paymentVerificationPage.checkPaymentVerificationTitle();
      paymentVerificationPage.checkListOfPaymentPlansTitle();
      paymentVerificationPage.checkAllSearchFieldsVisible();
      paymentVerificationPage.checkPaymentPlansTableVisible();
    });

    // eslint-disable-next-line mocha/no-setup-in-describe
    paymentVerificationPage.countPaymentPlanArray().forEach((row_no) => {
      it(`Check Payment Plan Details Page - Row: ${row_no}`, () => {
        cy.scenario([
          "Go to Payment Verification page",
          "Choose and open cash plan",
          "Check if all elements on page exist"
        ]);
        paymentVerificationPage.choosePaymentPlan(row_no).click();
        paymentVerificationDetailsPage.checkPaymentVerificationTitle();
        paymentVerificationDetailsPage.checkGridPaymentDetails();
        paymentVerificationDetailsPage.checkBankReconciliationTitle();
        paymentVerificationDetailsPage.checkGridBankReconciliation();
        paymentVerificationDetailsPage.checkVerificationPlansSummaryTitle();
        paymentVerificationDetailsPage.checkGridVerificationPlansSummary();
      });
    });

    it.skip("Check Create Verification Plan pop-up", () => {
      // ToDo
    });
  });

  describe("Component tests Payment Verification", () => {
    context("Create Verification Plan", () => {
      afterEach(() => {
        paymentVerificationDetailsPage.deleteVerificationPlan(0);
      });
      it("Create Verification Plan using random sampling", () => {
        cy.scenario([
          "Search Pending cash plans",
          "Select first Pending cash plan",
          "Check if Payment Verification title exists",
          "Press Create Verification Plan button",
          "Check if Create Verification Plan title occurs",
          "Choose Random Sampling tab",
          "Press Save button",
          "Check if Verification Plan was created"
        ]);
        paymentVerificationPage.selectStatus("Pending");
        paymentVerificationPage.getPaymentPlanRows().should("have.length", 1);
        paymentVerificationPage.choosePaymentPlan(0).click();
        paymentVerificationDetailsPage.checkPaymentVerificationTitle();
        paymentVerificationDetailsPage.getCreateVerificationPlan().click();
        paymentVerificationDetailsPage.checkCVPTitle();
        paymentVerificationDetailsPage.getRandomSampling().click();
        paymentVerificationDetailsPage
          .getCVPConfidenceInterval()
          .should("be.visible");
        paymentVerificationDetailsPage.getCVPSave().click();
        paymentVerificationDetailsPage.checkVerificationPlan();
      });
    });

    context("Verification Plan Settings", () => {
      it.skip("Test_1", () => {
        // ToDo
      });
    });

    context("Edit Verification Plan", () => {
      beforeEach(() => {
        paymentVerificationPage.getPaymentPlanID().type("PP-0060-23-00000002");
        paymentVerificationPage.getApply().click();
        paymentVerificationPage.getPaymentPlanRows().should("have.length", 1);
        paymentVerificationPage.choosePaymentPlan(0).click();
        paymentVerificationDetailsPage.createNewVerificationPlan();
      });
      it.skip("Test_1", () => {
        paymentVerificationDetailsPage.getEditVP().contains("EDIT").click();
        paymentVerificationDetailsPage.getCVPTitle();
      });
    });

    context("Delete Verification Plan", () => {
      beforeEach(() => {
        paymentVerificationPage.getPaymentPlanRows().should("have.length", 1);
        paymentVerificationPage.choosePaymentPlan(0).click();
        paymentVerificationDetailsPage.createNewVerificationPlan(
          defaultNumberOfVPlans016
        );
      });
      it("Delete Verification Plan", () => {
        cy.scenario([
          "Press Delete button",
          "Press Delete button on pop-up",
          "Check if Verification Plan was deleted"
        ]);
        paymentVerificationDetailsPage.getDeletePlan().scrollIntoView().click();
        paymentVerificationDetailsPage.getDelete().scrollIntoView().click();
        paymentVerificationDetailsPage.getNumberOfPlans().contains(1);
      });
    });

    context("Activate Verification Plan", () => {
      beforeEach(() => {
        paymentVerificationPage.getPaymentPlanRows().should("have.length", 1);
        paymentVerificationPage.choosePaymentPlan(0).click();
        paymentVerificationDetailsPage.createNewVerificationPlan(
          defaultNumberOfVPlans016
        );
      });
      afterEach(() => {
        paymentVerificationDetailsPage.discardVerificationPlan(0);
        paymentVerificationDetailsPage.deleteVerificationPlan(0);
      });
      it("Activate Verification Plan", () => {
        cy.scenario([
          "Press Activation button",
          "Press Activate button on pop-up",
          "Check if Summary status = ACTIVE",
          "Check if Activation Date was set",
          "Check if verification plan has status Active"
        ]);
        paymentVerificationDetailsPage.getActivatePlan().click();
        paymentVerificationDetailsPage.getActivate().click();
        paymentVerificationDetailsPage.getStatusVP().contains("ACTIVE");
        paymentVerificationDetailsPage.getActivationDate().find("div").not("-");
        paymentVerificationDetailsPage.getStatus().contains("ACTIVE");
      });
    });

    context("Finish Verification Plan", () => {
      beforeEach(() => {
        paymentVerificationPage.getPaymentPlanID().type("PP-0060-23-00000002");
        paymentVerificationPage.getApply().click();
        paymentVerificationPage.getPaymentPlanRows().should("have.length", 1);
        paymentVerificationPage.choosePaymentPlan(0).click();
        paymentVerificationDetailsPage.createNewVerificationPlan(
          defaultNumberOfVPlans016
        );
      });
      it.skip("Finish Verification Plan", () => {
        paymentVerificationDetailsPage.getActivatePlan().click();
        paymentVerificationDetailsPage.getActivate().click();
        paymentVerificationDetailsPage.getStatusVP().contains("ACTIVE");
        paymentVerificationDetailsPage.getFinishPlan().click();
        paymentVerificationDetailsPage.getFinish().click();
        paymentVerificationDetailsPage.getStatusVP().contains("FINISHED");
      });
    });

    context("Grievance creation/preview", () => {
      it.skip("Test_1", () => {
        // ToDo
      });
    });

    context("Verify Payment Record", () => {
      it.skip("Verify Manually", () => {
        // ToDo
      });
      it.skip("Verify using RapidPro", () => {
        // ToDo
      });
      it.skip("Verify using XLSX", () => {
        // ToDo
      });
    });
  });
  describe("E2E tests Payment Verification", () => {
    // eslint-disable-next-line mocha/no-setup-in-describe
    paymentVerificationPage.countPaymentPlanArray().forEach((row_no) => {
      it(`Compare data in Payment Plan Details Page - Row: ${row_no}`, () => {
        paymentVerificationPage.choosePaymentPlan(row_no).click();
        cy.get('[data-cy="page-header-container"]', {
          timeout: 10000
        }).contains("Payment Plan");
        paymentVerificationDetailsPage.checkPaymentPlanDetailsTitle();
        paymentVerificationDetailsPage.checkVerificationPlansSummaryTitle();
      });
    });
  });
  describe("Regression tests Payment Verification", () => {
    it.skip("BUG 161302 - The Status drop-down menu jumps.", () => {
      // ToDo
    });
  });
});
