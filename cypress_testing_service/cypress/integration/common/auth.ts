import { Given } from 'cypress-cucumber-preprocessor/steps';

Given('I login to AD as {word}', (role: string) => {
  const { username, password } = Cypress.env(role);
  const loginUrl = Cypress.env('loginUrl');

  cy.log(`Signing in user to A as ${role}`);
  cy.loginToAD(username, password, loginUrl);

  Cypress.env('logged_in_user_username', username);
  cy.visit(loginUrl);
});

Given('I login once to AD as {word}', () => {
  // do nothing, perform login procedure in scope of
  // before.ts located together with spec file,
  // so that login would be invoked only once before
  // all scenarios for the given feature
});

Given('I am not logged in to AD', () => {
  cy.request('/api/logout');
});
