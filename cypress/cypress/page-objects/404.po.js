import BaseComponent from "./base.component";

export default class ErrorPage extends BaseComponent {
  // Locators
  pageNotFound = "h1";
  buttonRefresh = "button";
  buttonCountryDashboard = 'button[data-cy="button-go-back"]';

  // Texts
  text404Error = "Access Denied";
  textRefresh = "REFRESH PAGE";
  textGoTo = "GO BACK";
  // Elements
  getPageNoFound = () => cy.get(this.pageNotFound).contains(this.text404Error);
  getButtonRefresh = () =>
    cy.get(this.buttonRefresh).contains(this.textRefresh);
  getGoToCountryDashboard = () =>
    cy.get(this.buttonCountryDashboard).contains(this.textGoTo);
}
