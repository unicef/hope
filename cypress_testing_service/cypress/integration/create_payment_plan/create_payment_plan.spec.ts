import { When, Then, Given } from 'cypress-cucumber-preprocessor/steps';
import {
  fillProgramForm,
  fillTargetingForm,
} from '../../procedures/procedures';

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

Given('I have target population in ready status', () => {
  cy.visit('/');
  cy.get('span').contains('Targeting').click();
  cy.get('[data-cy="button-target-population-create-new"]').click({
    force: true,
  });
  fillTargetingForm(cy);
  cy.get('[data-cy="button-target-population-add-criteria"]').eq(1).click();
  cy.get(
    '[data-cy=button-target-population-create] > .MuiButton-label',
  ).click();
  cy.get('[data-cy="button-target-population-lock"]').click({ force: true });
  cy.get('[data-cy="button-target-population-modal-lock"]').click({
    force: true,
  });
  cy.get('[data-cy="button-target-population-send-to-hope"]').click({
    force: true,
  });
  cy.get('[data-cy="button-target-population-modal-send-to-hope"]').click({
    force: true,
  });
  cy.get('[data-cy="status-container"]').contains('Ready');
});

When('I visit the main dashboard', () => {
  cy.visit('/');
});

Then('I should see the side panel with Payment Module option', () => {
  cy.get('span').contains('Payment Module', { timeout: 10000 });
});

When('I click on Payment Module option', () => {
  cy.get('span').contains('Payment Module').click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Payment Module page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Payment Module');
});

When('I click the New Payment Plan button', () => {
  cy.get('[data-cy="button-new-payment-plan"]').click({
    force: true,
  });
});

Then('I should see the New Payment Plan page', () => {
  cy.get('[data-cy="page-header-container"]').contains('New Payment Plan');
});

When('I fill out the form fields and save', () => {
  cy.get('[data-cy="input-target-population"]').first().click();
  cy.wait(200); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('[data-cy="select-option-1"]').click();
  cy.get('[data-cy="input-start-date"]').click().type('2022-12-12');
  cy.get('[data-cy="input-end-date"]').click().type('2022-12-23');
  cy.get('[data-cy="input-currency"]').first().click();
  cy.get('[data-cy="select-option-1"]').click();
  cy.get('[data-cy="input-dispersion-start-date"]').click().type('2023-12-12');
  cy.get('[data-cy="input-dispersion-end-date"]').click().type('2023-12-23');
  cy.get('[data-cy="button-save-payment-plan"]').click({
    force: true,
  });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Payment Plan details page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Payment Plan ID');
  cy.get('h6').contains('Details');
  cy.get('h6').contains('Results');
  cy.get('h6').contains('Payments List');
  cy.get('h6').contains('Activity Log');
});
