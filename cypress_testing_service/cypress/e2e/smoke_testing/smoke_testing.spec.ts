import { When, Then, And, Given } from "@badeball/cypress-cucumber-preprocessor";

When('I visit the main dashboard', () => {
  cy.visit('/');
});

Then('I should see the AD login page', () => {
  cy.get('a').contains('Sign in');
});

When('I visit admin panel', () => {
  cy.visit('/api/unicorn/');
});

And('I fill in the login form', () => {
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});

Then('I should see the admin panel contents', () => {
  cy.get('a').contains('HOPE Administration');
  cy.get('p').contains('Please enter the correct username').should('not.exist');
});
