import BaseComponent from "./base.component";

export default class ErrorPage extends BaseComponent {
  // Locators
  // Texts
  Text404Error = "Oops! Page Not Found";
  // Elements
  getPageNoFound = () => cy.get("h1").contains(this.Text404Error);
}
