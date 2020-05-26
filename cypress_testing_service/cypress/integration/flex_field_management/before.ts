before(() => {
  cy.clearLocalStorage();
  cy.clearCookies();

  cy.login({ role: 'hqAdmin' });

  cy.get<{ username: string }>('@loggedUser').then(({ username }) => {
    cy.get('header').should('be.visible').contains(username);
  });
});
