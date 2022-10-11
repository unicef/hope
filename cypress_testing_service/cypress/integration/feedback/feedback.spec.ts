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

Then('I should see the side panel with Feedback option', () => {
  cy.get('span')
    .contains('Accountability', { timeout: 10000 })
    .click({ force: true });
  cy.get('span').contains('Feedback', { timeout: 10000 });
});

When('I click on Feedback option', () => {
  cy.get('span')
    .contains('Feedback', { timeout: 10000 })
    .click({ force: true });
});

Then('I should see the Feedback page', () => {
  cy.get('h5').contains('Feedback');
});

When('I click the Submit New Feedback button', () => {
  cy.get('[data-cy="button-submit-new-feedback"').click({ force: true });
});

Then('I should see the New Feedback page', () => {
  cy.get('h5').contains('New Feedback');
});

When('I fill in the form and save', () => {
  cy.get('[data-cy="select-issueType"]').click();
  cy.contains('Positive feedback').click();
  cy.get('[data-cy="button-submit"]').click();
  cy.get('[data-cy="household-table-row"]').eq(0).click();
  cy.contains('LOOK UP INDIVIDUAL').click({ force: true });
  cy.get('[data-cy="individual-table-row"]').eq(0).click();
  cy.get('[data-cy="button-submit"]').click();
  cy.get('[data-cy="input-address"]').click();
  cy.get('[data-cy="input-admin1"]').click();
  cy.get('[data-cy="input-village"]').click();
  cy.get('[data-cy="input-countryOrigin"]').click();
  cy.get('[data-cy="input-headOfHousehold"]').click();
  cy.get('[data-cy="input-consent"]').click();
  cy.get('[data-cy="button-submit"]').click();
  cy.get('[data-cy="input-description"]').click().type('description');
  cy.get('[data-cy="button-submit"]').click();
});

Then('I should see the Feedback details page', () => {
  cy.contains('Feedback ID:');
});

When('I edit the Feedback and save', () => {
  cy.get('[data-cy="button-edit"]').click({ force: true });
  cy.get('[data-cy="input-description"]').click().type('description EDITED');
  cy.get('[data-cy="button-submit"]').click();
});

Then('I should see the updated Feedback', () => {
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.contains('EDITED');
});
