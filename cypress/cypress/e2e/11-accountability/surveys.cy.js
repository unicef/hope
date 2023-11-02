import ErrorPage from "../../page-objects/404.po";
import SurveysPage from "../../page-objects/pages/accountability/communication_page.po";

let error404Page = new ErrorPage();
let surveysPage = new SurveysPage();

describe("Accountability - Surveys", () => {
  before(function () {
    cy.navigateToHomePage();
    surveysPage.clickMenuAccountability();
  });
  beforeEach(() => {
    surveysPage.clickMenuAccountability();
    surveysPage.clickMenuSurveys();
  });

  describe("Smoke tests Accountability - Surveys", () => {
    it("Check Surveys page", () => {
      cy.scenario([
        "Go to Accountability page",
        "Elements of Accountability menu are visible",
        "Go to Surveys page",
        "Check if all elements on page exist",
      ]);
    });
  });
});
