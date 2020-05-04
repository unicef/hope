declare namespace Cypress {
  interface Chainable {
    loginToAD(
      username: string,
      password: string,
      url: string,
    ): Chainable<Element>;

    loginWithMock(): Chainable<Element>;

    getByTestId(value: string): Chainable<Element>;

    navigateTo(newPath: string): Chainable<Element>;

    pickDayOfTheMonth(day: number, fieldName: string): Chainable<Element>;
  }
}
