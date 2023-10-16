import ProgramManagement from "../../page-objects/pages/program_management/program_management.po";
import PMDetailsPage from "../../page-objects/pages/program_management/details_page.po";
<<<<<<< HEAD
import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";

let programManagement = new ProgramManagement();
let programManagementDetails = new PMDetailsPage();
let programDetails = new ProgramDetails();
=======
import ErrorPage from "../../page-objects/404.po";

let error404Page = new ErrorPage();
let programManagement = new ProgramManagement();
let programManagementDetailsPage = new PMDetailsPage();
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd

describe("Program Management", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
    cy.get("span").contains("Programme Management").click();
  });

  after(() => {
    cy.initScenario("init_clear");
    cy.adminLogin();
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
<<<<<<< HEAD
      programManagement
        .getPageHeaderTitle()
        .should("contain", "Programme Management");
      programManagement.getButtonNewProgram().click({ force: true });
      programManagement
        .getDialogTitle()
        .should("contain", "Set-up a new Programme");
=======
      cy.get("h5").should("contain", "Programme Management");
      cy.get('[data-cy="button-new-program"]').click({ force: true });
      cy.get("h6").should("contain", "Set-up a new Programme");
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
      cy.uniqueSeed().then((seed) => {
        const programName = `Test Program ${seed}`;
        programManagement.getInputProgrammeName().type(programName);
        programManagement.getInputCashAssistScope().click();
        programManagement.getSelectOptionUnicef().click();
        programManagement.getInputSector().first().click();
        programManagement.getSelectOptionByName("Multi Purpose").click();
        programManagement.getInputDataCollectingType().click();
        programManagement.getSelectOptionByName("Partial").click();
        programManagement.getInputStartDate().click().type("2023-01-01");
        programManagement.getInputEndDate().click().type("2033-12-30");
        programManagement
          .getInputDescription()
          .first()
          .click()
          .type("test description");
        programManagement
          .getInputBudget()
          .first()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}9999");
        programManagement.getInputAdminArea().click().type("Some Admin Area");
        programManagement
          .getInputPopulationGoal()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}4000");
        programManagement.getButtonSave().click({ force: true });
        programDetails.getPageHeaderTitle().should("contain", programName);
        programDetails.getButtonActivateProgram().click({ force: true });
        programDetails.getButtonActivateProgramModal().click({
          force: true,
        });
        programDetails.getStatusContainer().should("contain", "ACTIVE");
      });
    });
    it("Edit Program", () => {
      cy.scenario([
        "Go to Programme Management page",
        "Choose Programme",
        "Edit Programme",
        "Check if programme was edited properly",
      ]);
<<<<<<< HEAD
      programManagement.getStatusFilter().click();
      programManagement.getOption().contains("Active").click();
      programManagement.getButtonApply().click();
      programManagement.getStatusContainer().should("contain", "ACTIVE");
      programManagement
        .getTableRowByName(programManagement.textTestProgramm)
        .click();
      programDetails.getButtonEditProgram().click();
=======
      cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({ force: true });
      cy.get('[data-value="ACTIVE"]').click({ force: true });
      cy.get('[data-cy="button-filters-apply"]').click();
      cy.get('[data-cy="status-container"]').should("contain", "ACTIVE");
      cy.get('[data-cy="status-container"]').eq(0).click({ force: true });
      cy.contains("EDIT PROGRAMME").click({ force: true });
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
      cy.uniqueSeed().then((seed) => {
        const editedProgramName = `Edited program ${seed}`;
        programManagement
          .getInputProgrammeName()
          .clear()
          .type(editedProgramName);
        programManagement.getInputCashAssistScope().click();
        programManagement.getSelectOptionForPartners().click();
        programManagement.getInputSector().click();
        programManagement.getSelectOptionByName("Health").click();
        programManagement
          .getInputStartDate()
          .click()
          .type("{selectAll}")
          .type("2022-11-02");
        programManagement
          .getInputEndDate()
          .click()
          .type("{selectAll}")
          .type("2077-01-11");
        programManagement
          .getInputDescription()
          .first()
          .clear()
          .type("Edit Test description");
        programManagement
          .getInputBudget()
          .first()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}8888");
        programManagement
          .getInputFrequencyOfPayment()
          .contains("One-off")
          .click();
        programManagement.getInputAdminArea().clear().type("Some Admin Area");
        programManagement.getInputCashPlus().uncheck();
        programManagement
          .getInputPopulationGoal()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}2000");
        programManagement
          .getInputIndividualDataNeeded()
          .find("input")
          .eq(1)
          .click();
        programManagement.getButtonSave().click();
        programManagement.getPageHeaderTitle().contains(editedProgramName);
      });
    });
<<<<<<< HEAD
=======
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
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd

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
<<<<<<< HEAD
    it.skip("174517: Check clear cache", () => {
=======
    it("174517: Check clear cash", () => {
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
      cy.scenario([
        "Go to Program Management page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      programManagement.clearCache();
      cy.get("h5").should("contain", "Programme Management");
    });
<<<<<<< HEAD
    // ToDo: 174707
    it.skip("174707: Create a program without Data Collecting Type", () => {
      programManagement
        .getPageHeaderTitle()
        .should("contain", "Programme Management");
      programManagement.getButtonNewProgram().click({ force: true });
      programManagement
        .getDialogTitle()
        .should("contain", "Set-up a new Programme");
      cy.uniqueSeed().then((seed) => {
        const programName = `Test Program ${seed}`;
        programManagement.getInputProgrammeName().type(programName);
        programManagement.getInputCashAssistScope().click();
        programManagement.getSelectOptionUnicef().click();
        programManagement.getInputSector().first().click();
        programManagement.getSelectOptionByName("Multi Purpose").click();
        programManagement.getInputStartDate().click().type("2023-01-01");
        programManagement.getInputEndDate().click().type("2033-12-30");
        programManagement
          .getInputDescription()
          .first()
          .click()
          .type("test description");
        programManagement
          .getInputBudget()
          .first()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}9999");
        programManagement.getInputAdminArea().click().type("Some Admin Area");
        programManagement
          .getInputPopulationGoal()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}4000");
        programManagement.getButtonSave().click({ force: true });
        programDetails.getPageHeaderTitle().should("contain", programName);
        programDetails.getButtonActivateProgram().click({ force: true });
        programDetails.getButtonActivateProgramModal().click({
          force: true,
        });
        programDetails.getStatusContainer().should("contain", "ACTIVE");
      });
    });
=======
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
  });
});
