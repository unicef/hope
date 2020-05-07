declare namespace Cypress {
  interface Chainable<Subject> {
    loginToAD(
      username: string,
      password: string,
      url: string,
    ): Chainable<Subject>;

    loginWithMock(): Chainable<Subject>;

    getByTestId(value: string): Chainable<Subject>;

    getBusinessAreaSlug(): Chainable<Subject>;

    navigateTo(newPath: string): Chainable<Subject>;

    pickDayOfTheMonth(day: number, fieldName: string): Chainable<Subject>;
  }
}
