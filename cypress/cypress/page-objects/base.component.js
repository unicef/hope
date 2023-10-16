export default class BaseComponent {
  // Menu Locators
<<<<<<< HEAD
  buttonPaymentModule = 'a[data-cy="nav-Payment Module"]';
  navRegistrationDataImport = 'a[data-cy="nav-Registration Data Import"]';
  navProgrammePopulation = 'div[data-cy="nav-Programme Population"]';
  navHouseholds = 'a[data-cy="nav-Households"]';
  navIndividuals = 'a[data-cy="nav-Individuals"]';
  navProgrammeManagement = 'a[data-cy="nav-Programme Management"]';
  navProgrammeDetails = 'a[data-cy="nav-Programme Details"]';
  navTargeting = 'a[data-cy="nav-Targeting"]';
  navCashAssist = 'div[data-cy="nav-Cash Assist"]';
  navPaymentModule = 'a[data-cy="nav-Payment Module"]';
  navPaymentVerification = 'a[data-cy="nav-Payment Verification"]';
  navGrievance = 'div[data-cy="nav-Grievance"]';
  navGrievanceTickets = 'a[data-cy="nav-Grievance Tickets"]';
  navGrievanceDashboard = 'a[data-cy="nav-Grievance Dashboard"]';
  navFeedback = 'a[data-cy="nav-Feedback"]';
  navReporting = 'a[data-cy="nav-Reporting"]';
  navProgrammeUsers = 'a[data-cy="nav-Programme Users"]';
  navActivityLog = 'a[data-cy="nav-Activity Log"]';
  navResourcesKnowledgeBase = 'a[data-cy="nav-resources-Knowledge Base"]';
  navResourcesConversations = 'a[data-cy="nav-resources-Conversations"]';
  navResourcesToolsAndMaterials =
    'a[data-cy="nav-resources-Tools and Materials"]';
  navResourcesReleaseNote = 'a[data-cy="nav-resources-Release Note"]';
  headerTitle = 'h5[data-cy="page-header-title"]';
  globalProgramFilter = 'div[data-cy="global-program-filter"]';
  option = 'li[role="option"]';
  ticketListRow = 'tr[role="checkbox"]';
=======
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
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd

  // Texts
  buttonPaymentVerificationText = "Payment Verification";
  buttonPaymentModuleText = "Payment Verification";
  buttonTargetingText = "Targeting";
  buttonPaymentModuleText = "Payment Module";
  buttonGrievanceText = "Grievance";
  buttonGrievanceTicketsText = "Grievance Tickets";
  buttonGrievanceDashboardText = "Grievance Dashboard";
  buttonFeedbackText = "Feedback";
  textTestProgramm = "Test Programm";
  textDraftProgram = "Draft Program";

<<<<<<< HEAD
  // Elements)
  getButtonPaymentModule = () => cy.get(this.buttonPaymentModule);
  getMenuButtonRegistrationDataImport = () =>
    cy.get(this.navRegistrationDataImport);
  getMenuButtonProgrammePopulation = () => cy.get(this.navProgrammePopulation);
  getMenuButtonHouseholds = () => cy.get(this.navHouseholds);
  getMenuButtonIndividuals = () => cy.get(this.navIndividuals);
  getMenuButtonProgrammeManagement = () => cy.get(this.navProgrammeManagement);
  getMenuButtonProgrammeDetails = () => cy.get(this.navProgrammeDetails);
  getMenuButtonCashAssist = () => cy.get(this.navCashAssist);
  getMenuButtonPaymentModule = () => cy.get(this.navPaymentModule);
  getMenuButtonReporting = () => cy.get(this.navReporting);
  getMenuButtonProgrammeUsers = () => cy.get(this.navProgrammeUsers);
  getMenuButtonActivityLog = () => cy.get(this.navActivityLog);
  getMenuButtonResourcesKnowledgeBase = () =>
    cy.get(this.navResourcesKnowledgeBase);
  getMenuButtonResourcesConversations = () =>
    cy.get(this.navResourcesConversations);
  getMenuButtonResourcesToolsAndMaterials = () =>
    cy.get(this.navResourcesToolsAndMaterials);
  getMenuButtonResourcesReleaseNote = () =>
    cy.get(this.navResourcesReleaseNote);
  getMenuButtonPaymentVerification = () => cy.get(this.navPaymentVerification);
  getMenuButtonTargeting = () => cy.get(this.navTargeting);
  getMenuButtonGrievance = () => cy.get(this.navGrievance);
  getMenuButtonGrievanceTickets = () => cy.get(this.navGrievanceTickets);
  getMenuButtonGrievanceDashboard = () => cy.get(this.navGrievanceDashboard);
  getGlobalProgramFilter = () => cy.get(this.globalProgramFilter);
  getMenuButtonFeedback = () => cy.get(this.navFeedback);
=======
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
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
  getHeaderTitle = () => cy.get(this.headerTitle);
  getTicketListRow = () => cy.get(this.ticketListRow);

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

<<<<<<< HEAD
  clickMenuButtonPaymentModule() {
    this.getMenuButtonPaymentModule()
      .contains(this.buttonPaymentModuleText)
      .click();
=======
  clearCache() {
    this.getMenuUserProfile().click();
    this.getMenuItemClearCache().click();
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
  }

  pressEscapeFromElement(element) {
    element.focused().then(($el) => {
      if ($el.length) {
        element.type("{esc}");
      }
    });
  }

  getProgrammesOptions = () => cy.get(this.option);

  navigateToProgrammePage(program = this.textAllProgrammes) {
    cy.visit("/");
    this.getGlobalProgramFilter().click();
    cy.log(`Program: ${program}`);
    this.getProgrammesOptions().contains(program).first().click();
  }
}
