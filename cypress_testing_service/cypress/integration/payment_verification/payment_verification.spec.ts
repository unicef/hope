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

Then('I should see the side panel with Payment Verification option', () => {
  cy.get('span').contains('Payment Verification');
});

When('I click on Payment Verification option', () => {
  cy.get('span').contains('Payment Verification').click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the List of Cash Plans', () => {
  cy.get('h6').contains('List of Cash Plans');
});

When('I click one of the table rows', () => {
  cy.get('[data-cy="cash-plan-table-row"]').first().click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Cash Plan Details Page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Cash Plan');
  cy.get('h6').contains('Cash Plan Details');
  cy.get('h6').contains('Verification Plans Summary');
});
