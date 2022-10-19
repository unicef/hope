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

Then('I should see the side panel with Grievance option', () => {
  cy.get('span').contains('Grievance').click({ force: true });
  cy.get('span').contains('Grievance Tickets');
});

When('I click on Grievance Tickets option', () => {
  cy.get('span').contains('Grievance Tickets').click({ force: true });
});

Then('I should see the Grievance page', () => {
  cy.get('h5').contains('Grievance Tickets');
});

When('I click the New Ticket button', () => {
  cy.get('[data-cy="button-new-ticket"').click({ force: true });
});

Then('I should see the New Ticket page', () => {
  cy.get('h5').contains('New Ticket');
});

When('I fill in the form and save', () => {
  cy.get('[data-cy="select-category"]').click();
  cy.contains('Referral').click();
  cy.get('[data-cy="button-submit"]').click();
  cy.get('[data-cy="household-table-row"]').eq(0).click();
  cy.contains('LOOK UP INDIVIDUAL').click({ force: true });
  cy.get('[data-cy="individual-table-row"]').eq(0).click();
  cy.get('[data-cy="button-submit"]').click();
  cy.get('[data-cy="input-maleChildrenCount"]').click();
  cy.get('[data-cy="input-childrenDisabledCount"]').click();
  cy.get('[data-cy="input-village"]').click();
  cy.get('[data-cy="input-countryOrigin"]').click();
  cy.get('[data-cy="input-headOfHousehold"]').click();
  cy.get('[data-cy="input-consent"]').click();
  cy.get('[data-cy="button-submit"]').click();
  cy.get('[data-cy="input-description"]').click().type('description');
  cy.get('[data-cy="button-submit"]').click();
});

Then('I should see the Grievance details page', () => {
  cy.contains('Ticket ID:');
});

When('I edit the Grievance and save', () => {
  cy.get('[data-cy="button-edit"]').click({ force: true });
  cy.get('[data-cy="input-comments"]')
    .click({ force: true })
    .type('comments EDITED');
  cy.get('[data-cy="button-submit"]').click({ force: true });
});

Then('I should see the updated Grievance', () => {
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.contains('EDITED');
});
