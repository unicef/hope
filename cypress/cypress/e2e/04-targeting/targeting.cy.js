import Targeting from "../../page-objects/pages/targeting/targeting.po";
import TDetailsPage from "../../page-objects/pages/targeting/details_page.po";
import CreateNew from "../../page-objects/pages/targeting/create_new.po";
import ErrorPage from "../../page-objects/404.po";

let error404Page = new ErrorPage();
let targetingPage = new Targeting();
let targetingDetailsPage = new TDetailsPage();
let targetingCreateNewPage = new CreateNew();

let programName = "TargetingProgram";

describe("Targeting", () => {
  beforeEach(() => {
    cy.initScenario("targeting");
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
      cy.scenario([
        "Go to Targeting Details page",
        "Check if all elements on page exist",
      ]);
      targetingPage.selectStatus("Open");
      targetingPage.getTargetPopulationsRows().should("have.length", 1);
      targetingPage.chooseTargetPopulationRow(0).click();
      targetingDetailsPage.checkElementsOnPage("OPEN");
    });
    it("Check Targeting New Ticket page", () => {
      cy.scenario([
        "Go to Targeting New Ticket page",
        "Check if all elements on page exist",
      ]);
      targetingPage.getButtonCreateNew().click();
      targetingCreateNewPage.checkElementsOnPage();
    });
  });

  describe("Component tests Targeting", () => {
    context("Create new target population", () => {
      // TODO: Refactor in second milestone
      it("Can visit the targeting page and create a target population", () => {
        cy.scenario([
          "Go to Targeting New Ticket page",
          "Press Create New button",
          "Fill name field",
          "Press button household rule",
          "Check if all elements on page exist",
        ]);
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

          // TODO: Refactor in second milestone
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
      it.skip("Targeting Search filter", () => {});
      it.skip("Targeting Status filter", () => {});
      it.skip("Targeting Programme filter", () => {});
      it.skip("Targeting Number of Households filter", () => {});
    });
    context("Edit targeting", () => {
      it.skip("Edit", () => {});
    });
    context("Rebuild targeting", () => {
      it.skip("Rebuild", () => {});
    });
    context("Lock targeting", () => {
      it.skip("Lock", () => {});
    });
    context("Unlock targeting", () => {
      it.skip("Unlock", () => {});
    });
    context("Mark ready targeting", () => {
      it.skip("Mark ready", () => {});
    });
  });
  describe.skip("E2E tests Targeting", () => {
    it("404 Error page", () => {
      cy.scenario([
        "Go to Targeting page",
        "Click first row",
        "Delete part of URL",
        "Check if 404 occurred",
      ]);
      targetingPage.getTargetPopulationsRows().first().click();
      targetingDetailsPage.checkElementsOnPage("OPEN");
      cy.url().then((url) => {
        let newUrl = url.slice(0, -10);
        cy.visit(newUrl);
        error404Page.getPageNoFound().should("be.visible");
      });
    });
  });

  describe("Regression tests Targeting", () => {
    it("174517: Check clear cash", () => {
      cy.scenario([
        "Go to Targeting page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      targetingPage.clearCache();
      targetingPage.checkElementsOnPage();
    });
  });
});
