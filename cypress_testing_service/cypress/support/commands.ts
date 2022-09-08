Cypress.Commands.add("getByTestId", (testId: string) => {
  return cy.get(`[data-testid="${testId}"]`);
});

Cypress.Commands.add("getByCyId", (cyId: string) => {
  return cy.get(`[data-cy="${cyId}"]`);
});
