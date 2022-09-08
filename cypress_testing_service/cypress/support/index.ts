// ***********************************************************
// This support/index.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
// ***********************************************************

import './commands';
import './chai';
import 'cypress-file-upload';

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to select DOM element by data-cy attribute.
       * @example cy.getByCyId('hero-title')
       */
      getByCyId(cyId: string): Chainable<Element>
      /**
       * Custom command to select DOM element by data-testid attribute.
       * @example cy.getByTestId('hero-title')
       */
      getByTestId(testId: string): Chainable<Element>
    }
  }
}
