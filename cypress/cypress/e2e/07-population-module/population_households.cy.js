import PopulationHouseholds from "../../page-objects/pages/population_module/population_households.po";
import HPDetailsPage from "../../page-objects/pages/population_module/households_details_page.po";

let populationHouseholds = new PopulationHouseholds();
let householdsDetailsPage = new HPDetailsPage();

describe("Households Module", () => {
  before(() => {
    cy.checkIfLoggedIn();
  });
  beforeEach(() => {
    cy.initScenario("payment_plan");
    cy.navigateToHomePage();
    cy.get("span").contains("Population").click();
    cy.get("span").contains("Individuals");
    cy.get("span").contains("Households");
    cy.get("span").contains("Households").click();
    // populationHouseholds.getButtonFiltersExpand().click();
  });
  describe("Smoke tests Households Population module", () => {
    it("Check Households Population page", () => {
      populationHouseholds.checkElementsOnPage();
    });
    it("Check Households Population Details page", () => {
      // ToDo: Global Programme changes
      cy.scenario([
        "Go to Population page",
        "Check if page is in Households",
        "Choose first Household from list",
        "Check if all elements on page exist",
      ]);
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
      it.skip("Households Population Search filter", () => {});
      it.skip("Households Population Programme filter", () => {});
      it.skip("Households Population Residence Status filter", () => {});
      it.skip("Households Population Admin Level 2 filter", () => {});
      it.skip("Household Size filter", () => {});
      it.skip("Households Population Sorted by filter", () => {});
      it.skip("Households Population Status filter", () => {});
    });
  });
  describe.skip("E2E tests Households Population", () => {});

  describe("Regression tests Households Population", () => {
    it("174517: Check clear cache", () => {
      cy.scenario([
        "Go to Households page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      populationHouseholds.clearCache();
      populationHouseholds
        .getPageHeaderTitle()
        .contains(populationHouseholds.textTitle);
    });
  });
});
