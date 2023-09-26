import FollowUpPage from "../../page-objects/pages/payment_module/follow-up_payment_plans.po";

let followUpPage = new FollowUpPage();

describe("Follow-up Payment Plans", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
  });
  describe("Smoke tests Payment module", () => {
    it.skip("Check Follow-up Payment Plans page", () => {});
    it.skip("Check Follow-up Payment Plans Details page", () => {});
  });
  describe("Component tests Follow-up Payment Plans", () => {
    it("Can create a payment plan", () => {});
  });
  describe.skip("E2E tests Payment", () => {});

  describe.skip("Regression tests Payment", () => {});
});
