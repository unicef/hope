import PaymentVerification from "../../page-objects/pages/payment_veryfication/payment_veryfication.po";
import PVDetailsPage from "../../page-objects/pages/payment_veryfication/details_page.po";

let pv = new PaymentVerification();
let pvd = new PVDetailsPage();
let defaultNumberOfVPlans016 = 0;

describe("Payment Verification", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
    pv.clickMenuButtonPaymentVerification();
  });

  describe("Smoke tests Payment Verification", () => {
    it("Check Payment Verification page", () => {
      cy.scenario([
        "Go to Payment Verification page",
        "Check if all elements on page exist",
      ]);
      pv.checkPaymentVerificationTitle();
      pv.checkListOfCashPlansTitle();
      pv.checkAllSearchFieldsVisible();
      pv.checkCashPlansTableVisible();
    });

    // eslint-disable-next-line mocha/no-setup-in-describe
    pv.countCashPlanArray().forEach((row_no) => {
      it(`Check Cash Plan Details Page - Row: ${row_no}`, () => {
        pv.scenario([
          "Go to Payment Verification page",
          "Choose and open cash plan",
          "Check if all elements on page exist",
        ]);
        pv.chooseCashPlan(row_no).click();
        pvd.checkPaymentVerificationTitle();
        pvd.checkGridPaymentDetails();
        pvd.checkBankReconciliationTitle();
        pvd.checkGridBankReconciliation();
        pvd.checkVerificationPlansSummaryTitle();
        pvd.checkGridVerificationPlansSummary();
      });
    });

    it.skip("Check Create Verification Plan pop-up", () => {
      // ToDo
    });
  });

  describe("Component tests Payment Verification", () => {
    context("Create Verification Plan", () => {
      afterEach(() => {
        pvd.deleteVerificationPlan(0);
      });
      it("Create Verification Plan using random sampling", () => {
        pv.scenario([
          "Search Pending cash plans",
          "Select first Pending cash plan",
          "Check if Payment Verification title exists",
          "Press Create Verification Plan button",
          "Check if Create Verification Plan title occurs",
          "Choose Random Sampling tab",
          "Press Save button",
          "Check if Verification Plan was created",
        ]);
        pv.selectStatus("Pending");
        pv.getStatusOption().contains("Pending").type("{esc}");
        pv.getCashPlanRows().should("have.length", 1);
        pv.chooseCashPlan(0).click();
        pvd.checkPaymentVerificationTitle();
        pvd.getCreateVerificationPlan().click();
        pvd.checkCVPTitle();
        pvd.getRandomSampling().click();
        pvd.getCVPConfidenceInterval().should("be.visible");
        pvd.getCVPSave().click();
        pvd.checkVerificationPlan();
      });
    });

    context("Verification Plan Settings", () => {
      it.skip("Test_1", () => {
        // ToDo
      });
    });

    context("Edit Verification Plan", () => {
      beforeEach(() => {
        pv.getPaymentPlanID().type("123-21-CSH-00002");
        pv.getCashPlanRows().should("have.length", 1);
        pv.chooseCashPlan(0).click();
        pvd.createNewVerificationPlan();
      });
      it.skip("Test_1", () => {
        pvd.getEditVP().contains("EDIT").click();
        pvd.getCVPTitle;
      });
    });

    context("Delete Verification Plan", () => {
      beforeEach(() => {
        pv.getPaymentPlanID().type("123-21-CSH-00002");
        pv.getCashPlanRows().should("have.length", 1);
        pv.chooseCashPlan(0).click();
        pvd.createNewVerificationPlan(defaultNumberOfVPlans016);
      });
      it.skip("Delete one Verification Plan", () => {
        pvd.getDeletePlan().click();
        pvd.getDelete().click();
        pvd.getNumberOfPlans().contains(1);
      });
    });

    context("Activate Verification Plan", () => {
      beforeEach(() => {
        pv.getPaymentPlanID().type("123-21-CSH-00002");
        pv.getCashPlanRows().should("have.length", 1);
        pv.chooseCashPlan(0).click();
        pvd.createNewVerificationPlan(defaultNumberOfVPlans016);
      });
      afterEach(() => {
        pvd.discardVerificationPlan(0);
        pvd.deleteVerificationPlan(0);
      });
      it("Activate Verification Plan", () => {
        pv.scenario([
          "Press Activation button",
          "Press Activate button on pop-up",
          "Check if Summary status = ACTIVE",
          "Check if Activation Date was set",
          "Check if verification plan has status Active",
        ]);
        pvd.getActivatePlan().click();
        pvd.getActivate().click();
        pvd.getStatusVP().contains("ACTIVE");
        pvd.getActivationDate().find("div").not("-");
        pvd.getStatus().contains("ACTIVE");
      });
    });

    context("Finish Verification Plan", () => {
      beforeEach(() => {
        pv.getPaymentPlanID().type("123-21-CSH-00001");
        pv.getCashPlanRows().should("have.length", 1);
        pv.chooseCashPlan(0).click();
        pvd.createNewVerificationPlan(defaultNumberOfVPlans016);
      });
      it.skip("Finish Verification Plan", () => {
        pvd.getActivatePlan().click();
        pvd.getActivate().click();
        pvd.getStatusVP().contains("ACTIVE");
        pvd.getFinishPlan().click();
        pvd.getFinish().click();
        pvd.getStatusVP().contains("FINISHED");
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
    pv.countCashPlanArray().forEach((row_no) => {
      it.skip(`Compare data in Cash Plan Details Page - Row: ${row_no}`, () => {
        // pv.chooseCashPlan(row_no).click()
        cy.get('[data-cy="cash-plan-table-row"]').first().click();
        cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
        cy.get('[data-cy="page-header-container"]').contains("Payment Plan");
        cy.get("h6").contains("Cash Plan Details");
        cy.get("h6").contains("Verification Plans Summary");
      });
    });
  });
  describe("Regression tests Payment Verification", () => {
    it.skip("BUG 161302 - The Status drop-down menu jumps.", () => {
      // ToDo
    });
  });
});
