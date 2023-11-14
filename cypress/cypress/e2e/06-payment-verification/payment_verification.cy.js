import PaymentVerification from "../../page-objects/pages/payment_verification/payment_verification.po";
import PVDetailsPage from "../../page-objects/pages/payment_verification/details_page.po";

let paymentVerificationPage = new PaymentVerification();
let paymentVerificationDetailsPage = new PVDetailsPage();
let defaultNumberOfVPlans016 = 0;

const paymentPlanID = "PP-0060-23-00000002";
describe("Payment Verification", () => {
  before(() => {
    cy.checkIfLoggedIn();
  });
  beforeEach(() => {
    cy.navigateToHomePage();
    paymentVerificationPage.clickMenuButtonPaymentVerification();
    paymentVerificationPage.getButtonFiltersExpand().click();
  });

  after(() => {
    cy.initScenario("init_clear");
    cy.adminLogin();
  });

  describe("Smoke tests Payment Verification", () => {
    it("Check Payment Verification page", () => {
      cy.scenario([
        "Go to Payment Verification page",
        "Check if all elements on page exist",
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
          "Check if all elements on page exist",
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

    it.skip("Check Create Verification Plan pop-up", () => {});
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
          "Check if Verification Plan was created",
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
      it.skip("Test_1", () => {});
    });

    context("Edit Verification Plan", () => {
      beforeEach(() => {
        paymentVerificationPage.getPaymentPlanRows().should("have.length", 1);
        paymentVerificationPage.choosePaymentPlan(0).click();
        paymentVerificationDetailsPage.createNewVerificationPlan();
      });
      it("Edit Verification Plan", () => {
        cy.scenario([
          "Go to Verification Plan page",
          "Choose Verification Plan",
          "Create New Verification Plan",
          "After create Verification Plan Press Edit button",
          "Change verification channel from MANUAL to XLSX",
          "Press button Save",
          "Check if Verification Plan was changed",
        ]);
        paymentVerificationDetailsPage.getEditVP().contains("Edit").click();
        paymentVerificationDetailsPage.getCvpInputAdminCheckbox().click();
        paymentVerificationDetailsPage
          .getLabelVERIFICATIONCHANNEL()
          .contains("MANUAL");
        paymentVerificationDetailsPage.getXLSX().click();
        paymentVerificationDetailsPage.getCVPSave().click();
        paymentVerificationDetailsPage
          .getLabelVERIFICATIONCHANNEL()
          .contains("XLSX");
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
          "Go to Verification Plan page",
          "Choose Verification Plan",
          "Create New Verification Plan",
          "Press Delete button",
          "Press Delete button on pop-up",
          "Check if Verification Plan was deleted",
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
          "Go to Verification Plan page",
          "Choose Verification Plan",
          "Create New Verification Plan",
          "Press Activation button",
          "Press Activate button on pop-up",
          "Check if Summary status = ACTIVE",
          "Check if Activation Date was set",
          "Check if verification plan has status Active",
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
        paymentVerificationPage.getPaymentPlanRows().should("have.length", 1);
        paymentVerificationPage.choosePaymentPlan(0).click();
        paymentVerificationDetailsPage.createNewVerificationPlan(
          defaultNumberOfVPlans016
        );
      });
      it("Finish Verification Plan", () => {
        cy.scenario([
          "Go to Verification Plan page",
          "Choose Active Verification Plan",
          "Press Finish button",
          "Press Finish button on pop-up",
          "Check if Verification Plan was finished",
        ]);
        paymentVerificationDetailsPage.getActivatePlan().click();
        paymentVerificationDetailsPage.getActivate().click();
        paymentVerificationDetailsPage.getStatusVP().contains("ACTIVE");
        paymentVerificationDetailsPage.getFinishPlan().click();
        paymentVerificationDetailsPage.getFinish().click();
        paymentVerificationDetailsPage.getStatusVP().contains("FINISHED");
      });
    });

    context("Grievance creation/preview", () => {
      it.skip("Test_1", () => {});
    });

    context("Verify Payment Record", () => {
      it.skip("Verify Manually", () => {});
      it.skip("Verify using RapidPro", () => {});
      it.skip("Verify using XLSX", () => {});
    });
  });
  describe("E2E tests Payment Verification", () => {
    // ToDo: Refactor this in second milestone
    paymentVerificationPage.countPaymentPlanArray().forEach((row_no) => {
      it(`Compare data in Payment Plan Details Page - Row: ${row_no}`, () => {
        paymentVerificationPage.choosePaymentPlan(row_no).click();
        cy.get('[data-cy="page-header-container"]', {
          timeout: 10000,
        }).contains("Payment Plan");
        paymentVerificationDetailsPage.checkPaymentPlanDetailsTitle();
        paymentVerificationDetailsPage.checkVerificationPlansSummaryTitle();
      });
    });
  });
  describe("Regression tests Payment Verification", () => {
    it("174517: Check clear cache", () => {
      cy.scenario([
        "Go to Payment Verification page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      paymentVerificationPage.clearCache();
      paymentVerificationPage.checkPaymentVerificationTitle();
    });
    it.skip("BUG 161302 - The Status drop-down menu jumps.", () => {});
  });
});
