import ErrorPage from "../../page-objects/404.po";
import CommunicationPage from "../../page-objects/pages/accountability/communication.po";

let error404Page = new ErrorPage();
let communicationPage = new CommunicationPage();

describe("Accountability - Communication", () => {
  before(() => {
    cy.checkIfLoggedIn();
  });
  beforeEach(() => {
    cy.navigateToHomePage();
    communicationPage.getMenuButtonAccountability();
    communicationPage.getMenuButtonSurveys();
  });

  describe("Smoke tests Accountability - Communication", () => {
    it("Check Communication page", () => {
      cy.scenario([
        "Go to Accountability page",
        "Elements of Accountability menu are visible",
        "Go to Communication page",
        "Check if all elements on page exist",
      ]);
    });
  });
});
