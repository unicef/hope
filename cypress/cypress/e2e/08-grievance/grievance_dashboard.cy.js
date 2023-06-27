import GrievanceDashboard from "../../page-objects/pages/grievance/grievance_dashboard.po";

let grievanceDashboard = new GrievanceDashboard();

describe("Grievance Dashboard", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
    grievanceDashboard.clickMenuButtonGrievance();
    grievanceDashboard.clickMenuButtonGrievanceDashboard();
  });

  describe("Smoke tests Grievance Dashboard", () => {
    it("Check Grievance Dashboard page", () => {
      grievanceDashboard.checkElementsOnPage();
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
