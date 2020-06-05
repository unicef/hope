before(() => {
  cy.clearCookies();
  cy.clearLocalStorage();

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
      permissions: ['is_active', 'is_staff','is_superuser'],
    });

    cy.wrap(registeredUser).as('registeredUser');
  });

  cy.get<{ username: string; password: string }>('@registeredUser').then(
    ({ username, password }) => {
      cy.visit('/api/admin');
      cy.get('input[name=username]').type(username);
      cy.get('input[name=password]').type(password);
      cy.get('input[type=submit]').click();
    },
  );
});

beforeEach(() => {
  const {
    whitelist: { cookies },
    localStorage: userStorage,
  } = Cypress.env('hqAdmin');

  cy.log(`cookies, preserving once: ${JSON.stringify(cookies)}`);
  Cypress.Cookies.preserveOnce(...cookies);

  cy.log(`setting user local storage: ${JSON.stringify(userStorage)}`);
  Object.keys(userStorage).forEach((key) => {
    localStorage.setItem(key, userStorage[key]);
  });
});
