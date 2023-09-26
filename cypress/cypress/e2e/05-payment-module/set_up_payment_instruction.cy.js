import PaymentPlanPage from "../../page-objects/pages/payment_module/payment_plan_page.po";
import PaymentPlanDetailsPage from "../../page-objects/pages/payment_module/payment_plans_details_page.po";

let paymentPlanPage = new PaymentPlanPage();
let paymentPlanDetailsPage = new PaymentPlanDetailsPage();

describe("Payment Plan", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
  });
  describe("Smoke tests Payment Plan module", () => {
    it("Check Payment Plan page", () => {});
  });
  describe("Component tests Payment Plan", () => {
    it("Can create a payment plan", () => {});
  });
  describe.skip("E2E tests Payment", () => {});

  describe.skip("Regression tests Payment", () => {});
});
