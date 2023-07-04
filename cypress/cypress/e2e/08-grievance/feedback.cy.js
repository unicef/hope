import Feedback from "../../page-objects/pages/grievance/feedback.po";
import FeedbackDetailsPage from "../../page-objects/pages/grievance/details_feedback_page.po";
import NewFeedback from "../../page-objects/pages/grievance/new_feedback.po";

let feedbackPage = new Feedback();
let feedbackDetailsPage = new FeedbackDetailsPage();
let newFeedbackPage = new NewFeedback();

describe("Grievance - Feedback", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
    feedbackPage.clickMenuButtonGrievance();
    feedbackPage.clickMenuButtonFeedback();
  });

  describe("Smoke tests Feedback", () => {
    it("Check Feedback page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Go to Feedback page",
        "Elements of Grievance menu are visible",
        "Check if all elements on page exist",
      ]);
      feedbackPage.checkGrievanceMenu();
      feedbackPage.checkElementsOnPage();
    });
    it("Check Feedback Details page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Go to Feedback page",
        "Choose first row from Feedbacks List",
        "Check if all elements on details page exist",
      ]);
      feedbackPage.chooseTableRow(0);
      feedbackDetailsPage.checkElementsOnPage();
    });
    it("Check Feedback New Ticket page", () => {
      cy.scenario([
        "Go to Grievance page",
        "Press Submit New Feedback button",
        "Check if all elements on details page exist",
      ]);
      feedbackPage.clickButtonSubmitNewFeedback();
      newFeedbackPage.checkElementsOnPage();
    });
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
