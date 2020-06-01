const role = 'hqAdmin';

before(() => {
  cy.clearCookies();
  cy.clearLocalStorage();

  cy.generateUser().then((registeredUser) => {
    const { firstName, lastName, username, email, password } = registeredUser;
    cy.createUser({
      firstName,
      lastName,
      username,
      email,
      password,
      isStaff: true,
      isSuperuser: true,
      isActive: true,
    });
    cy.assignBusinessArea(username);
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
  } = Cypress.env(role);
  cy.log(`cookies, preserving once: ${JSON.stringify(cookies)}`);
  Cypress.Cookies.preserveOnce(...cookies);

  cy.log(`setting user local storage: ${JSON.stringify(userStorage)}`);
  Object.keys(userStorage).forEach((key) => {
    localStorage.setItem(key, userStorage[key]);
  });
});
