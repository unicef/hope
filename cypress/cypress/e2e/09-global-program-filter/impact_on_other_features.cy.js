import AllProgrammes from "../../page-objects/pages/all_programmes/all_programmes.po";
import Grievance from "../../page-objects/pages/grievance/grievance_tickets.po";
import Targeting from "../../page-objects/pages/targeting/targeting.po";
import PaymentModule from "../../page-objects/pages/payment_module/payment_module.po";
import Feedback from "../../page-objects/pages/grievance/feedback.po";

let programmesPage = new AllProgrammes();
let grievancePage = new Grievance();
let targetingPage = new Targeting();
let paymentModulePage = new PaymentModule();
let feedbackPage = new Feedback();

describe("Global Program Filter - Impacts", () => {
  before(() => {
    cy.initScenario("init_clear");
    cy.adminLogin();
    cy.navigateToHomePage();
  });
  beforeEach(() => {
    programmesPage.navigateToProgrammePage();
  });
  describe("E2E tests GPF impacts", () => {
    it.skip("GPF - Registration data import Verification", () => {});
    it.skip("GPF - Program management", () => {});
    it("GPF - Targeting", () => {
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      targetingPage.clickMenuButtonTargeting();
      targetingPage.getTicketListRow().should("have.length", 2);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      targetingPage.clickMenuButtonTargeting();
      targetingPage.getTicketListRow().should("have.length", 0);
    });
    // ToDo: Add after fix 171383:
    it.skip("GPF - Payment module", () => {
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      paymentModulePage.clickMenuButtonPaymentModule();
      paymentModulePage.getTicketListRow().should("have.length", 2);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      paymentModulePage.clickMenuButtonPaymentModule();
      paymentModulePage.getTicketListRow().should("have.length", 0);
    });
    it.skip("GPF - Payment Verification", () => {});
    it.skip("GPF - Population module", () => {});
    it("GPF - Grievance", () => {
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
    it("GPF - Feedback", () => {
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      feedbackPage.clickMenuButtonGrievance();
      feedbackPage.clickMenuButtonGrievanceTickets();
      feedbackPage.getTicketListRow().should("have.length", 2);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      feedbackPage.clickMenuButtonGrievance();
      feedbackPage.clickMenuButtonGrievanceTickets();
      feedbackPage.getTicketListRow().should("have.length", 0);
    });
  });

  describe.skip("Regression tests Country Dashboard", () => {});
});
