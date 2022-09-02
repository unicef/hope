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

When('I click the Households option', () => {
  cy.get('span').contains('Households').click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Households Page and the table', () => {
  cy.get('div').contains('Households');
  cy.get('[data-cy="table-title"]').contains('Households');
});

When('I click one of the table rows', () => {
  cy.get('[data-cy="household-table-row"]').first().click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Household details page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Household ID:');
  cy.get('h6').contains('Details');
  cy.get('h6').contains('Benefits');
  cy.get('h6').contains('Household Composition');
  cy.get('h6').contains('Individuals in Household');
  cy.get('h6').contains('Payment Records');
  cy.get('h6').contains('Vulnerabilities');
  cy.get('h6').contains('Registration Details');
  cy.get('h6').contains('Activity Log');
});
