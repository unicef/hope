before(() => {
  cy.clearLocalStorage();
  cy.clearCookiesWhitelist();
  cy.clearCookies();
});
