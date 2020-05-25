before(() => {
  cy.clearLocalStorage();
  cy.clearCookies();

  cy.logout();
  cy.visit('/');
  cy.get('a').contains('Sign in');
});
