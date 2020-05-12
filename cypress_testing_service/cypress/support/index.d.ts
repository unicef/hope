declare namespace Cypress {
  interface Chainable<Subject> {
    loginToAD(
      username: string,
      password: string,
      url: string,
    ): Chainable<Subject>;

    loginWithMock(): Chainable<Subject>;

    getByTestId<E extends Node = HTMLElement>(
      testId: string,
      options?: Partial<Loggable & Timeoutable & Withinable>,
    ): Chainable<JQuery<E>>;

    getBusinessAreaSlug(): Chainable<string>;

    navigateTo(newPath: string): Chainable<Subject>;

    pickDayOfTheMonth(day: number, fieldName: string): Chainable<Subject>;

    downloadXlsxData(url: string): Chainable<any>;

    parseXlsxData(nameOrIndex?: string | number): Chainable<any>;
  }
}
