import AllProgrammes from "../../page-objects/pages/all_programmes/all_programmes.po";
import Grievance from "../../page-objects/pages/grievance/grievance_tickets.po";
import Targeting from "../../page-objects/pages/targeting/targeting.po";
import PaymentModule from "../../page-objects/pages/payment_module/payment_module.po";
import Feedback from "../../page-objects/pages/grievance/feedback.po";
import PopulationIndividuals from "../../page-objects/pages/population_module/population_individuals.po";
import PopulationHouseholds from "../../page-objects/pages/population_module/population_households.po";
import PaymentVerification from "../../page-objects/pages/payment_verification/payment_verification.po";
import RegistrationDataImport from "../../page-objects/pages/registration_data_import/registration_data_import.po";
import GrievanceDashboard from "../../page-objects/pages/grievance/grievance_dashboard.po";
import GrievanceDetailsPage from "../../page-objects/pages/grievance/details_grievance_page.po";

let grievanceDashboard = new GrievanceDashboard();
let grievanceDetailsPage = new GrievanceDetailsPage();
let programmesPage = new AllProgrammes();
let grievancePage = new Grievance();
let targetingPage = new Targeting();
let paymentModulePage = new PaymentModule();
let feedbackPage = new Feedback();
let populationIndividuals = new PopulationIndividuals();
let populationHouseholds = new PopulationHouseholds();
let paymentVerification = new PaymentVerification();
let registrationDataImport = new RegistrationDataImport();

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
    it("GPF - Registration data import Verification", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (Test Programme)",
        "Go to Registration data import page",
        "Check row list: 2 rows",
        "Choose program (Draft Programme)",
        "Go to Registration data import page",
        "Check row list: 0 rows",
      ]);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      registrationDataImport.getMenuButtonRegistrationDataImport().click();
      registrationDataImport.getTicketListRow().should("have.length", 2);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      registrationDataImport.getMenuButtonRegistrationDataImport().click();
      registrationDataImport.getTicketListRow().should("have.length", 0);
    });
    it("GPF - Registration data import - import button", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (Test Programme)",
        "Go to Registration data import page",
        "Import button is active",
        "Choose program (Draft Programme)",
        "Go to Registration data import page",
        "Import button is disabled",
      ]);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      registrationDataImport.getMenuButtonRegistrationDataImport().click();
      registrationDataImport.getButtonImport().should("not.be.disabled");
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      registrationDataImport.getMenuButtonRegistrationDataImport().click();
      registrationDataImport.getButtonImport().should("be.disabled");
    });
    it("GPF - Program details", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (" + programmesPage.textTestProgramm + ")",
        "Header Title: " + programmesPage.textTestProgramm,
        "Choose program (" + programmesPage.textDraftProgram + ")",
        "Header Title: " + programmesPage.textDraftProgram,
      ]);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      programmesPage.getHeaderTitle().contains(programmesPage.textTestProgramm);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textDraftProgram)
        .click();
      programmesPage.getHeaderTitle().contains(programmesPage.textDraftProgram);
    });
    it("GPF - Targeting", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (" + programmesPage.textTestProgramm + ")",
        "Go to Targeting page",
        "Check row list: 2 rows",
        "Choose program (" + programmesPage.textDraftProgram + ")",
        "Go to Targeting page",
        "Check row list: 0 rows",
      ]);
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
    it("GPF - Payment module", () => {
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
    it("GPF - Payment Verification", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (" + programmesPage.textTestProgramm + ")",
        "Go to Payment Verification page",
        "Check row list: 1 rows",
        "Choose program (" + programmesPage.textDraftProgram + ")",
        "Go to Payment Verification page",
        "Check row list: 0 rows",
      ]);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      paymentVerification.clickMenuButtonPaymentVerification();
      paymentVerification.getTicketListRow().should("have.length", 1);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      paymentVerification.clickMenuButtonPaymentVerification();
      paymentVerification.getTicketListRow().should("have.length", 0);
    });
    it("GPF - Population module", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (" + programmesPage.textTestProgramm + ")",
        "Go to Population module page",
        "Go to Individual page",
        "Check row list: 6 rows",
        "Go to Households page",
        "Check row list: 2 rows",
        "Choose program (" + programmesPage.textDraftProgram + ")",
        "Go to Individual page",
        "Check row list: 0 rows",
        "Go to Households page",
        "Check row list: 0 rows",
      ]);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      populationIndividuals.clickNavIndividuals();
      populationIndividuals.getTicketListRow().should("have.length", 6);
      populationHouseholds.getMenuButtonHouseholds().click();
      populationHouseholds.getTicketListRow().should("have.length", 2);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textDraftProgram)
        .click();
      populationIndividuals.clickNavIndividuals();
      populationIndividuals.getTicketListRow().should("have.length", 0);
      populationHouseholds.getMenuButtonHouseholds().click();
      populationHouseholds.getTicketListRow().should("have.length", 0);
    });
    it("GPF - Grievance", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (" + programmesPage.textTestProgramm + ")",
        "Go to Grievance page",
        "Check row list: 6 rows",
        "Choose program (" + programmesPage.textDraftProgram + ")",
        "Go to Grievance page",
        "Check row list: 0 rows",
      ]);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      grievancePage.clickMenuButtonGrievance();
      grievancePage.clickMenuButtonGrievanceTickets();
      grievancePage.getTicketListRow().should("have.length", 6);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      grievancePage.clickMenuButtonGrievance();
      grievancePage.clickMenuButtonGrievanceTickets();
      grievancePage.getTicketListRow().should("have.length", 0);
    });
    it("GPF - Feedback", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (" + programmesPage.textTestProgramm + ")",
        "Go to Feedback page",
        "Check row list: 6 rows",
        "Choose program (" + programmesPage.textDraftProgram + ")",
        "Go to Feedback page",
        "Check row list: 0 rows",
      ]);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage
        .getProgrammesOptions()
        .contains(programmesPage.textTestProgramm)
        .click();
      feedbackPage.clickMenuButtonGrievance();
      feedbackPage.clickMenuButtonFeedback();
      feedbackPage.getTicketListRow().should("have.length", 2);
      programmesPage.getGlobalProgramFilter().click();
      programmesPage.getProgrammesOptions().contains("Draft Program").click();
      feedbackPage.clickMenuButtonGrievance();
      feedbackPage.clickMenuButtonFeedback();
      feedbackPage.getTicketListRow().should("have.length", 0);
    });
    it("GPF - Grievance Dashboard", () => {
      cy.scenario([
        "Go to main page (All programmes set)",
        "Choose program (" + programmesPage.textTestProgramm + ")",
        "Go to Grievance and close one ticket",
        "Go to Grievance Dashboard page",
        "Check data",
        "Choose program (" + programmesPage.textDraftProgram + ")",
        "Go to Grievance Dashboard page",
        "Check if data properly changed",
      ]);
      grievancePage.navigateToProgrammePage();
      grievancePage.clickMenuButtonGrievance();
      grievanceDashboard.getTicketListRow().contains("GRV-0000005").click();
      grievanceDetailsPage.getButtonCloseTicket().click();
      grievanceDetailsPage.getButtonConfirm().click();
      grievanceDetailsPage.getTicketStatus().contains("Closed");
      grievanceDetailsPage.clickMenuButtonGrievanceDashboard();
      grievanceDashboard.getTotalTickets().contains("7");
      grievanceDashboard.getSystemGeneratedTickets().contains("1");
      grievanceDashboard.getUserGeneratedTickets().contains("6");
      grievanceDashboard.getSystemGeneratedClosed().contains("0");
      grievanceDashboard.getUserGeneratedClosed().contains("1");
      grievanceDashboard
        .getSystemGeneratedResolutions()
        .should("contain.text", "0 days");
      grievanceDashboard
        .getUserGeneratedResolutions()
        .should("not.have.text", "0 days");
      grievancePage.navigateToProgrammePage("Draft Program");
      grievancePage.clickMenuButtonGrievance();
      grievanceDetailsPage.clickMenuButtonGrievanceDashboard();
      grievanceDashboard.getTotalTickets().contains("0");
      grievanceDashboard.getSystemGeneratedTickets().contains("0");
      grievanceDashboard.getUserGeneratedTickets().contains("0");
      grievanceDashboard.getSystemGeneratedClosed().contains("0");
      grievanceDashboard.getUserGeneratedClosed().contains("0");
      grievanceDashboard
        .getSystemGeneratedResolutions()
        .should("contain.text", "0 days");
      grievanceDashboard
        .getUserGeneratedResolutions()
        .should("contain.text", "0 days");
    });
  });

  describe.skip("Regression tests GPF", () => {});
});
