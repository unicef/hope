import { When, Then, Given } from 'cypress-cucumber-preprocessor/steps';
import { fillProgramForm, uniqueSeed } from '../../procedures/procedures';

Given('I am authenticated', () => {
  cy.visit('/api/unicorn/');
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});

Given('I have an active program', () => {
  cy.visit('/');
  cy.get('span').contains('Programme Management').click();
  cy.get('[data-cy="button-new-program"]').click({ force: true });
  fillProgramForm(cy);
  cy.get('[data-cy="button-save"]').click({ force: true });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('[data-cy="button-activate-program"]').click({ force: true });
  cy.get('[data-cy="button-activate-program-modal"]').click({ force: true });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('[data-cy="status-container"]').contains('ACTIVE');
});

When('I visit the main dashboard', () => {
  cy.visit('/');
});

Then('I should see the side panel with Targeting option', () => {
  cy.get('span').contains('Targeting', { timeout: 10000 });
});

When('I click on Targeting option', () => {
  cy.get('span').contains('Targeting').click();
});

Then('I should see the Targeting page', () => {
  cy.get('h5').contains('Targeting');
});

When('I click the Create New button', () => {
  cy.get('[data-cy="button-target-population-create-new"]').click({
    force: true,
  });
});

Then('I should see the Create Target Population page', () => {
  cy.get('[data-cy="input-name"]')
    .first()
    .find('label')
    .contains('Enter Target Population Name');
});

When('I fill out the form fields and save', () => {
  cy.get('[data-cy="input-name"]').first().type(`test TP ${uniqueSeed}`);
  cy.get('[data-cy="input-program"]').first().click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('[data-cy="select-option-1"]').click();
  cy.get('[data-cy="button-target-population-add-criteria"]').click();
  cy.get('[data-cy="button-household-rule"]').click();
  cy.get('[data-cy="autocomplete-target-criteria"]')
    .click()
    .type('residence status');
  cy.contains('Residence status').click();
  cy.get('[data-cy="select-filters[0].value"]').click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('li').eq(3).click();
  cy.get('[data-cy="button-target-population-add-criteria"]').eq(1).click();
});

Then('I should see the Households table', () => {
  cy.get('h6').contains('Households');
});

When('I save the Target Population', () => {
  cy.get(
    '[data-cy=button-target-population-create] > .MuiButton-label',
  ).click();
});

Then('I should see the Target Population details page and status Open', () => {
  cy.get('h6').contains('Targeting Criteria');
  cy.get('[data-cy="status-container"]').contains('Open');
});

When('I Lock Target Population', () => {
  cy.get('[data-cy="button-target-population-lock"]').click();
  cy.get('[data-cy="button-target-population-modal-lock"]').click();
});

Then(
  'I should see the Target Population details page and status Locked',
  () => {
    cy.get('h6').contains('Targeting Criteria');
    cy.get('[data-cy="status-container"]').contains('Locked');
  },
);

When('I Send Target Population to HOPE', () => {
  cy.get('[data-cy="button-target-population-send-to-hope"]').click({
    force: true,
  });
  cy.get('[data-cy="button-target-population-modal-send-to-hope"]').click();
});

Then('I should see the Target Population details page and status Ready', () => {
  cy.get('h6').contains('Targeting Criteria');
  cy.get('[data-cy="status-container"]').contains('Ready');
});
