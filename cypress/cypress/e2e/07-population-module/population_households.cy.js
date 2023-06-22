import PopulationHouseholds from "../../page-objects/pages/population_module/population_households.po";
import HPDetailsPage from "../../page-objects/pages/population_module/households_details_page.po";

let ph = new PopulationHouseholds();
let phdp = new HPDetailsPage();

describe("Households Module", () => {
  beforeEach(() => {
    cy.initScenario("payment_plan");
    cy.adminLogin();
    cy.navigateToHomePage();
    cy.get("span").contains("Population").click();
    cy.get("span").contains("Individuals");
    cy.get("span").contains("Households");
    cy.get("span").contains("Households").click();
  });
  describe("Smoke tests Households Population module", () => {
    it.skip("Check Households Population page", () => {});
    it.skip("Check Households Population Details page", () => {
      // ToDo: Global Programme changes
      cy.get("div").contains("Households", { timeout: 10000 });
      cy.get('[data-cy="table-title"]').contains("Households");
      cy.get('[data-cy="household-table-row"]').first().click({ force: true });
      cy.get('[data-cy="page-header-container"]').contains("Household ID:", {
        timeout: 10000,
      });
      cy.get("h6").contains("Details");
      cy.get("h6").contains("Benefits");
      cy.get("h6").contains("Household Composition");
      cy.get("h6").contains("Individuals in Household");
      cy.get("h6").contains("Payment Records");
      cy.get("h6").contains("Vulnerabilities");
      cy.get("h6").contains("Registration Details");
      cy.get("h6").contains("Activity Log");
    });
  });
  describe("Component tests Households Population", () => {
    context("Households Population Filters", () => {
      it.skip("Households Population Search filter", () => {
        // ToDo
      });
      it.skip("Households Population Programme filter", () => {
        // ToDo
      });
      it.skip("Households Population Residence Status filter", () => {
        // ToDo
      });
      it.skip("Households Population Admin Level 2 filter", () => {
        // ToDo
      });
      it.skip("Household Size filter", () => {
        // ToDo
      });
      it.skip("Households Population Sorted by filter", () => {
        // ToDo
      });
      it.skip("Households Population Status filter", () => {
        // ToDo
      });
    });
  });
  describe.skip("E2E tests Households Population", () => {});

  describe.skip("Regression tests Households Population", () => {});
});
