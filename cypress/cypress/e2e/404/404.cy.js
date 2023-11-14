import Grievance from "../../page-objects/pages/grievance/grievance_tickets.po";
import GrievanceDetailsPage from "../../page-objects/pages/grievance/details_grievance_page.po";
import ErrorPage from "../../page-objects/404.po";

let grievancePage = new Grievance();
let grievanceDetailsPage = new GrievanceDetailsPage();
let error404Page = new ErrorPage();

describe("404 Page", () => {
  before(function () {
    cy.initScenario("init_clear");
    cy.fixture("grievance_new_ticket").as("newTicket");
    cy.adminLogin();
    cy.navigateToHomePage();
    grievancePage.clickMenuButtonGrievance();
  });
  beforeEach(() => {
    grievancePage.clickMenuButtonGrievanceTickets();
  });

  describe("E2E tests 404 Page", () => {
    afterEach(function () {
      Cypress.session.clearCurrentSessionData();
      cy.adminLogin();
      cy.navigateToHomePage();
      grievancePage.clickMenuButtonGrievance();
    });
    it("404 Error page - refresh", () => {
      cy.scenario([
        "Go to Grievance page",
        "Click first row",
        "Delete part of URL",
        "Check if 404 occurred",
        "Press button refresh",
        "Check if 404 occurred",
      ]);
      grievancePage.chooseTicketListRow(0, "GRV-0000001").click();
      grievanceDetailsPage.getTitle().contains(grievanceDetailsPage.textTitle);
      cy.url().then((url) => {
        let newUrl = url.slice(0, -10);
        cy.visit(newUrl);
        cy.intercept("/404/**").as("error404");
        error404Page.getPageNoFound();
        error404Page.getButtonRefresh().click();
        cy.wait("@error404").its("response.statusCode").should("eq", 200);
        error404Page.getPageNoFound();
      });
    });
    it("404 Error page - go to country dashboard", () => {
      cy.scenario([
        "Go to Grievance page",
        "Click first row",
        "Delete part of URL",
        "Check if 404 occurred",
        "Press go to country dashboard button",
        "Check if country dashboard opened",
      ]);
      grievancePage.chooseTicketListRow(0, "GRV-0000001").click();
      grievanceDetailsPage.getTitle().contains(grievanceDetailsPage.textTitle);
      cy.url().then((url) => {
        let newUrl = url.slice(0, -10);
        cy.visit(newUrl);
        cy.intercept("/404/**").as("error404");
        error404Page.getPageNoFound();
        error404Page.getGoToCountryDashboard().click();
        cy.wait("@error404").its("response.statusCode").should("eq", 200);
        cy.get("h5").contains("Dashboard");
      });
    });
  });
});
