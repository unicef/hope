import ProgramDetails from "../../page-objects/pages/program_details/program_details.po";

let programDetails = new ProgramDetails();

describe("Program Details", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
  });

  describe("Smoke tests Program Details", () => {
    it.skip("Check Program Details page", () => {
      // Scenario:
      // 1. Go to Program Details page
      // 2. Check if all elements on page exist
    });
  });

  describe("Component tests Program Details", () => {});

  describe.skip("E2E tests Program Details", () => {});

  describe.skip("Regression tests Program Details", () => {});
});
