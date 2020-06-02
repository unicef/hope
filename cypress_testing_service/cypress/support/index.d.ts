declare namespace Cypress {
  type Permission = 'is_active' | 'is_staff' | 'is_superuser';
  interface User {
    username: string;
    password: string;
    name: string;
    email: string;
    firstName: string;
    lastName: string;
    permissions: Permission[];
  }

  interface Chainable<Subject> {
    /**
     * Generate user with fake, random -like data.
     */
    generateUser(): Chainable<User>;

    /**
     * Visits django admin UI.
     * NOTE:
     * - 'daUsername' and daPassword env variables need to be set first
     */
    visitDjangoAdmin(): Chainable<null>;

    /**
     * Adds a user account through django admin UI.
     */
    addUser(user: User): Chainable<null>;

    /**
     * Creates a user through django admin shell.
     * NOTE:
     * - requires access to django admin shell
     * - recommended to be used only in local environment setup
     */
    createUser(user: User): Chainable<null>;

    /**
     * Assigns a business area to the user with provided email.
     * NOTE:
     * - requires access to django admin shell
     * - recommended to be used only in local environment setup
     */
    assignBusinessArea(email: string): Chainable<null>;

    /**
     * Loads cookies for specific user role defined in cypress.env.json.
     */
    loadUserCookies({ role }: { role: string }): Chainable<null>;

    /**
     * Loads to Active Directory using pupeteer.
     */
    loginToAD(
      username: string,
      password: string,
      url: string,
    ): Chainable<null>;

    /**
     * Loads local storage items for specific user role defined in cypress.env.json.
     */
    loadUserLocalStorage({ role }: { role: string }): Chainable<null>;

    /**
     * Logs out the current user.
     */
    logout(): Chainable<null>;

    /**
     * Gets an element using data-cy attribute.
     */
    getByTestId<E extends Node = HTMLElement>(
      testId: string,
      options?: Partial<Loggable & Timeoutable & Withinable>,
    ): Chainable<JQuery<E>>;

    /**
     * Reads business area slug from the url.
     * NOTE:
     * - assumes url has the format /{businessAreaSlug}/foo/bar
     */
    getBusinessAreaSlug(): Chainable<string>;

    /**
     * Navigates to 'newPath' within current business area.
     */
    navigateTo(newPath: string): Chainable<null>;

    /**
     * Picks day of the month from the UI picker.
     */
    pickDayOfTheMonth(day: number, fieldName: string): Chainable<null>;

    /**
     * Downloads xlsx file data.
     */
    downloadXlsxData(url: string): Chainable<any>;

    /**
     * Parses the xlsx file data.
     */
    parseXlsxData(nameOrIndex?: string | number): Chainable<any>;

    /**
     * Uploads file using gql api.
     */
    gqlUploadFile(
      url: string,
      operations: object,
      blob: Blob,
      fileName: string,
    ): Chainable<object>;
  }
}
