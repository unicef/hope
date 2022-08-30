import { When, Then, And, Given } from 'cypress-cucumber-preprocessor/steps';

Given('I am authenticated', () => {
  cy.visit('/api/unicorn/');
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});

When('I visit the main dashboard', () => {
  cy.visit('/');
});

Then('I should see the side panel with Programme Management option', () => {
  cy.get('span').contains('Programme Management', { timeout: 10000 });
});

When('I click on Programme Management option', () => {
  cy.get('span').contains('Programme Management').click();
});

Then('I should see the Programs page', () => {
  cy.get('h5').contains('Programme Management');
});

When('I click the New Programme button', () => {
  cy.get('[data-cy="button-new-program"]').click({ force: true });
});

Then('I should see the Set-up a new Programme modal', () => {
  cy.get('h6').contains('Set-up a new Programme');
});

When('I fill out all the form fields', () => {
  const uniqueSeed = Date.now().toString();

  cy.get('[data-cy="input-programme-name"]').type(`test program ${uniqueSeed}`);
  cy.get('[data-cy="input-cash-assist-scope"]').first().click();
  cy.get('[data-cy="select-option-1"]').click();
  cy.get('[data-cy="input-sector"]').first().click();
  cy.get('[data-cy="select-option-1"]').click();
  cy.get('[data-cy="input-start-date"]').click().type('2022-12-12');
  cy.get('[data-cy="input-end-date"]').click().type('2022-12-23');
  cy.get('[data-cy="input-description"]')
    .first()
    .click()
    .type('test description');
  cy.get('[data-cy="input-budget"]')
    .first()
    .click()
    .type('{backspace}{backspace}{backspace}{backspace}9999');
  cy.get('[data-cy="input-admin-area"]').click().type('Some Admin Area');
  cy.get('[data-cy="input-population-goal"]')
    .click()
    .type('{backspace}{backspace}{backspace}{backspace}4000');
});

And('I click the save button', () => {
  cy.get('[data-cy="button-save"]').click({ force: true });
  cy.wait(3000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Program details page', () => {
  cy.get('h6').contains('Programme Details');
});
