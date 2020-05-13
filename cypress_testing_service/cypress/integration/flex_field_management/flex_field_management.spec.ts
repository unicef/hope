import { When, Then, And } from 'cypress-cucumber-preprocessor/steps';

const importXlsDocument = (type) => {
  const path = 'documents/flexibleAttributes';
  cy.fixture(`${path}/meta`).then((meta) => {
    const { fileName, ...otherMeta } = meta[type];
    cy.fixture(`${path}/${fileName}`, 'base64').then((fileContent) => {
      // @ts-ignore
      cy.get('input[type=file]').upload(
        {
          fileName,
          fileContent,
          encoding: 'base64',
          ...otherMeta,
        },
        { subjectType: 'input', force: true },
      );

      cy.get('button[type=submit]').click();
    });
  });
};

When('the User navigates to Django Administration page', () => {
  cy.visit('/api/admin');
});

Then('the Site Administration page is shown', () => {
  cy.get('#user-tools').should(($userTools) => {
    const text = $userTools.text();
    expect(text).to.containIgnoreCase('welcome');
    expect(text).to.containIgnoreCase('log out');
  });

  cy.get('#content').contains('site administration', { matchCase: false });
});

When('the User navigates to Flexible Attributes import section', () => {
  cy.visit('/api/admin/core/flexibleattribute/import-xls/');
});

And('the User imports a valid XLS file with flexible attributes', () => {
  importXlsDocument('valid');
});

And('the XLS file is uploaded without errors', () => {
  cy.get('.messagelist').contains('Your xls file has been imported', {
    timeout: 10000,
  });

  cy.get('.errorlist').should('be.not.be.visible');
});

Then('the list of imported flexible attributes is shown', () => {
  cy.get('table tbody tr').should('have.length.gt', 0);
});

And('the User imports flexible attributes XLS file with empty label', () => {
  importXlsDocument('emptyLabel');
});

Then('the XLS file is not uploaded', () => {
  cy.get('.messagelist').should('be.not.be.visible');
});

And('error messages about empty label is shown', () => {
  cy.get('.errorlist').contains('label cannot be empty');
});
