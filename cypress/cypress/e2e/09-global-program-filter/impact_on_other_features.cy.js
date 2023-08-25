import AllProgrammes from "../../page-objects/pages/all_programmes/all_programmes.po";
import Grievance from "../../page-objects/pages/grievance/grievance_tickets.po";

let programmesPage = new AllProgrammes();
let grievancePage = new Grievance();

describe("Global Program Filter - Impacts", () => {
  beforeEach(() => {
    programmesPage.navigateToProgrammePage();
  });
  describe("E2E tests GPF impacts", () => {
    it.only("GPF - Registration data import Verification", () => {
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      grievancePage.clickMenuButtonGrievance();
      grievancePage.clickMenuButtonGrievanceTickets();
      grievancePage.getTicketListRow().should("have.length", 4);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      grievancePage.clickMenuButtonGrievance();
      grievancePage.clickMenuButtonGrievanceTickets();
      grievancePage.getTicketListRow().should("have.length", 0);
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
