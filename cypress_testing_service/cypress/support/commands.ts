import mockAuthCookies from './mockAuthCookies.json';

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
  cy.task('AzureAdSingleSignOn', options).then(
    ({ cookies }: { cookies: Cypress.Cookie }) => {
      login(cookies);
    },
  );
});

Cypress.Commands.add('loginWithMock', () => {
  login(mockAuthCookies);
});

Cypress.Commands.add('getByTestId', (value, options) => {
  return cy.get(`[data-cy=${value}]`, options);
});

Cypress.Commands.add('getBusinessAreaSlug', () => {
  cy.location('pathname').then((pathname) => {
    const businessAreaSlug = pathname.split('/')[1];
    cy.wrap(businessAreaSlug).as('businessAreaSlug');
  });

  return cy.get('@businessAreaSlug');
});

Cypress.Commands.add('navigateTo', (newPath) => {
  return cy.getBusinessAreaSlug().then((businessAreaSlug) => {
    cy.visit('/'.concat(businessAreaSlug, newPath));
  });
});

Cypress.Commands.add('pickDayOfTheMonth', (day, inputName) => {
  cy.getByTestId(`date-input-${inputName}`).click();
  cy.get('.MuiPickersBasePicker-pickerView button')
    .contains(new RegExp(`^${day}$`, 'g'))
    .click();
});

Cypress.Commands.add(
  'parseXlsxData',
  { prevSubject: 'optional' },
  (data, nameOrIndex) => {
    return cy.task('parseXlsxData', { data, nameOrIndex });
  },
);

Cypress.Commands.add('downloadXlsxData', (url) => {
  return cy.wrap(
    new Promise((resolve) => {
      const request = new XMLHttpRequest();
      request.open('GET', url, true);
      request.responseType = 'blob';

      request.onload = () => {
        expect(request.status).eq(200, 'XLSX data download failed');

        const blob = request.response;

        const reader = new FileReader();
        reader.onload = () => {
          resolve(reader.result);
        };
        reader.readAsBinaryString(blob);
      };
      request.send();
    }),
  );
});
