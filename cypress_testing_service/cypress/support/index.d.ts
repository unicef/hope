declare namespace Cypress {
  interface Chainable<Subject> {
    getByTestId<E extends Node = HTMLElement>(
      testId: string,
      options?: Partial<Loggable & Timeoutable & Withinable>,
    );
  }
}