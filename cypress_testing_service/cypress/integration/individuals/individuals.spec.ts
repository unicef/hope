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

Then('I should see the side panel with Population option', () => {
  cy.get('span').contains('Population', { timeout: 10000 });
});

When('I click on Population option', () => {
  cy.get('span').contains('Population').click();
});

Then('I should see Individuals and Households options', () => {
  cy.get('span').contains('Individuals', { timeout: 10000 });
  cy.get('span').contains('Households', { timeout: 10000 });
});

When('I click the Individuals option', () => {
  cy.get('span').contains('Individuals').click();
});

Then('I should see the Individuals Page', () => {
  cy.get('h6').contains('Individuals');
});

When('I click one of the table rows', () => {
  cy.get('h6').contains('Individuals');
});

// And('I click the save button', () => {
//   cy.get('[data-cy="button-save"]').click({ force: true });
//   cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
// });

// Then('I should see the Program details page', () => {
//   cy.get('h6').contains('Programme Details');
// });

// When('I click the activate button', () => {
//   cy.get('[data-cy="button-activate-program"]').click({ force: true });
// });

// Then('I should see the Activate Program Modal opened', () => {
//   cy.get('h6').contains('Activate Programme');
// });

// When('I click the activate button in the modal', () => {
//   cy.get('[data-cy="button-activate-program-modal"]').click({ force: true });
//   cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
// });

// Then('I should see the Program is active', () => {
//   cy.get('[data-cy="status-container"]').contains('ACTIVE');
// });
