import { Given } from 'cypress-cucumber-preprocessor/steps';

Given('I login to AD as {word}', (role: string) => {
  const { adUsername, adPassword } = Cypress.env(role);
  const loginUrl = Cypress.env('loginUrl');

  cy.log(`Signing in user to A as ${role}`);
  cy.loginToAD(adUsername, adPassword, loginUrl);

  cy.visit(loginUrl);
  cy.wrap({ username: adUsername }).as('loggedUser');
});

Given('I am authenticated as a {word}', (role: string) => {
  cy.loadUserCookies({ role });
  cy.loadUserLocalStorage({ role });

  cy.visit('/');
  cy.getByTestId('business-area-container').should('be.visible');
});

Given('I login once to AD as {word}', () => {
  // do nothing, perform login procedure using before hooks,
  // so that login would be invoked only once before all scenarios
  // for the given feature
});
