import addContext from "mochawesome/addContext";

export default class BaseComponent {
  // Menu Locators
  buttonPaymentVerification =
    'span[class="MuiTypography-root MuiListItemText-primary MuiTypography-body1 MuiTypography-displayBlock"]';

  // Texts
  buttonPaymentVerificationText = "Payment Verification";

  // Elements
  getMenuButtonPaymentVerification = () =>
    cy.get(this.buttonPaymentVerification);

  clickMenuButtonPaymentVerification() {
    this.getMenuButtonPaymentVerification()
      .contains(this.buttonPaymentVerificationText)
      .click();
  }
  scenario(steps) {
    let outputText = "";
    steps.forEach((step, index) => {
      outputText += index + 1 + ". " + step + "\n";
    });
    Cypress.once("test:after:run", (test) => {
      addContext(
        { test },
        {
          title: "Scenario",
          value: outputText,
        }
      );
    });
  }
}
