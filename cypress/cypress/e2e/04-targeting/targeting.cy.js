import Targeting from "../../page-objects/pages/targeting/targeting.po";
import TDetailsPage from "../../page-objects/pages/targeting/details_page.po";
import CreateNew from "../../page-objects/pages/targeting/create_new.po";
import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";

let targetingPage = new Targeting();
let targetingDetailsPage = new TDetailsPage();
let targetingCreateNewPage = new CreateNew();
let programDetails = new ProgramDetails();

let programName = "TargetingProgram";

describe("Targeting", () => {
  before(() => {
    cy.checkIfLoggedIn();
  });
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
      // targetingPage.getButtonFiltersExpand().click();
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
      it.skip("Can visit the targeting page and create a target population", () => {
        cy.scenario([
          "Go to Targeting New Ticket page",
          "Press Create New button",
          "Fill name field",
          "Press button household rule",
          "Check if all elements on page exist",
        ]);
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
  describe("E2E tests Targeting", () => {
    it("GPF: Disabled button CREATE NEW when program has draft status", () => {
      targetingPage.navigateToProgrammePage("Draft Program");
      targetingPage.clickMenuButtonTargeting();
      targetingPage.getButtonCreateNew().should("be.visible");
      targetingPage
        .getButtonCreateNew()
        .should("have.attr", "aria-disabled")
        .and("equal", "true");
    });
    it("GPF: Disabled button CREATE NEW when program has finished status", () => {
      targetingPage.navigateToProgrammePage("Draft Program");
      programDetails.getButtonActivateProgram().click();
      programDetails.getButtonActivateProgramModal().click();
      programDetails.getStatusContainer().should("contain", "ACTIVE");
      programDetails.getButtonFinishProgram().click();
      programDetails.getButtonFinishProgram().eq(1).click();
      programDetails.getStatusContainer().should("contain", "FINISHED");
      targetingPage.clickMenuButtonTargeting();
      targetingPage.getButtonCreateNew().should("be.visible");
      targetingPage
        .getButtonCreateNew()
        .should("have.attr", "aria-disabled")
        .and("equal", "true");
    });
  });

  describe("Regression tests Targeting", () => {
    it("173542: GPF: Error occurs after apply empty Number of Households field", () => {
      cy.scenario([
        "Go to Targeting",
        "Fill Number of Households field",
        "Press button Apply",
        "Delete value from Number of Households",
        "Press button Apply",
      ]);
      // targetingPage.getButtonFiltersExpand().click();
      targetingPage.getMaxNumberOfHouseholdsFilter().type("123");
      targetingPage.getMinNumberOfHouseholdsFilter().type("456");
      targetingPage.getApply().click();
      targetingPage
        .getMaxNumberOfHouseholdsFilter()
        .find("input")
        .should("have.value", "123");
      targetingPage
        .getMinNumberOfHouseholdsFilter()
        .find("input")
        .should("have.value", "456");
      targetingPage.getMaxNumberOfHouseholdsFilter().clear();
      targetingPage.getMinNumberOfHouseholdsFilter().clear();
      targetingPage.getApply().click();
      targetingPage
        .getMaxNumberOfHouseholdsFilter()
        .find("input")
        .should("have.value", "");
      targetingPage
        .getMinNumberOfHouseholdsFilter()
        .find("input")
        .should("have.value", "");
      targetingPage.getTargetPopulationsRows().should("have.length", 2);
    });
    it.skip('173541: GPF: Clear button does not work for field "Number of Households" in page Targeting', () => {
      cy.scenario([
        "Go to Targeting",
        "Fill Number of Households field",
        "Press button Clear",
        "Fill Number of Households field",
        "Press button Apply",
        "Press button Clear",
      ]);
      targetingPage.getMaxNumberOfHouseholdsFilter().type("123");
      targetingPage.getMinNumberOfHouseholdsFilter().type("456");
      targetingPage.getClear().click();
      targetingPage
        .getMaxNumberOfHouseholdsFilter()
        .find("input")
        .should("have.value", "");
      targetingPage
        .getMinNumberOfHouseholdsFilter()
        .find("input")
        .should("have.value", "");
      targetingPage.getMaxNumberOfHouseholdsFilter().type("123");
      targetingPage.getMinNumberOfHouseholdsFilter().type("456");
      targetingPage.getApply().click();
      targetingPage.getClear().click();
      targetingPage
        .getMaxNumberOfHouseholdsFilter()
        .find("input")
        .should("have.value", "");
      targetingPage
        .getMinNumberOfHouseholdsFilter()
        .find("input")
        .should("have.value", "");
    });
  });
  describe("Regression tests Targeting", () => {
    it.skip("174517: Check clear cache", () => {
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
