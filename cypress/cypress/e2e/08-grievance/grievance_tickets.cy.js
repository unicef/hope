import Grievance from "../../page-objects/pages/grievance/grievance_tickets.po";
import GDetailsPage from "../../page-objects/pages/grievance/details_grievance_page.po";
import NewTicket from "../../page-objects/pages/grievance/new_ticket.po";

let grievancePage = new Grievance();
let grievanceDetailsPage = new GDetailsPage();
let newTicketPage = new NewTicket();

describe("Grievance", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
    grievancePage.clickMenuButtonGrievance();
  });

  describe("Smoke tests Grievance", () => {
    it("Check Grievance page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Elements of Grievance menu are visible",
        "Check if all elements on page exist",
      ]);
      grievancePage.checkGrievanceMenu();
      grievancePage.checkElementsOnUserGeneratedPage();
      grievancePage.checkElementsOnSystemGeneratedPage();
    });
    it("Check Grievance Details page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Press tab: System-Generated",
        "Choose first row from Grievance Tickets List",
        "Check if all elements on details page exists",
      ]);
      grievancePage.getTabSystemGenerated().click();
      cy.url().should("include", "/system-generated");
      // ToDo: After fix bug: XXX
      grievancePage
        .getTicketListRow()
        .eq(0)
        .find("a")
        .contains("GRV-0000001")
        .click();
      grievanceDetailsPage.checkGrievanceMenu();
      grievanceDetailsPage.checkElementsOnPage();
    });
    it("Check Grievance New Ticket page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Press New Ticket button",
        "Check if all elements on details page exists",
      ]);
      grievancePage.getButtonNewTicket().click();
      newTicketPage.checkElementsOnPage();
    });
  });

  describe("Component tests Grievance", () => {
    context("Export", () => {
      it.skip("ToDo", () => {});
    });

    context("Grievance Filters", () => {
      it.skip("Grievance Programme filter", () => {});
      it.skip("Grievance Status filter", () => {});
      it.skip("Grievance FSP filter", () => {});
      it.skip("Grievance Creation Date filter", () => {});
      it.skip("Grievance Admin Level 2 filter", () => {});
      it.skip("Grievance Category filter", () => {});
      it.skip("Grievance Assignee filter", () => {});
      it.skip("Grievance Similarity Score filter", () => {});
      it.skip("Grievance Registration Date Import filter", () => {});
      it.skip("Grievance Preferred language filter", () => {});
    });
    context("Create New Ticket", () => {
      it.skip("Create New Ticket - Data Change - Add Individual", () => {});
      it.skip("Create New Ticket - Data Change - Household Data Update", () => {});
      it.skip("Create New Ticket - Data Change - Individual Data Update", () => {});
      it.skip("Create New Ticket - Data Change - Withdraw Individual", () => {});
      it.skip("Create New Ticket - Data Change - Withdraw Household", () => {});
      it.skip("Create New Ticket - Grievance Complaint", () => {});
      it.skip("Create New Ticket - Negative Feedback", () => {});
      it.skip("Create New Ticket - Positive Feedback", () => {});
      it.skip("Create New Ticket - Referral", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Bribery, corruption or kickback", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Data breach", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Conflict of interest", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Fraud and forgery", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Fraud involving misuse of programme funds by third party", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Gross mismanagement", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Harassment and abuse of authority", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Inappropriate staff conduct", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Miscellaneous", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Personal disputes", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Sexual harassment and sexual exploitation", () => {});
      it.skip("Create New Ticket - Sensitive Grievance - Unauthorized use, misuse or waste of UNICEF property or funds", () => {});

      it.skip("Create New Ticket - Cancel", () => {});
    });

    context("Edit Ticket", () => {
      it.skip("Edit Ticket", () => {});
    });

    context("Assign Ticket", () => {
      it.skip("Assign to me", () => {});
      it.skip("Set to in progress", () => {});
      it.skip("Send for approval", () => {});
      it.skip("Send back", () => {});
      it.skip("Close ticket", () => {});
      it.skip("Add new note", () => {});
      it.skip("Create Linked Ticket from details page", () => {});
      it.skip("Mark duplicate from details page", () => {});
    });
  });
  describe.skip("E2E tests Grievance", () => {});

  describe("Regression tests Grievance", () => {
    // ToDo: Enable
    xit('164824 GM: Cannot select a row except texts from "Ticket ID" column.', () => {
      grievancePage.getTabSystemGenerated().click();
      cy.url().should("include", "/system-generated");
    });
  });
});
