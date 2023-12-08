import ProgramManagement from "../../page-objects/pages/program_management/program_management.po";
import PMDetailsPage from "../../page-objects/pages/program_management/details_page.po";
import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";

let programManagement = new ProgramManagement();
let programManagementDetails = new PMDetailsPage();
let programDetails = new ProgramDetails();

describe("Program Management", () => {
  before(() => {
    cy.checkIfLoggedIn();
  });

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
      programManagement
        .getPageHeaderTitle()
        .should("contain", "Programme Management");
      programManagement.getButtonNewProgram().click({ force: true });
      programManagement
        .getDialogTitle()
        .should("contain", "Create Programme");
      cy.uniqueSeed().then((seed) => {
        const programName = `Test Program ${seed}`;
        programManagement.getInputProgrammeName().type(programName);
        programManagement.getInputSector().click()
        programManagement.getSelectOptionByName("Health").click();
        programManagement.getInputDataCollectingType().click();
        programManagement.getSelectOptionByName("Full").click();
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
      // programManagement.getButtonFiltersExpand().click();
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
          .getInputProgrammeName().find("input")
          .clear()
          .type(editedProgramName);
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
        programManagement.getInputAdminArea().find("input").clear().type("Some Admin Area");
        programManagement.getInputCashPlus().uncheck();
        programManagement
          .getInputPopulationGoal()
          .click()
          .type("{backspace}{backspace}{backspace}{backspace}2000");
        programManagement.getButtonSave().click();
        programManagement.getPageHeaderTitle().contains(editedProgramName);
      });
    });

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
    it("174517: Check clear cache", () => {
      cy.scenario([
        "Go to Program Management page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      programManagement.clearCache();
      cy.get("h5").should("contain", "Programme Management");
    });
    it("174707: Create a program without Data Collecting Type", () => {
      programManagement
        .getPageHeaderTitle()
        .should("contain", "Programme Management");
      programManagement.getButtonNewProgram().click({ force: true });
      programManagement
        .getDialogTitle()
        .should("contain", "Create Programme");
      cy.uniqueSeed().then((seed) => {
        const programName = `Test Program ${seed}`;
        programManagement.getInputProgrammeName().type(programName);
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
        cy.get("p").contains("Data Collecting Type is required");
      });
    });
    it("171253 GPF: After delete program it is still visible and clickable in GPF", () => {
      programDetails.navigateToProgrammePage("Draft Program");
      programDetails.getButtonRemoveProgram().click();
      programDetails.getButtonRemoveProgram().eq(1).click();
      programDetails.getGlobalProgramFilter().click();
      programDetails
        .getProgrammesOptions()
        .should("not.contain", "Draft Program");
      cy.url().should("include", "programs/all/list");
    });
  });
});
