/**
 * This is copied from `@types/chai-subset`. The types package imports
 * `@types/chai` which conflicts with Cypress' definitions for chai which is why
 * this code is copied instead of installing that package.
 * /// <reference path="https://github.com/cypress-io/cypress/issues/7435" />
 */

declare module "chai-subset" {
  global {
    namespace Chai {
      interface Assertion {
        containSubset(expected: any): Assertion
      }
      interface Assert {
        containSubset(val: any, exp: any, msg?: string): void
      }
    }
  }

  const chaiSubset: Chai.ChaiPlugin;
  export = chaiSubset
}
