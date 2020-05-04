// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

// This is an example of how you might use the plugin in your tests
// https://gist.github.com/csuzw/845b589549b61d3a5fe18e49592e166f

const login = (cookies) => {
  cy.clearCookies();

  cookies.forEach((cookie) => {
    cy.setCookie(cookie.name, cookie.value, {
      domain: cookie.domain,
      expiry: cookie.expires,
      httpOnly: cookie.httpOnly,
      path: cookie.path,
      secure: cookie.secure,
      sameSite: cookie.sameSite,
    });
    Cypress.Cookies.preserveOnce(cookie.name);
  });
};

Cypress.Commands.add('loginToAD', (username, password, loginUrl) => {
  const options = {
    username,
    password,
    loginUrl,
    postLoginSelector: '[data-cy=side-nav]',
    headless: true,
    logs: false,
    getAllBrowserCookies: true,
  };

  // see why we need this task
  // https://github.com/cypress-io/cypress/issues/1342
  // https://github.com/cypress-io/cypress/issues/944
  cy.task('AzureAdSingleSignOn', options).then((result) => {
    login(result.cookies);
  });
});

Cypress.Commands.add('loginWithMock', () => {
  // eslint-disable-next-line global-require
  const mockAuthCookies = []; // require('./mockAuthCookies.json');
  login(mockAuthCookies);
});

Cypress.Commands.add('getByTestId', (value) => {
  return cy.get(`[data-cy=${value}]`);
});

Cypress.Commands.add('navigateTo', (newPath) => {
  return cy.location('pathname').then((pathname) => {
    const businessAreaSlug = pathname.split('/')[1];
    cy.visit('/'.concat(businessAreaSlug, newPath));
  });
});

Cypress.Commands.add('pickDayOfTheMonth', (day, inputName) => {
  cy.getByTestId(`date-input-${inputName}`).click();
  cy.get('.MuiPickersBasePicker-pickerView button')
    .contains(new RegExp(`^${day}$`, 'g'))
    .click();
});
