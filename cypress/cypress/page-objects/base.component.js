import addContext from "mochawesome/addContext";

export default class BaseComponent {
  // Menu Locators
  buttonPaymentVerification =
    'span[class="MuiTypography-root MuiListItemText-primary MuiTypography-body1 MuiTypography-displayBlock"]';
  buttonTargeting =
    'span[class="MuiTypography-root MuiListItemText-primary MuiTypography-body1 MuiTypography-displayBlock"]';
  // Texts
  buttonPaymentVerificationText = "Payment Verification";
  buttonTargetingText = "Targeting";

  // Elements
  getMenuButtonPaymentVerification = () =>
    cy.get(this.buttonPaymentVerification);
  getMenuButtonTargeting = () => cy.get(this.buttonTargeting);

  clickMenuButtonPaymentVerification() {
    this.getMenuButtonPaymentVerification()
      .contains(this.buttonPaymentVerificationText)
      .click();
  }

  clickMenuButtonTargeting() {
    this.getMenuButtonTargeting().contains(this.buttonTargetingText).click();
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
