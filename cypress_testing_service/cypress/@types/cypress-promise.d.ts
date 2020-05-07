declare module 'cypress-promise' {
  function promisify<T>(chain: Cypress.Chainable<T>): Promise<T>;

  export = promisify;
}
