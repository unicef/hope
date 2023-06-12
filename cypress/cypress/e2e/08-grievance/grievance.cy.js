import Grievance from "../../page-objects/pages/grievance/grievance.po";
import GDetailsPage from "../../page-objects/pages/grievance/details_page.po";
import NewTicket from "../../page-objects/pages/grievance/new_ticket.po";

let g = new Grievance();
let gd = new GDetailsPage();
let gnt = new NewTicket();

describe("Grievance", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
  });

  describe("Smoke tests Grievance", () => {
    it.skip("Check Grievance page", () => {
      // Scenario:
      // 1. Go to Grievance page
      // 2. Check if all elements on page exist
    });
  });

  describe("Component tests Grievance", () => {
    context("Export", () => {
      it.skip("ToDo", () => {});
    });

    context("Grievance Filters", () => {
      it.skip("Grievance Programme filter", () => {
        // ToDo
      });
      it.skip("Grievance Status filter", () => {
        // ToDo
      });
      it.skip("Grievance FSP filter", () => {
        // ToDo
      });
      it.skip("Grievance Creation Date filter", () => {
        // ToDo
      });
      it.skip("Grievance Admin Level 2 filter", () => {
        // ToDo
      });
      it.skip("Grievance Category filter", () => {
        // ToDo
      });
      it.skip("Grievance Assignee filter", () => {
        // ToDo
      });
      it.skip("Grievance Similarity Score filter", () => {
        // ToDo
      });
      it.skip("Grievance Registration Date Import filter", () => {
        // ToDo
      });
      it.skip("Grievance Preferred language filter", () => {
        // ToDo
      });
    });
    context("Create New Ticket", () => {
      it.skip("Create New Ticket - Data Change - Add Individual", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Data Change - Household Data Update", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Data Change - Individual Data Update", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Data Change - Withdraw Individual", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Data Change - Withdraw Household", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Grievance Complaint", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Negative Feedback", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Positive Feedback", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Referral", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Bribery, corruption or kickback", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Data breach", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Conflict of interest", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Fraud and forgery", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Fraud involving misuse of programme funds by third party", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Gross mismanagement", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Harassment and abuse of authority", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Inappropriate staff conduct", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Miscellaneous", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Personal disputes", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Sexual harassment and sexual exploitation", () => {
        // ToDo
      });
      it.skip("Create New Ticket - Sensitive Grievance - Unauthorized use, misuse or waste of UNICEF property or funds", () => {
        // ToDo
      });

      it.skip("Create New Ticket - Cancel", () => {
        // ToDo
      });
    });

    context("Edit Ticket", () => {
      it.skip("Edit Ticket", () => {
        // ToDo
      });
    });

    context("Assign Ticket", () => {
      it.skip("Assign to me", () => {
        // ToDo
      });
      it.skip("Set to in progress", () => {
        // ToDo
      });
      it.skip("Send for approval", () => {
        // ToDo
      });
      it.skip("Send back", () => {
        // ToDo
      });
      it.skip("Close ticket", () => {
        // ToDo
      });
      it.skip("Add new note", () => {
        // ToDo
      });
      it.skip("Create Linked Ticket from details page", () => {
        // ToDo
      });
      it.skip("Mark duplicate from details page", () => {
        // ToDo
      });
    });
  });
  describe.skip("E2E tests Grievance", () => {});

  describe.skip("Regression tests Grievance", () => {});
});
