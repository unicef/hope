import GrievanceDashboard from "../../page-objects/pages/grievance/grievance_dashboard.po";

let grievanceDashboard = new GrievanceDashboard();

describe("Grievance Dashboard", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
  });

  describe("Smoke tests Grievance Dashboard", () => {
    it.skip("Check Grievance Dashboard page", () => {
      // Scenario:
      // 1. Go to Grievance page
      // 2. Check if all elements on page exist
    });
  });

  describe("Component tests Grievance Dashboard", () => {
    context("Check numbers of tickets", () => {
      it.skip("ToDo", () => {});
    });
    context("Check number of closed tickets", () => {
      it.skip("ToDo", () => {});
    });
    context("Check average resolution", () => {
      it.skip("ToDo", () => {});
    });
  });
  describe.skip("E2E tests Grievance Dashboard", () => {});

  describe.skip("Regression tests Grievance Dashboard", () => {});
});
