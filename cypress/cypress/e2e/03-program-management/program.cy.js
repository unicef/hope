import ProgramManagement from "../../page-objects/pages/program_management/program_management.po";
import PMDetailsPage from "../../page-objects/pages/program_management/details_page.po";
import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";

let programManagement = new ProgramManagement();
let programManagementDetails = new PMDetailsPage();
let programDetails = new ProgramDetails();

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
    it("Create a program", () => {
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
      programManagement.getStatusFilter().click();
      programManagement.getOption().contains("Active").click();
      programManagement.getButtonApply().click();
      programManagement.getStatusContainer().should("contain", "ACTIVE");
      programManagement
        .getTableRowByName(programManagement.textTestProgramm)
        .click();
      programDetails.getButtonEditProgram().click();
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
    it("Finish Program", () => {
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
  describe.skip("E2E tests Program Management", () => {});

  describe("Regression tests Program Management", () => {
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
  });
});
