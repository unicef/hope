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

Then('I should see the side panel with Communication option', () => {
  cy.get('span')
    .contains('Accountability', { timeout: 10000 })
    .click({ force: true });
  cy.get('span').contains('Communication', { timeout: 10000 });
});

When('I click on Communication option', () => {
  cy.get('span')
    .contains('Communication', { timeout: 10000 })
    .click({ force: true });
});

Then('I should see the Communication page', () => {
  cy.get('h5').contains('Communication');
});

When('I click the New Message button', () => {
  cy.get('[data-cy="button-communication-create-new"]').click({ force: true });
});

Then('I should see the New Message page', () => {
  cy.get('h5').contains('New Message');
});

When('I fill in the form and save', () => {
  cy.get('[data-cy="input-checkbox-household"]').eq(0).click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-title"]').eq(0).click().type('Some title');
  cy.get('[data-cy="input-body"]').eq(0).click().type('Some message');
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="button-confirm"]').click({ force: true });
});

Then('I should see the Message details page', () => {
  cy.contains('MSG');
});
