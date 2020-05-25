import { Given } from 'cypress-cucumber-preprocessor/steps';

Given('I login to AD as {word}', (role: string) => {
  const { username, password } = Cypress.env(role);
  const loginUrl = Cypress.env('loginUrl');

  cy.log(`Signing in user to A as ${role}`);
  cy.loginToAD(username, password, loginUrl);

  cy.visit(loginUrl);
  cy.wrap({ username }).as('loggedUser');
});

Given('I login once to AD as {word}', () => {
  // do nothing, perform login procedure in scope of
  // support/before.ts, so that login would be invoked
  //  only once before all scenarios for the given feature
});
