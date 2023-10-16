import BaseComponent from "./base.component";

export default class ErrorPage extends BaseComponent {
  // Locators
  pageNotFound = "h1";
  buttonRefresh = "button";
  buttonCountryDashboard = "a";

  // Texts
  text404Error = "Oops! Page Not Found";
  textRefresh = "REFRESH PAGE";
  textGoTo = "GO TO COUNTRY DASHBOARD";
  // Elements
  getPageNoFound = () => cy.get(this.pageNotFound).contains(this.text404Error);
  getButtonRefresh = () =>
    cy.get(this.buttonRefresh).contains(this.textRefresh);
  getGoToCountryDashboard = () =>
    cy.get(this.buttonCountryDashboard).contains(this.textGoTo);
}
