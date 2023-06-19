import Targeting from "../../page-objects/pages/targeting/targeting.po";
import TDetailsPage from "../../page-objects/pages/targeting/details_page.po";
import CreateNew from "../../page-objects/pages/targeting/create_new.po";

let t = new Targeting();
let td = new TDetailsPage();
let tcn = new CreateNew();

let programName = "TargetingProgram";

describe("Targeting", () => {
  beforeEach(() => {
    cy.initScenario("targeting");
    cy.adminLogin();
    cy.navigateToHomePage();
    t.clickMenuButtonTargeting();
  });

  describe("Smoke tests Targeting", () => {
    it.only("Check Targeting page", () => {
      cy.scenario([
        "Go to Payment Targeting page",
        "Check if all elements on page exist",
      ]);
      t.checkElementsOnPage();
    });
    it.skip("Check Targeting Details page", () => {});
    it.skip("Check Targeting New Ticket page", () => {});
  });

  describe("Component tests Targeting", () => {
    context("Create new target population", () => {
      it("Can visit the targeting page and create a target population", () => {
        cy.visit("/");
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
          cy.get('[data-cy="input-program"]').first().click();
          cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
          cy.get(`[data-cy="select-option-${programName}-${seed}"]`).click();
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
      it.skip("Targeting Programme filter", () => {
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
