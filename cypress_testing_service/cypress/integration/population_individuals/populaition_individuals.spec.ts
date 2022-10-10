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
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Individuals Page and the table', () => {
  cy.get('div').contains('Individuals');
  cy.get('[data-cy="table-title"]').contains('Individuals');
});

When('I click one of the table rows', () => {
  cy.get('[data-cy="individual-table-row"]').first().click({ force: true });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Individual details page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Individual ID:');
  cy.get('h6').contains('Bio Data');
  cy.get('h6').contains('Vulnerabilities');
  cy.get('h6').contains('Activity Log');
});
