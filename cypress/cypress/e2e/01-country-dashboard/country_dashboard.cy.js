import CountryDashboard from "../../page-objects/pages/country_dashboard/country_dashboard.po";

let cd = new CountryDashboard();

describe("Country Dashboard", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
  });

  describe("Smoke tests Country Dashboard", () => {
    it.skip("Check Country Dashboard page", () => {
      // Scenario:
      // 1. Go to Country Dashboard page
      // 2. Check if all elements on page exist
    });
  });

  describe("Component tests Country Dashboard", () => {
    context("Export", () => {
      it.skip("ToDo", () => {});
    });

    context("Filters", () => {
      it.skip("Programme filter", () => {
        // ToDo
      });
      it.skip("Admin Level 2 filter", () => {
        // ToDo
      });
    });
  });
  describe.skip("E2E tests Country Dashboard", () => {});

  describe.skip("Regression tests Country Dashboard", () => {});
});
