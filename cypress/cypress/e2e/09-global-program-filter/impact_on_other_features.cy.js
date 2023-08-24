import AllProgrammes from "../../page-objects/pages/all_programmes/all_programmes.po";

let programmesPage = new AllProgrammes();

describe("Global Program Filter - Impacts", () => {
  beforeEach(() => {
    programmesPage.navigateToProgrammePage();
  });
  describe("E2E tests GPF impacts", () => {
    it.only("GPF - Registration data import Verification", () => {
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm);
    });
    it.skip("GPF - Program management", () => {});
    it.skip("GPF - Targeting", () => {});
    it.skip("GPF - Payment module", () => {});
    it.skip("GPF - Payment Verification", () => {});
    it.skip("GPF - Population module", () => {});
    it.skip("GPF - Grievance", () => {});
    it.skip("GPF - Feedback", () => {});
  });

  describe.skip("Regression tests Country Dashboard", () => {});
});
