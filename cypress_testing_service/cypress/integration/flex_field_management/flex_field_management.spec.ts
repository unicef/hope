import { When, Then, And } from 'cypress-cucumber-preprocessor/steps';

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

When('the User navigates to Flexible Attributes section', () => {
  cy.visit('/api/admin/core/flexibleattribute/');
});

And('the User imports a valid XLS file with flexible attributes', () => {
  cy.visit('/api/admin/core/flexibleattribute/import-xls/');

  const fileName = 'flexibleAttributesValid.xls';
  cy.fixture(fileName, 'base64').then((fileContent) => {
    // @ts-ignore
    cy.get('input[type=file]').upload(
      {
        fileContent,
        fileName,
        encoding: 'base64',
        mimeType: 'application/vnd.ms-excel',
      },
      { subjectType: 'input', force: true },
    );

    cy.get('button[type=submit]').click();

    cy.get('.messagelist').contains('Your xls file has been imported', {
      timeout: 10000,
    });
  });
});

And('the XLS file is uploaded without errors', () => {
  cy.get('.errorlist').should('be.not.be.visible');
});

Then('the list of imported flexible attributes is shown', () => {
  cy.get('table tbody tr').should('have.length.gt', 0);
});
