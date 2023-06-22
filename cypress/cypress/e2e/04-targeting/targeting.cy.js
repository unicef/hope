import Targeting from "../../page-objects/pages/targeting/targeting.po";
import TDetailsPage from "../../page-objects/pages/targeting/details_page.po";
import CreateNew from "../../page-objects/pages/targeting/create_new.po";

let targetingPage = new Targeting();
let targetingDetailsPage = new TDetailsPage();
let targetingCreateNewPage = new CreateNew();

let programName = "TargetingProgram";

describe("Targeting", () => {
  beforeEach(() => {
    cy.initScenario("targeting");
    cy.adminLogin();
    cy.navigateToHomePage();
    targetingPage.clickMenuButtonTargeting();
  });

  describe("Smoke tests Targeting", () => {
    it("Check Targeting page", () => {
      cy.scenario([
        "Go to Targeting page",
        "Check if all elements on page exist",
      ]);
      targetingPage.checkElementsOnPage();
    });
    it("Check Targeting Details page", () => {
      targetingPage.selectStatus("Open");
      targetingPage.getTargetPopulationsRows().should("have.length", 1);
      targetingPage.chooseTargetPopulationRow(0).click();
      targetingDetailsPage.checkElementsOnPage("OPEN");
    });
    it("Check Targeting New Ticket page", () => {
      targetingPage.getButtonCreateNew().click();
      targetingCreateNewPage.checkElementsOnPage();
    });
  });

  describe("Component tests Targeting", () => {
    context("Create new target population", () => {
      it("Can visit the targeting page and create a target population", () => {
        cy.navigateToHomePage();
        cy.get("span").contains("Targeting").click();
        cy.get("h5").contains("Targeting");
        cy.get('[data-cy="button-target-population-create-new"]').click({
          force: true,
        });
        cy.uniqueSeed().then((seed) => {
          const targetPopulationName = `test TP ${seed}`;
          cy.get('[data-cy="input-name"]')
            .eq(1)
            .type(targetPopulationName, { force: true });
          cy.get('[data-cy="button-target-population-add-criteria"]').click();

          cy.get('[data-cy="button-household-rule"]', {
            timeout: 10000,
          }).click();
          cy.get('[data-cy="autocomplete-target-criteria"]')
            .click()
            .type("address");

          // TODO
          // cy.contains("Address").click();
          // cy.get('[data-cy="input-filters[0].value"]')
          //   .click()
          //   .type(`TargetingVille-${seed}`);
          // cy.get('[data-cy="button-target-population-add-criteria"]').eq(1).click();
          // cy.get("h6").contains("Households");
          // cy.get(
          //   "[data-cy=button-target-population-create] > .MuiButton-label"
          // ).click();
          // cy.get("h6").contains("Targeting Criteria");
          // cy.get('[data-cy="status-container"]').contains("OPEN");
          // cy.get('[data-cy="button-target-population-lock"]').click({
          //   force: true
          // });
          // cy.get('[data-cy="button-target-population-modal-lock"]').click({
          //   force: true
          // });
          // cy.get("h6").contains("Targeting Criteria");
          // cy.get('[data-cy="status-container"]').contains("LOCKED");
          // cy.get('[data-cy="button-target-population-send-to-hope"]').click({
          //   force: true
          // });
          // cy.get('[data-cy="button-target-population-modal-send-to-hope"]').click();
          // cy.get("h6").contains("Targeting Criteria");
          // cy.get('[data-cy="status-container"]').contains("READY");
        });
      });
    });
    context("Targeting Filters", () => {
      it.skip("Targeting Search filter", () => {
        // ToDo
      });
      it.skip("Targeting Status filter", () => {
        // ToDo
      });
      it.skip("Targeting Number of Households filter", () => {
        // ToDo
      });
    });
    context("Edit targeting", () => {
      it.skip("Edit", () => {
        // ToDo
      });
    });
    context("Rebuild targeting", () => {
      it.skip("Rebuild", () => {
        // ToDo
      });
    });
    context("Lock targeting", () => {
      it.skip("Lock", () => {
        // ToDo
      });
    });
    context("Unlock targeting", () => {
      it.skip("Unlock", () => {
        // ToDo
      });
    });
    context("Mark ready targeting", () => {
      it.skip("Mark ready", () => {
        // ToDo
      });
    });
  });
  describe.skip("E2E tests Targeting", () => {});

  describe.skip("Regression tests Targeting", () => {});
});
