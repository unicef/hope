import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";

let programDetails = new ProgramDetails();

describe("Program Details", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
  });

  describe("Smoke tests Program Details", () => {
    it.only("Check Program Details page", () => {
      cy.scenario([
        "1. Go to Program Details page (Active program chosen)",
        "2. Check if all elements on page exist",
        "3. Change program to Draft program",
        "4. Check if all elements on page exist",
      ]);
      programDetails.getTableTitle().should("be.visible");
      programDetails.getTashPlanTableRow().should("have.length", 1);
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
      programDetails.getTashPlanTableRow().should("not.exist");
    });
  });

  describe("Component tests Program Details", () => {});

  describe.skip("E2E tests Program Details", () => {});

  describe.skip("Regression tests Program Details", () => {});
});
