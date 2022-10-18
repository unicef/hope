import { When, Then, Given } from 'cypress-cucumber-preprocessor/steps';

Given('I am authenticated', () => {
  cy.visit('/api/unicorn/');
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});
const clearCache = () => {
  cy.get('[data-cy="menu-user-profile"]').click();
  cy.get('[data-cy="menu-item-clear-cache"]').click();
  // hack to let the page reload
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
};

When('I visit the main dashboard', () => {
  cy.visit('/');
  clearCache();
});

Then('I should see the side panel with Surveys option', () => {
  cy.get('span')
    .contains('Accountability', { timeout: 10000 })
    .click({ force: true });
  cy.get('span').contains('Surveys', { timeout: 10000 });
});

When('I click on Surveys option', () => {
  cy.get('span').contains('Surveys', { timeout: 10000 }).click({ force: true });
});

Then('I should see the Surveys page', () => {
  cy.get('h5').contains('Surveys');
});

When('I click the New Survey button', () => {
  cy.get('[data-cy="button-new-survey"]').click({ force: true });
  cy.get('[data-cy="menu-item-rapid-pro"]').click();
});

Then('I should see the New Survey page', () => {
  cy.get('h5').contains('New Survey');
});

When('I fill in the form and save', () => {
  cy.get('[data-cy="input-radio-program"]').eq(0).click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-title"]').click().type('Some title');
  cy.get('[data-cy="button-submit"]').click({ force: true });
});

Then('I should see the Feedback details page', () => {
  cy.contains('Survey ID:');
});
