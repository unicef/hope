import BaseComponent from "../../base.component";

export default class Login extends BaseComponent {
  // Locators

  // Texts

  // Elements
  navigateToLoginPage() {
    cy.visit("/api/unicorn/");
  }
}
