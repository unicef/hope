export default class BaseComponent {
  // Menu Locators
  buttonPaymentVerification =
    'span[class="MuiTypography-root MuiListItemText-primary MuiTypography-body1 MuiTypography-displayBlock"]';
  buttonTargeting =
    'span[class="MuiTypography-root MuiListItemText-primary MuiTypography-body1 MuiTypography-displayBlock"]';
  buttonGrievance = 'div[data-cy="nav-Grievance"]';
  // Texts
  buttonPaymentVerificationText = "Payment Verification";
  buttonTargetingText = "Targeting";
  buttonGrievanceText = "Grievance";

  // Elements
  getMenuButtonPaymentVerification = () =>
    cy.get(this.buttonPaymentVerification);
  getMenuButtonTargeting = () => cy.get(this.buttonTargeting);
  getMenuButtonGrievance = () => cy.get(this.buttonGrievance);

  clickMenuButtonPaymentVerification() {
    this.getMenuButtonPaymentVerification()
      .contains(this.buttonPaymentVerificationText)
      .click();
  }

  clickMenuButtonGrievance() {
    this.getMenuButtonGrievance().contains(this.buttonGrievanceText).click();
  }

  clickMenuButtonTargeting() {
    this.getMenuButtonTargeting().contains(this.buttonTargetingText).click();
  }
}
