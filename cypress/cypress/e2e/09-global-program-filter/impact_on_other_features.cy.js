import AllProgrammes from "../../page-objects/pages/all_programmes/all_programmes.po";
import Grievance from "../../page-objects/pages/grievance/grievance_tickets.po";
import Targeting from "../../page-objects/pages/targeting/targeting.po";
import PaymentModule from "../../page-objects/pages/payment_module/payment_module.po";
import Feedback from "../../page-objects/pages/grievance/feedback.po";
import PopulationIndividuals from "../../page-objects/pages/population_module/population_individuals.po";
import PopulationHouseholds from "../../page-objects/pages/population_module/population_households.po";
import PaymentVerification from "../../page-objects/pages/payment_verification/payment_verification.po";
import RegistrationDataImport from "../../page-objects/pages/registration_data_import/registration_data_import.po";

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
    it("GPF - Payment Verification", () => {
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
  });

  describe.skip("Regression tests Country Dashboard", () => {});
});
