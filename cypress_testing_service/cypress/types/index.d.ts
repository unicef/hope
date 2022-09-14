declare namespace Cypress {
  interface Chainable<Subject> {
    /**
     * Custom command to select DOM element by data-cy attribute.
     * @example cy.getByCyId('hero-title')
     */
    getByCyId(cyId: string): Chainable<any>
    /**
     * Custom command to select DOM element by data-testid attribute.
     * @example cy.getByTestId('hero-title')
     */
    getByTestId(testId: string): Chainable<any>
  }
}
