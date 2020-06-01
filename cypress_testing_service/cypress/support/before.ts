before(() => {
  cy.clearLocalStorageItems();
  cy.clearCookiesWhitelist();
  cy.clearCookies();
});
