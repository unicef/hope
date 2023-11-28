import Feedback from "../../page-objects/pages/grievance/feedback.po";
import FeedbackDetailsPage from "../../page-objects/pages/grievance/details_feedback_page.po";
import NewFeedback from "../../page-objects/pages/grievance/new_feedback.po";
import NewTicket from "../../page-objects/pages/grievance/new_ticket.po";
import GrievanceDetailsPage from "../../page-objects/pages/grievance/details_grievance_page.po";
import ErrorPage from "../../page-objects/404.po";

let error404Page = new ErrorPage();
let feedbackPage = new Feedback();
let feedbackDetailsPage = new FeedbackDetailsPage();
let newFeedbackPage = new NewFeedback();
let grievanceNewTicketPage = new NewTicket();
let grievanceDetailsPage = new GrievanceDetailsPage();

describe("Grievance - Feedback", () => {
  before(() => {
    cy.checkIfLoggedIn();
  });
  beforeEach(() => {
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

  describe.skip("Component tests Feedback", () => {
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
        feedbackDetailsPage.clickMenuButtonFeedback();
      });
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
      describe.skip("Feedback Created by filter", () => {
        before(() => {
          feedbackPage.getButtonSubmitNewFeedback().click();
          newFeedbackPage.chooseOptionByName("Positive");
          newFeedbackPage.getButtonNext().click();
          newFeedbackPage.getHouseholdTab().should("be.visible");
          newFeedbackPage.getButtonNext().click();
          newFeedbackPage.getReceivedConsent().click();
          newFeedbackPage.getButtonNext().click();
          newFeedbackPage.getLabelCategory().contains("Feedback");
          newFeedbackPage.getDescription().type("Test Description");
          newFeedbackPage.getButtonNext().contains("Save").click();
          feedbackPage.clickMenuButtonFeedback();
        });
        after(() => {
          cy.initScenario("init_clear");
          cy.adminLogin();
        });
        it("Feedback Created by filter", () => {
          cy.scenario([
            "Go to Grievance page",
            "Press Feedback button in menu",
            "Create new feedback cy Cypress User",
            "Press Feedback button in menu",
            "Choose Type Cypress User",
            "Press button Apply",
            `Check if Tickets List is empty`,
            "Press button Clear",
            "Choose Type Root Rootkowski",
            "Press button Apply",
            `Check if Tickets List has 2 row`,
          ]);
          feedbackPage.useCreatedByFilter("Cypress User");
          feedbackPage.expectedNumberOfRows(1);
          feedbackPage.getButtonClear().click();
          feedbackPage.expectedNumberOfRows(3);
          feedbackPage.useCreatedByFilter("Root Rootkowski");
          feedbackPage.expectedNumberOfRows(2);
        });
      });
    });
    context("Create New Feedback", () => {
      it("Create New Feedback - Negative Feedback", () => {
        cy.scenario([
          "Go to Grievance page",
          "Press Feedback button in menu",
          "Press Submit New Feedback button",
          "Choose Issue Type: Negative Feedback",
          "Press button Next",
          "Choose household and press Next button",
          "Select 'Received Consent*' and press Next button",
          "Fill all fields",
          `Press button Save`,
          `Check data in details page`,
        ]);
        feedbackPage.getButtonSubmitNewFeedback().click();
        newFeedbackPage.chooseOptionByName("Negative");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getHouseholdTableRows(0).click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getReceivedConsent().click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getLabelCategory().contains("Feedback");
        newFeedbackPage.getIssueType().contains("Negative Feedback");
        newFeedbackPage.getDescription().type("Test Description");
        newFeedbackPage.getComments().type("Test comment");
        newFeedbackPage.getAdminAreaAutocomplete().click();
        newFeedbackPage.getOption().contains("Zari").click();
        newFeedbackPage.getInputArea().type("Test Area");
        newFeedbackPage.getInputLanguage().type("Random Language");
        newFeedbackPage.getButtonNext().contains("Save").click();
        feedbackDetailsPage.getDescription().contains("Test Description");
        feedbackDetailsPage.getComments().contains("Test comment");
        feedbackDetailsPage.getAdministrativeLevel2().contains("Zari");
        feedbackDetailsPage.getCategory().contains("Feedback");
        feedbackDetailsPage.getIssueType().contains("Negative Feedback");
        feedbackDetailsPage.getAreaVillagePayPoint().contains("Test Area");
        feedbackDetailsPage.getLanguagesSpoken().contains("Random Language");
        feedbackDetailsPage.getTitlePage().contains("Feedback");
      });
      it("Create New Feedback - Positive Feedback", () => {
        cy.scenario([
          "Go to Grievance page",
          "Press Feedback button in menu",
          "Press Submit New Feedback button",
          "Choose Issue Type: Positive Feedback",
          "Press button Next",
          "Choose household and press Next button",
          "Select 'Received Consent*' and press Next button",
          "Fill all fields",
          `Press button Save`,
          `Check data in details page`,
        ]);
        feedbackPage.getButtonSubmitNewFeedback().click();
        newFeedbackPage.chooseOptionByName("Positive");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getHouseholdTableRows(1).click();
        newFeedbackPage.getLookUpIndividual().click();
        newFeedbackPage.getIndividualTableRow(0).click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getReceivedConsent().click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getLabelCategory().contains("Feedback");
        // ToDo Add after fix bug: XXX
        // newFeedbackPage.getIssueType().contains("Positive Feedback");
        newFeedbackPage.getDescription().type("Test Description");
        newFeedbackPage.getComments().type("Test comment");
        newFeedbackPage.getAdminAreaAutocomplete().click();
        newFeedbackPage.getOption().contains("Zari").click();
        newFeedbackPage.getInputArea().type("Test Area");
        newFeedbackPage.getInputLanguage().type("Random Language");
        newFeedbackPage.getButtonNext().contains("Save").click();
        feedbackDetailsPage.getDescription().contains("Test Description");
        feedbackDetailsPage.getComments().contains("Test comment");
        feedbackDetailsPage.getAdministrativeLevel2().contains("Zari");
        feedbackDetailsPage.getCategory().contains("Feedback");
        feedbackDetailsPage.getIssueType().contains("Positive Feedback");
        feedbackDetailsPage.getAreaVillagePayPoint().contains("Test Area");
        feedbackDetailsPage.getLanguagesSpoken().contains("Random Language");
        feedbackDetailsPage.getTitlePage().contains("Feedback");
      });
      it("Create New Feedback - Cancel", () => {
        cy.scenario([
          "Go to Grievance page",
          "Press Feedback button in menu",
          "Press Submit New Feedback button",
          "Press button Cancel",
          "Press Submit New Feedback button",
          "Press button Next",
          "Issue Type is required",
          "Choose Issue Type: Positive Feedback",
          "Press button Next",
          "Press button Back",
          "Press button Next",
          "Press button Cancel",
          "Press Submit New Feedback button",
          "Choose Issue Type: Positive Feedback",
          "Press button Next",
          "Choose household and individual",
          "Press button Next",
          "Press button Back",
          "Press button Next",
          "Press button Cancel",
          "Press Submit New Feedback button",
          "Choose Issue Type: Positive Feedback",
          "Press button Next",
          "Choose household and individual",
          "Press button Next",
          "Select 'Received Consent*'",
          "Press button Next",
          "Press button Back",
          "Press button Next",
          "Press button Cancel",
          "Press Submit New Feedback button",
          "Choose Issue Type: Positive Feedback",
          "Press button Next",
          "Choose household and individual",
          "Press button Next",
          "Select 'Received Consent*'",
          "Press button Next",
          "Fill all fields",
          `Press button Save`,
        ]);
        feedbackPage.getButtonSubmitNewFeedback().click();
        newFeedbackPage.getButtonBack().should("be.disabled");
        newFeedbackPage.getButtonCancel().click();
        feedbackPage.getTitlePage().contains("Feedback");
        feedbackPage.getButtonSubmitNewFeedback().click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getInputIssueType().contains("Issue Type is required");
        newFeedbackPage.chooseOptionByName("Positive");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getButtonCancel().click();
        feedbackPage.getButtonSubmitNewFeedback().click();
        newFeedbackPage.chooseOptionByName("Negative");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getButtonBack().click();
        newFeedbackPage.chooseOptionByName("Positive");
        newFeedbackPage.getButtonBack().should("be.disabled");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getReceivedConsent().click();
        newFeedbackPage.getButtonBack().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getReceivedConsent().click();
        newFeedbackPage.getButtonCancel().click();
        feedbackPage.getButtonSubmitNewFeedback().click();
        newFeedbackPage.chooseOptionByName("Negative");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getReceivedConsent().click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getDescription().should("be.visible");
        newFeedbackPage.getButtonBack().click();
        newFeedbackPage.getReceivedConsent().should("be.visible");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getDescription().should("be.visible");
        newFeedbackPage.getButtonCancel().click();
        feedbackPage.getButtonSubmitNewFeedback().click();
        newFeedbackPage.chooseOptionByName("Negative");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getReceivedConsent().click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getDescription().type("Test Description");
        newFeedbackPage.getButtonNext().contains("Save").click();
      });
      it("Create Linked Ticket", () => {
        cy.scenario([
          "Go to Grievance page",
          "Press Feedback button in menu",
          "Press Submit New Feedback button",
          "Choose Issue Type: Negative Feedback",
          "Press button Next",
          "Choose household and individual",
          "Press Next button",
          "Select 'Received Consent*' and press Next button",
          "Fill all fields",
          `Press button Save`,
          `Check data in details page`,
          `Press Create Linked Ticket`,
          "Create Grievance Ticket",
          "Check If Grievance Ticket is linked to Feedback",
        ]);
        feedbackPage.getButtonSubmitNewFeedback().click();
        newFeedbackPage.chooseOptionByName("Negative");
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getHouseholdTab().should("be.visible");
        newFeedbackPage.getHouseholdTableRows(1).click();
        newFeedbackPage.getLookUpIndividual().click();
        newFeedbackPage.getIndividualTableRow(0).click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getReceivedConsent().click();
        newFeedbackPage.getButtonNext().click();
        newFeedbackPage.getDescription().type("Test Description");
        newFeedbackPage.getButtonNext().contains("Save").click();
        feedbackDetailsPage
          .getTitlePage()
          .contains("Feedback ID:")
          .then(($textFeedbackID) => {
            const feedbackID = $textFeedbackID.text().split("ID: ")[1];
            feedbackDetailsPage.getButtonCreateLinkedTicket().click();
            grievanceNewTicketPage.chooseCategory("Referral");
            grievanceNewTicketPage.getButtonNext().click();
            grievanceNewTicketPage.getReceivedConsent().click();
            grievanceNewTicketPage.getButtonNext().click();
            grievanceNewTicketPage
              .getDescription()
              .type("Test Grievance Ticket");
            grievanceNewTicketPage.getButtonNext().contains("Save").click();
            grievanceDetailsPage
              .getTitle()
              .contains("Ticket ID: ")
              .then(($textGrievanceID) => {
                const grievanceID = $textGrievanceID.text().split("ID: ")[1];
                feedbackPage.clickMenuButtonFeedback();
                feedbackPage
                  .getRows()
                  .contains(feedbackID)
                  .parent()
                  .parent()
                  .contains(grievanceID)
                  .parent()
                  .parent()
                  .click();
                feedbackDetailsPage
                  .getLabelTicketId()
                  .contains(grievanceID)
                  .click();
              });
          });
      });
    });

    context("Edit Feedback", () => {
      it.skip("Edit Feedback", () => {});
    });
  });
  describe.skip("E2E tests Feedback", () => {
    // ToDo: Enable after fix
    it.skip("404 Error page - refresh", () => {
      cy.scenario([
        "Go to Grievance page",
        "Go to Feedback page",
        "Click first row",
        "Delete part of URL",
        "Check if 404 occurred",
        "Press button refresh",
        "Check if 404 occurred",
      ]);
      feedbackPage.getRows().first().click();
      feedbackDetailsPage.getTitlePage().contains("Feedback");
      cy.url().then((url) => {
        let newUrl = url.slice(0, -10);
        cy.visit(newUrl);
        error404Page
          .getPageNoFound()
          .its("response.statusCode")
          .should("eq", 200);
        error404Page.getButtonRefresh().click();
        error404Page
          .getPageNoFound()
          .its("response.statusCode")
          .should("eq", 200);
      });
    });
  });
  describe("Regression tests Feedback", () => {
    it("171154: GPF: Program is still optional in Feedback", () => {
      cy.scenario([
        "Go to Feedback page",
        "Press button Submit New Feedback",
        "Choose type (e.g. Negative) and press Next button",
        "Choose Household and press Next button",
        "Select Received Consent* and press Next button",
      ]);
      feedbackPage.getButtonSubmitNewFeedback().click();
      newFeedbackPage.chooseOptionByName("Negative");
      newFeedbackPage.getButtonNext().click();
      newFeedbackPage.getHouseholdTab().should("be.visible");
      newFeedbackPage.getHouseholdTableRows(0).click();
      newFeedbackPage.getButtonNext().click();
      newFeedbackPage.getReceivedConsent().click();
      newFeedbackPage.getButtonNext().click();
      newFeedbackPage.getLabelCategory().contains("Feedback");
      newFeedbackPage.getIssueType().contains("Negative Feedback");
      cy.get("label").should("not.contain", "Programme Title");
    });
    it("174517: Check clear cache", () => {
      cy.scenario([
        "Go to Feedback page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      feedbackPage.clearCache();
      feedbackPage.checkElementsOnPage();
    });
  });
});
