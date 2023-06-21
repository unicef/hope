import Feedback from "../../page-objects/pages/grievance/feedback.po";
import FDetailsPage from "../../page-objects/pages/grievance/details_feedback_page.po";
import NewFeedback from "../../page-objects/pages/grievance/new_feedback.po";

let feedbackPage = new Feedback();
let feedbackDetailsPage = new FDetailsPage();
let newFeedbackPage = new NewFeedback();

describe("Grievance - Feedback", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
  });

  describe("Smoke tests Feedback", () => {
    it.skip("Check Feedback page", () => {});
    it.skip("Check Feedback Details page", () => {});
    it.skip("Check Feedback New Ticket page", () => {});
  });

  describe("Component tests Feedback", () => {
    context("Feedback Filters", () => {
      it.skip("Feedback Search filter", () => {
        // ToDo
      });
      it.skip("Feedback Issue Type filter", () => {
        // ToDo
      });
      it.skip("Grievance Created by filter", () => {
        // ToDo
      });
      it.skip("Grievance Creation Date filter", () => {
        // ToDo
      });
    });
    context("Create New Feedback", () => {
      it.skip("Create New Feedback - Negative Feedback", () => {
        // ToDo
      });
      it.skip("Create New Feedback - Positive Feedback", () => {
        // ToDo
      });
      it.skip("Create New Feedback - Cancel", () => {
        // ToDo
      });
    });

    context("Edit Feedback", () => {
      it.skip("Edit Feedback", () => {
        // ToDo
      });
    });
  });
  describe.skip("E2E tests Feedback", () => {});

  describe.skip("Regression tests Feedback", () => {});
});
