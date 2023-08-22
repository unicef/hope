import AllProgrammes from "../../page-objects/pages/all_programmes/all_programmes.po";

let programmesPage = new AllProgrammes();

describe("Country Dashboard", () => {
  beforeEach(() => {
    programmesPage.navigateToProgrammePage();
  });
  describe.skip("E2E tests Country Dashboard", () => {
    it("Registration data import Verification", () => {});
    it("Program management", () => {});
    it("Targeting", () => {});
    it("Payment module", () => {});
    it("Payment Verification", () => {});
    it("Population module", () => {});
    it("Grievance", () => {});
    it("Feedback", () => {});
  });

  describe.skip("Regression tests Country Dashboard", () => {});
});
