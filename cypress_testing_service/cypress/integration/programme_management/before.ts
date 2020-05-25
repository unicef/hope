before(() => {
  cy.login();
  cy.get<{ username: string }>('@loggedUser').then(({ username }) => {
    cy.get('header').should('be.visible').contains(username);
  });
});
