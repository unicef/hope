before(() => {
  cy.clearCookies();
  cy.clearLocalStorage();

  if (!Cypress.env('useFixedCookies')) {
    cy.visitDjangoAdmin();
    cy.generateUser().then((registeredUser) => {
      const {
        username,
        password,
        name,
        email,
        firstName,
        lastName,
      } = registeredUser;
      cy.addUser({
        username,
        password,
        name,
        email,
        firstName,
        lastName,
        permissions: ['is_active', 'is_staff', 'is_superuser'],
      });

      cy.visit('/api/admin');
      cy.get('input[name=username]').type(username);
      cy.get('input[name=password]').type(password);
      cy.get('input[type=submit]').click();
    });
  }
});

beforeEach(() => {
  const { cookies } = Cypress.env('whitelist');
  cy.log(`cookies, preserving once: ${JSON.stringify(cookies || [])}`);
  Cypress.Cookies.preserveOnce(...(cookies || []));

  const testLocalStorage = Cypress.env('localStorage');
  cy.log(`setting user local storage: ${JSON.stringify(testLocalStorage || {})}`);
  Object.keys(testLocalStorage || {}).forEach((key) => {
    localStorage.setItem(key, testLocalStorage[key]);
  });
});
