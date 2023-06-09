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
}
