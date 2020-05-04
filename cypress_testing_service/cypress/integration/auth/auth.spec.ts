import { When, Then } from 'cypress-cucumber-preprocessor/steps';

When('I visit {word}', (path) => {
  cy.visit(path);
});

When('I click Logout', () => {
  cy.getByTestId('menu-btn-user-profile').click();
  cy.getByTestId('menu-item-logout').click();
});

Then('I should get redirected to login', () => {
  cy.location('pathname').should('eq', '/login');
  cy.get('a').contains('Sign in');
});

Then('I should see the Dashboard', () => {
  cy.getByTestId('main-content').contains('Dashboard');
});

Then('I see my email address in the header', () => {
  cy.get('header').contains(Cypress.env('logged_in_user_username'));
});
