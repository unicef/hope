before(() => {
  cy.logout();
  cy.visit('/');
  cy.get('a').contains('Sign in');
});
