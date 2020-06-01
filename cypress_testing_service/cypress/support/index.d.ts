declare namespace Cypress {
  interface Chainable<Subject> {
    /**
     * Generate user with fake, almost random data.
     */
    generateUser(): Chainable<any>;

    /**
     * Creates user directly through django admin.
     */
    createUser({
      firstName,
      lastName,
      username,
      email,
      password,
      isStaff,
      isSuperuser,
      isActive,
    }: {
      firstName: string;
      lastName: string;
      username: string;
      email: string;
      password: string;
      isStaff?: boolean;
      isSuperuser?: boolean;
      isActive?: boolean;
    }): Chainable<any>;

    /**
     * Assigns a business area to the user with provided email.
     */
    assignBusinessArea(email: string): Chainable<any>;

    /**
     * Allows to login using AD or authMock.
     * The 'role' is not supported currently by authMock.
     * Ref. to cypress.env.json for additional details.
     */
    login({ role }: { role: string }): Chainable<Subject>;

    /**
     * Sets cookies for specific user role defined in cypress.env.json.
     */
    setUserCookies({ role }: { role: string }): Chainable<Subject>;

    loginToAD(
      username: string,
      password: string,
      url: string,
    ): Chainable<Subject>;

    /**
     * Sets cookies whitelist for specific user role defined in cypress.env.json.
     * Whitelisted cookies are preserved across tests. To remove persisted cookies,
     * use clearCookiesWhitelist.
     */
    setCookiesWhitelist({ role }: ({ role: string })): Chainable<null>;
    clearCookiesWhitelist(): Chainable<null>;

    /**
     * Sets local storage items for specific user role defined in cypress.env.json.
     * Items set with setLocalStorageItems won't be cleared until clearLocalStorageItems
     * is used. Ref. to localStorage.ts for more details.
     */
    setLocalStorageItems({ role }: ({ role: string })): Chainable<null>;
    clearLocalStorageItems(): Chainable<null>;

    logout(): Chainable<Subject>;

    getByTestId<E extends Node = HTMLElement>(
      testId: string,
      options?: Partial<Loggable & Timeoutable & Withinable>,
    ): Chainable<JQuery<E>>;

    getBusinessAreaSlug(): Chainable<string>;

    navigateTo(newPath: string): Chainable<Subject>;

    pickDayOfTheMonth(day: number, fieldName: string): Chainable<Subject>;

    downloadXlsxData(url: string): Chainable<any>;

    parseXlsxData(nameOrIndex?: string | number): Chainable<any>;

    gqlUploadFile(
      url: string,
      operations: object,
      blob: Blob,
      fileName: string,
    ): Chainable<object>;
  }
}
