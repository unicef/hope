import ProgramManagement from "../../page-objects/pages/program_management/program_management.po";
import PMDetailsPage from "../../page-objects/pages/program_management/details_page.po";
import ErrorPage from "../../page-objects/404.po";

let error404Page = new ErrorPage();
let programManagement = new ProgramManagement();
let programManagementDetailsPage = new PMDetailsPage();

describe("Program Management", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
    cy.get("span").contains("Programme Management").click();
  });

  describe("Smoke tests Program Management", () => {
    it.skip("Check Program Management page", () => {});
    it.skip("Check Program Management Details page", () => {});
  });
  describe("Component tests Program Management", () => {
    // ToDo: Refactor in second milestone
    it("Create a program", () => {
      cy.scenario([
        "Go to Programme Management page",
        "Create new programme",
        "Check if programme was created properly",
      ]);
      cy.get("h5").should("contain", "Programme Management");
      cy.get('[data-cy="button-new-program"]').click({ force: true });
      cy.get("h6").should("contain", "Set-up a new Programme");
      cy.uniqueSeed().then((seed) => {
        const programName = `test program ${seed}`;
        cy.get('[data-cy="input-programme-name"]').type(programName);
        cy.get('[data-cy="input-cash-assist-scope"]').first().click();
        cy.get('[data-cy="select-option-Unicef"]').click();
        cy.get('[data-cy="input-sector"]').first().click();
        cy.get('[data-cy="select-option-Multi Purpose"]').click();
        cy.get('[data-cy="input-data-collecting-type"]').first().click();
        cy.get('[data-cy="select-option-Partial"]').click();
        cy.get('[data-cy="input-start-date"]').click().type("2023-01-01");
        cy.get('[data-cy="input-end-date"]').click().type("2033-12-30");
        cy.get('[data-cy="input-description"]')
          .first()
          .click()
          .type("test description");
        cy.get('[data-cy="input-budget"]')
          .first()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}9999");
        cy.get('[data-cy="input-admin-area"]').click().type("Some Admin Area");
        cy.get('[data-cy="input-population-goal"]')
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}4000");
        cy.get('[data-cy="button-save"]').click({ force: true });
        cy.get("h6").should("contain", "Programme Details");
        cy.get('[data-cy="button-activate-program"]').click({ force: true });
        cy.get('[data-cy="button-activate-program-modal"]').click({
          force: true,
        });
        cy.get('[data-cy="status-container"]').should("contain", "ACTIVE");
      });
    });
    it("Edit Program", () => {
      cy.scenario([
        "Go to Programme Management page",
        "Choose Programme",
        "Edit Programme",
        "Check if programme was edited properly",
      ]);
      cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true });
      cy.get('[data-value="ACTIVE"]').click({ force: true });
      cy.get('[data-cy="button-filters-apply"]').click();
      cy.get('[data-cy="status-container"]').should("contain", "ACTIVE");
      cy.get('[data-cy="status-container"]').eq(0).click({ force: true });
      cy.contains("EDIT PROGRAMME").click({ force: true });
      cy.uniqueSeed().then((seed) => {
        const editedProgramName = `Edited program ${seed}`;
        cy.get('[data-cy="input-programme-name"]')
          .clear()
          .type(editedProgramName);
        cy.get('[data-cy="input-cash-assist-scope"]').first().click();
        cy.get('[data-cy="select-option-Unicef"]').click();
        cy.get('[data-cy="input-sector"]').first().click();
        cy.get('[data-cy="select-option-Multi Purpose"]').click();
        cy.get('[data-cy="input-start-date"]').click().type("2023-01-10");
        cy.get('[data-cy="input-end-date"]').click().type("2033-12-31");
        cy.get('[data-cy="input-description"]')
          .first()
          .clear()
          .type("Edit Test description");
        cy.get('[data-cy="input-budget"]')
          .first()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}8888");
        cy.get('[data-cy="input-admin-area"]').clear().type("Some Admin Area");
        cy.get('[data-cy="input-population-goal"]')
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}2000");
        cy.get('[data-cy="button-save"]').click({ force: true });
        cy.get("h5").should("contain", editedProgramName);
      });
    });
    it("Finish Program", () => {
      cy.scenario([
        "Go to Programme Management page",
        "Choose active Programme",
        "Finish Programme",
        "Check if programme was finished properly",
      ]);
      cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true });
      cy.get('[data-value="ACTIVE"]').click({ force: true });
      cy.get('[data-cy="button-filters-apply"]').click();
      cy.reload();
      cy.get('[data-cy="status-container"]').should("contain", "ACTIVE");
      cy.get('[data-cy="status-container"]').eq(0).click({ force: true });
      cy.contains("Finish Programme").click({ force: true });
      cy.get('[data-cy="button-finish-program"]').eq(1).click({ force: true });
      cy.get('[data-cy="status-container"]').should("contain", "FINISHED");
    });
    it("Reactivate Program", () => {
      cy.scenario([
        "Go to Programme Management page",
        "Choose finished Programme",
        "Reactivate Programme",
        "Check if programme was reactivated properly",
      ]);
      cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true });
      cy.get('[data-value="FINISHED"]').click({ force: true });
      cy.get('[data-cy="button-filters-apply"]').click();
      cy.reload();
      cy.get('[data-cy="status-container"]').should("contain", "FINISHED");
      cy.get('[data-cy="status-container"]').eq(0).click({ force: true });
      cy.contains("Reactivate").eq(0).click({ force: true });
      cy.get(".MuiDialogActions-root > .MuiButton-contained").click({
        force: true,
      });
      cy.get('[data-cy="status-container"]').should("contain", "ACTIVE");
    });
    it.skip("Remove Program", () => {});
    it.skip("Activate Program", () => {});
    it.skip("Reactivate Program", () => {});
    it.skip("Open in Cashassist", () => {});

    context("PM Filters", () => {
      it.skip("PM Programme filter", () => {});
      it.skip("PM Status filter", () => {});
      it.skip("PM FSP filter", () => {});
      it.skip("PM Start Date filter", () => {});
      it.skip("PM End Date filter", () => {});
      it.skip("PM Sector filter", () => {});
      it.skip("PM Num. of Households filter", () => {});
      it.skip("PM Budget (USD) filter", () => {});
    });
  });
  describe("E2E tests Program Management", () => {
    it("404 Error page", () => {
      cy.scenario([
        "Go to Program Management page",
        "Click first row",
        "Delete part of URL",
        "Check if 404 occurred",
      ]);
      programManagement.getTableRow().first().click();
      programManagementDetailsPage.getTitle().contains("Draft Program");
      cy.url().then((url) => {
        let newUrl = url.slice(0, -10);
        cy.visit(newUrl);
        error404Page.getPageNoFound();
      });
    });
  });

  describe("Regression tests Program Management", () => {
    it("174517: Check clear cash", () => {
      cy.scenario([
        "Go to Program Management page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      programManagement.clearCache();
      cy.get("h5").should("contain", "Programme Management");
    });
  });
});
