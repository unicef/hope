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
      [["FED-23-0001", 1, "Feedback ID: FED-23-0001"]].forEach((testData) => {
        it("Grievance Search filter", () => {
          cy.scenario([
            "Go to Grievance page",
            "Press Feedback button in menu",
            'Type in Search filter "Not Exist"',
            "Press button Apply",
            "Check if Tickets List is empty",
            "Press button Clear",
            "Type in Search filter " + testData[0],
            "Press button Apply",
            `Check if Tickets List has ${testData[1]} rows`,
            "Press first row from Ticket List and check data",
            "Come back to Feedback Page",
          ]);
          feedbackPage.useSearchFilter("Not Exist");
          feedbackPage.expectedNumberOfRows(0);
          feedbackPage.getButtonClear().click();
          feedbackPage.useSearchFilter(testData[0]);
          feedbackPage.expectedNumberOfRows(testData[1]);
          feedbackPage.chooseTicketListRow(0, testData[0]).click();
          feedbackDetailsPage.getTitlePage().contains(testData[2]);
        });
      });
      it("Feedback Issue Type filter", () => {
        cy.scenario([
          "Go to Grievance page",
          "Press Feedback button in menu",
          "Choose Type Positive",
          "Press button Apply",
          `Check if Tickets List has 1 row`,
          "Press first row from Ticket List and check data",
          "Come back to Feedback Page",
          "Press button Clear",
          `Check if Tickets List has 2 row`,
          "Choose Type Positive",
          "Press button Apply",
          `Check if Tickets List has 1 row`,
          "Press first row from Ticket List and check data",
          "Come back to Feedback Page",
        ]);
        feedbackPage.useIssueTypeFilter("Positive feedback");
        feedbackPage.expectedNumberOfRows(1);
        feedbackPage.chooseTicketListRow(0, "FED-23-0002").click();
        feedbackDetailsPage.getTitlePage().contains("Feedback ID: FED-23-0002");
        feedbackDetailsPage.pressBackButton();
        feedbackPage.getButtonClear().click();
        feedbackPage.useIssueTypeFilter("Negative feedback");
        feedbackPage.expectedNumberOfRows(1);
        feedbackPage.chooseTicketListRow(0, "FED-23-0001").click();
        feedbackDetailsPage.getTitlePage().contains("Feedback ID: FED-23-0001");
      });
      it("Feedback Created by filter", () => {
        cy.scenario([
          "Go to Grievance page",
          "Press Feedback button in menu",
          "Choose Type cypress@cypress.com",
          "Press button Apply",
          `Check if Tickets List is empty`,
          "Press button Clear",
          "Choose Type root@root.com",
          "Press button Apply",
          `Check if Tickets List has 2 row`,
        ]);
        feedbackPage.useCreatedByFilter("cypress@cypress.com");
        feedbackPage.expectedNumberOfRows(0);
        feedbackPage.getButtonClear().click();
        feedbackPage.useCreatedByFilter("root@root.com");
        feedbackPage.expectedNumberOfRows(2);
      });
      // ToDo: Add after fixed: 168323
      it.skip("Feedback Creation Date filter", () => {
        cy.scenario([
          "Go to Grievance page",
          "Press Feedback button in menu",
          "Type date in creation date filter",
          "Press creation date filter button",
          "Check calendar popup",
          "Press button Apply",
          "Check if Creation date",
          "Choose other day using calendar popup",
          "Press button Apply",
          `Check if Tickets List has 2 rows`,
        ]);
        feedbackPage.changeCreationDateTo("2024-01-01");
        feedbackPage.checkDateFilterTo("2024-01-01");
        feedbackPage.openCreationDateToFilter();
        feedbackPage.checkDateTitleFilter("Mon, Jan 1");
        feedbackPage.getButtonClear().click();
        feedbackPage.changeCreationDateTo("2023-01-30");
        feedbackPage.expectedNumberOfRows(2);
        feedbackPage.openCreationDateToFilter();
        feedbackPage.chooseDayFilterPopup(8);
        feedbackPage.checkDateFilterTo("2023-01-08");
        feedbackPage.getButtonApply().click();
        feedbackPage.expectedNumberOfRows(0);
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
