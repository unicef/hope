import PaymentCyclesPage from "../../page-objects/pages/payment_module/payment_cycles.po";

let paymentCyclesPage = new PaymentCyclesPage();

describe("Payment Plan", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
  });
  describe("Smoke tests Payment Plan module", () => {
    it.skip("Check Payment Plan page", () => {});
    it.skip("Check Payment Plan Details page", () => {});
  });
  describe("Component tests Payment Plan", () => {
    it("Can create a payment plan", () => {});
  });
  describe.skip("E2E tests Payment", () => {});

  describe("Regression tests Payment", () => {
    it.skip("174517: Check clear cache", () => {
      cy.scenario([
        "Go to Payment module page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      cy.navigateToHomePage();
      paymentModule.getButtonPaymentModule().click();
      paymentModule.clearCache();
      paymentModule.getTitle().contains(paymentModule.textTitle);
    });
  });
});
