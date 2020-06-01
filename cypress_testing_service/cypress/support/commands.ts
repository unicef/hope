import faker from 'faker';

const toBooleanField = (value: boolean) => (value ? 'True' : 'False');

Cypress.Commands.add('generateUser', () => {
  const firstName = faker.name.firstName();
  const lastName = faker.name.lastName();
  const email = faker.internet.email();
  return {
    firstName,
    lastName,
    name: `${firstName} ${lastName}`,
    username: email,
    email,
    password: faker.internet.password(),
  };
});

Cypress.Commands.add(
  'createUser',
  ({
    firstName,
    lastName,
    username,
    email,
    password,
    isStaff,
    isSuperuser,
    isActive,
  }) => {
    return cy.task('executeShellPlus', [
      `u = User(
        username='${username}',
        first_name='${firstName}',
        last_name='${lastName}',
        email='${email}',
        is_staff='${toBooleanField(isStaff)}',
        is_superuser='${toBooleanField(isSuperuser)}',
        is_active='${toBooleanField(isActive)}'
      )`,
      `u.set_password('${password}')`,
      `u.save()`,
    ]);
  },
);

Cypress.Commands.add('assignBusinessArea', (email) => {
  return cy.task('executeShellPlus', [
    `u = User.objects.get(email='${email}')`,
    `u.business_areas.set([BusinessArea.objects.first().id])`,
    `u.save()`,
  ]);
});

Cypress.Commands.add('login', ({ role }) => {
  const { username, password } = Cypress.env(role);
  const loginUrl = Cypress.env('loginUrl');

  if (!Cypress.env('useAuthMock')) {
    cy.log(`Signing in user to AD as ${role}`);
    cy.loginToAD(username, password, loginUrl);
    cy.visit(loginUrl);
  } else {
    cy.log('Signing in user with mock');
    cy.loginWithMock();
    cy.visit('/');
  }

  cy.wrap({ username }).as('loggedUser');
});

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
    ({ cookies }: { cookies: any }) => {
      cy.clearCookies();

      const whitelist: string[] = [];
      cookies.forEach((cookie) => {
        cy.setCookie(cookie.name, cookie.value, {
          domain: cookie.domain,
          expiry: cookie.expires,
          httpOnly: cookie.httpOnly,
          path: cookie.path,
          secure: cookie.secure,
          sameSite: cookie.sameSite,
        });

        whitelist.push(cookie.name);
      });

      Cypress.Cookies.defaults({ whitelist });
    },
  );
});

Cypress.Commands.add('loginWithMock', () => {
  const { cookies: mockCookies, localStorage: mockStorage } = Cypress.env(
    'authMock',
  );

  mockCookies.forEach((cookie) => {
    cy.setCookie(cookie.name, cookie.value, {
      domain: cookie.domain,
      expiry: cookie.expires,
      httpOnly: cookie.httpOnly,
      path: cookie.path,
      secure: cookie.secure,
      sameSite: cookie.sameSite.toLowerCase() as Cypress.SameSiteStatus,
    });
  });

  Cypress.Cookies.defaults({
    whitelist: Cypress.env('whitelist').cookies,
  });

  Object.keys(mockStorage).forEach((key) =>
    localStorage.setItem(key, mockStorage[key]),
  );
});

Cypress.Commands.add('setDefaultCookies', () => {
  Cypress.Cookies.defaults({
    whitelist: Cypress.env('whitelist').cookies,
  });
});

Cypress.Commands.add('clearDefaultCookies', () => {
  Cypress.Cookies.defaults({
    whitelist: [],
  });
});

Cypress.Commands.add('setDefaultStorage', () => {
  const { localStorage: mockStorage } = Cypress.env(
    'authMock',
  );

  Object.keys(mockStorage).forEach((key) =>
    localStorage.setItem(key, mockStorage[key]),
  );
});

Cypress.Commands.add('clearDefaultStorage', () => {
  const { localStorage: mockStorage } = Cypress.env(
    'authMock',
  );

  Object.keys(mockStorage).forEach((key) =>
    localStorage.removeItem(key),
  );
});

Cypress.Commands.add('logout', () => {
  localStorage.removeItem('AUTHENTICATED');
  cy.clearCookies();
  cy.request('/api/logout');
});

Cypress.Commands.add(
  'getByTestId',
  {
    prevSubject: ['optional', 'window', 'document', 'element'],
  },
  (subject, testId, options) => {
    const selector = `[data-cy=${testId}]`;

    if (subject) {
      cy.wrap(subject).find(selector, options);
    } else {
      cy.get(selector, options);
    }
  },
);

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
  cy.getByTestId('date-picker-container')
    .find('button p')
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

Cypress.Commands.add(
  'gqlUploadFile',
  (url: string, operations: object, blob: Blob, fileName: string) => {
    return cy.wrap(
      new Cypress.Promise((resolve) => {
        const formData = new FormData();
        formData.append('operations', JSON.stringify(operations));
        formData.append('map', JSON.stringify({ '0': ['variables.file'] }));
        formData.append('0', blob, fileName);

        const request = new XMLHttpRequest();
        request.open('POST', url, true);
        request.responseType = 'json';
        request.onload = () => {
          expect(request.status).eq(200, 'XLSX data download failed');
          resolve(request.response);
        };

        request.send(formData);
      }),
    );
  },
);
