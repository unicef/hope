import PopulationIndividuals from "../../page-objects/pages/population_module/population_individuals.po";
import IPDetailsPage from "../../page-objects/pages/population_module/individuals_details_page.po";

let pi = new PopulationIndividuals();
let pidp = new IPDetailsPage();

describe("Individuals Module", () => {
  beforeEach(() => {
    cy.initScenario("payment_plan");
    cy.adminLogin();
    cy.navigateToHomePage();
    cy.get("span").contains("Population").click();
    cy.get("span").contains("Individuals");
    cy.get("span").contains("Households");
    cy.get("span").contains("Individuals").click();
  });
  describe("Smoke tests Individuals Population module", () => {
    it.skip("Check Individuals Population page", () => {});
    it("Check Individuals Population Details page", () => {
      cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
      cy.get("div").contains("Individuals");
      cy.get('[data-cy="table-title"]').contains("Individuals");
      cy.get('[data-cy="individual-table-row"]').first().click({ force: true });
      cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
      cy.get('[data-cy="page-header-container"]').contains("Individual ID:");
      cy.get("h6").contains("Bio Data");
      cy.get("h6").contains("Vulnerabilities");
      cy.get("h6").contains("Activity Log");
    });
  });
  describe("Component tests Individuals Population", () => {
    context("Individuals Population Filters", () => {
      it.skip("Individuals Population Search filter", () => {
        // ToDo
      });
      it.skip("Individuals Population Programme filter", () => {
        // ToDo
      });
      it.skip("Individuals Population Residence Status filter", () => {
        // ToDo
      });
      it.skip("Individuals Population Admin Level 2 filter", () => {
        // ToDo
      });
      it.skip("Individuals Size filter", () => {
        // ToDo
      });
      it.skip("Individuals Population Sorted by filter", () => {
        // ToDo
      });
      it.skip("Individuals Population Status filter", () => {
        // ToDo
      });
    });
  });
  describe.skip("E2E tests Individuals Population", () => {});

  describe.skip("Regression tests Individuals Population", () => {});
});
