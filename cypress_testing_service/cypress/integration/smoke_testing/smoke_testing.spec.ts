import { When, Then, And } from 'cypress-cucumber-preprocessor/steps';
// import '../../support/before';

// Before(() => {
//   // workaround due to app code issue:
//   // 'Warning: Each child in a list should have a unique "key" prop.'
//   Cypress.on('uncaught:exception', () => {
//     return false;
//   });
// });

// Then('I should get redirected to login', () => {
//   cy.location('pathname').should('eq', '/login');
//   cy.get('a').contains('Sign in');
// });

// Then('I should see the Dashboard', () => {
//   cy.getByTestId('main-content').contains('Dashboard');
// });

// When('I make a request to GraphQL endpoint', () => {
//   cy.request('POST', 'api/graphql').as('graphQLRequest');
// });

// Then('I get a 200 response', () => {
//   cy.wait('@graphQLRequest').then((response) => {
//     expect(response.status).to.eq(200);
//   });
// });

When('I visit /', () => {
  cy.visit('/');
})

Then("I should see the AD login page", () => {
  cy.get('a').contains('Sign in');
})

When("I visit admin panel", () => {
  cy.visit('/api/unicorn/');
})

And("I fill in the login form", () => {
  cy.get('input[name="username"]').type('root');
  cy.get('input[name="password"]').type('root1234');
  cy.get('input').contains('Log in').click();
})

Then("I should see the admin panel contents", () => {
  cy.get('a').contains('HOPE Administration');
})