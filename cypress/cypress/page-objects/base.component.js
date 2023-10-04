export default class BaseComponent {
  // Menu Locators
  buttonPaymentVerification =
    'span[class="MuiTypography-root MuiListItemText-primary MuiTypography-body1 MuiTypography-displayBlock"]';
  buttonTargeting =
    'span[class="MuiTypography-root MuiListItemText-primary MuiTypography-body1 MuiTypography-displayBlock"]';
  buttonPaymentModule = 'a[data-cy="nav-Payment Module"]';
  buttonGrievance = 'div[data-cy="nav-Grievance"]';
  buttonGrievanceTickets = 'a[data-cy="nav-Grievance Tickets"]';
  buttonGrievanceDashboard = 'a[data-cy="nav-Grievance Dashboard"]';
  buttonFeedback = 'a[data-cy="nav-Feedback"]';
  headerTitle = 'h5[data-cy="page-header-title"]';
  menuUserProfile = 'button[data-cy="menu-user-profile"]';
  menuItemClearCache = 'li[data-cy="menu-item-clear-cache"]';

  // Texts
  buttonPaymentVerificationText = "Payment Verification";
  buttonPaymentModuleText = "Payment Verification";
  buttonTargetingText = "Targeting";
  buttonGrievanceText = "Grievance";
  buttonGrievanceTicketsText = "Grievance Tickets";
  buttonGrievanceDashboardText = "Grievance Dashboard";
  buttonFeedbackText = "Feedback";

  // Elements
  getMenuUserProfile = () => cy.get(this.menuUserProfile);
  getMenuItemClearCache = () => cy.get(this.menuItemClearCache);
  getMenuButtonPaymentVerification = () =>
    cy.get(this.buttonPaymentVerification);
  getMenuButtonTargeting = () => cy.get(this.buttonTargeting);
  getButtonPaymentModule = () => cy.get(this.buttonPaymentModule);
  getMenuButtonGrievance = () => cy.get(this.buttonGrievance);
  getMenuButtonGrievanceTickets = () => cy.get(this.buttonGrievanceTickets);
  getMenuButtonGrievanceDashboard = () => cy.get(this.buttonGrievanceDashboard);
  getMenuButtonFeedback = () => cy.get(this.buttonFeedback);
  getHeaderTitle = () => cy.get(this.headerTitle);

  checkGrievanceMenu() {
    this.getMenuButtonGrievanceTickets().should("be.visible");
    this.getMenuButtonGrievanceDashboard().should("be.visible");
    this.getMenuButtonFeedback().should("be.visible");
  }
  clickMenuButtonPaymentVerification() {
    this.getMenuButtonPaymentVerification()
      .contains(this.buttonPaymentVerificationText)
      .click();
  }

  clickMenuButtonGrievance() {
    this.getMenuButtonGrievance().contains(this.buttonGrievanceText).click();
  }

  clickMenuButtonGrievanceTickets() {
    this.getMenuButtonGrievanceTickets()
      .contains(this.buttonGrievanceTicketsText)
      .click();
  }

  clickMenuButtonGrievanceDashboard() {
    this.getMenuButtonGrievanceDashboard()
      .contains(this.buttonGrievanceDashboardText)
      .click();
  }

  clickMenuButtonFeedback() {
    this.getMenuButtonFeedback().contains(this.buttonFeedbackText).click();
  }

  clickMenuButtonTargeting() {
    this.getMenuButtonTargeting().contains(this.buttonTargetingText).click();
  }

  clearCache() {
    this.getMenuUserProfile().click();
    this.getMenuItemClearCache().click();
  }

  pressEscapeFromElement(element) {
    element.focused().then(($el) => {
      if ($el.length) {
        element.type("{esc}");
      }
    });
  }
}
