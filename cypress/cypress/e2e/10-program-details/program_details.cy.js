import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";

let programDetails = new ProgramDetails();

describe("Program Details", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
  });

  after(() => {
    cy.initScenario("init_clear");
    cy.adminLogin();
  });

  describe("Smoke tests Program Details", () => {
    it("Check Program Details page", () => {
      cy.scenario([
        "Go to Program Details page (Active program chosen)",
        "Check if all elements on page exist",
        "Change program to Draft program",
        "Check if all elements on page exist",
      ]);
      programDetails.getTableTitle().should("be.visible");
      programDetails.getCashPlanTableRow().should("have.length", 2);
      programDetails.getLabelAdministrativeAreasOfImplementation();
      programDetails.getButtonEditProgram().should("be.visible");
      programDetails.getLabelTotalNumberOfHouseholds().should("be.visible");
      programDetails.getLabelIndividualsData().should("be.visible");
      programDetails.getLabelCASH().should("be.visible");
      programDetails.getLabelDescription().should("be.visible");
      programDetails.getLabelFrequencyOfPayment().should("be.visible");
      programDetails.getLabelScope().should("be.visible");
      programDetails.getLabelSector().should("be.visible");
      programDetails.getLabelENDDATE().should("be.visible");
      programDetails.getLabelSTARTDATE().should("be.visible");
      programDetails.getStatusContainer().should("be.visible");
      programDetails.getLabelStatus().should("be.visible");
      programDetails.getPageHeaderTitle().should("be.visible");
      programDetails.getTablePagination().should("be.visible");
      programDetails.getTableLabel().should("be.visible");
      programDetails.getButtonCopyProgram().should("be.visible");

      programDetails.getGlobalProgramFilter().click();
      programDetails
        .getProgrammesOptions()
        .contains(programDetails.textDraftProgram)
        .click();

      programDetails.getButtonActivateProgram().should("be.visible");
      programDetails.getButtonRemoveProgram().should("be.visible");

      programDetails
        .getLabelAdministrativeAreasOfImplementation()
        .should("be.visible");
      programDetails.getButtonEditProgram().should("be.visible");
      programDetails.getLabelTotalNumberOfHouseholds().should("be.visible");
      programDetails.getLabelIndividualsData().should("be.visible");
      programDetails.getLabelCASH().should("be.visible");
      programDetails.getLabelDescription().should("be.visible");
      programDetails.getLabelFrequencyOfPayment().should("be.visible");
      programDetails.getLabelScope().should("be.visible");
      programDetails.getLabelSector().should("be.visible");
      programDetails.getLabelENDDATE().should("be.visible");
      programDetails.getLabelSTARTDATE().should("be.visible");
      programDetails.getStatusContainer().should("be.visible");
      programDetails.getLabelStatus().should("be.visible");
      programDetails.getPageHeaderTitle().should("be.visible");
      programDetails.getButtonCopyProgram().should("be.visible");
      programDetails.getTablePagination().should("not.exist");
      programDetails.getTableLabel().should("not.exist");
      programDetails.getTableTitle().should("not.exist");
      programDetails.getCashPlanTableRow().should("not.exist");
    });
  });

  describe("Component tests Program Details", () => {
    it("Finish Program", () => {
      cy.scenario([
        "Go to Program Details page (Active program chosen)",
        "Press Finish Programme button",
        "Press Finish button on popup",
        "Check Status",
      ]);
      programDetails.getButtonFinishProgram().click();
      programDetails.getButtonFinishProgram().eq(1).click();
      programDetails.getStatusContainer().should("contain", "FINISHED");
    });
    it("Reactivate Program", () => {
      cy.scenario([
        "Go to Program Details page (Finished program chosen)",
        "Press Reactivate button",
        "Press Reactivate button on popup",
        "Check Status",
      ]);
      programDetails.getButtonDataCyButtonReactivateProgram().click();
      programDetails.getButtonDataCyButtonReactivateProgramPopup().click();
      programDetails.getStatusContainer().should("contain", "ACTIVE");
    });
    it.skip("Remove Program", () => {});
    it.skip("Activate Program", () => {});
    it.skip("Reactivate Program", () => {});
  });

  describe.skip("E2E tests Program Details", () => {});

  describe.skip("Regression tests Program Details", () => {});
});
