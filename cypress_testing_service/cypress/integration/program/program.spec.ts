import { When, Then, And, Given } from 'cypress-cucumber-preprocessor/steps';
import { fillProgramForm } from '../../procedures/procedures';

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
  fillProgramForm(cy);
});

And('I click the save button', () => {
  cy.get('[data-cy="button-save"]').click({ force: true });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Program details page', () => {
  cy.get('h6').contains('Programme Details');
});

When('I click the activate button', () => {
  cy.get('[data-cy="button-activate-program"]').click({ force: true });
});

Then('I should see the Activate Program Modal opened', () => {
  cy.get('h6').contains('Activate Programme');
});

When('I click the activate button in the modal', () => {
  cy.get('[data-cy="button-activate-program-modal"]').click({ force: true });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Program is active', () => {
  cy.get('[data-cy="status-container"]').contains('ACTIVE');
});
