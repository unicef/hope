import { Given } from 'cypress-cucumber-preprocessor/steps';

Given('I login to AD as {word}', (role: string) => {
  const { username, password } = Cypress.env(role);
  const loginUrl = Cypress.env('loginUrl');

  cy.log(`Signing in user to A as ${role}`);
  cy.loginToAD(username, password, loginUrl);

  Cypress.env('logged_in_user_username', username);
  cy.visit(loginUrl);
});


