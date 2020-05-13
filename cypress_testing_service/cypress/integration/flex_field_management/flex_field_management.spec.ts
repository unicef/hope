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

And('error message about empty label is shown', () => {
  cy.get('.errorlist').contains('label cannot be empty');
});

And(
  'the User imports flexible attributes XLS file containing choices without name',
  () => {
    importXlsDocument('choicesNoName');
  },
);

And('error message about required name is shown', () => {
  cy.get('.errorlist').contains('name is required', { matchCase: false });
});

And(
  'the User imports a valid XLS file with default dairy_h_f attribute',
  () => {
    importXlsDocument('valid_dairy_h_f_default');
  },
);

Then('the dairy_h_f attribute has default value', () => {
  cy.get('table tbody tr').contains('dairy_h_f').click();
  cy.get('#content').contains('Change flexible attribute');
  cy.get('#content form textarea').contains('Milk and dairy products: yoghurt, cheese');
});

And(
  'the User imports a valid XLS file with modified dairy_h_f attribute',
  () => {
    importXlsDocument('valid_dairy_h_f_default_with_eggs');
  },
);

Then('the dairy_h_f attribute has modified value', () => {
  cy.get('table tbody tr').contains('dairy_h_f').click();
  cy.get('#content').contains('Change flexible attribute');
  cy.get('#content form textarea').contains('Milk and dairy products: yoghurt, cheese, eggs');
});
