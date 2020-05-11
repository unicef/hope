import { Given, When, And, Then } from 'cypress-cucumber-preprocessor/steps';
import { WorkBook } from 'xlsx';

Given('the User is viewing the Registration Data Import screen', () => {
  cy.navigateTo('/registration-data-import');

  cy.getByTestId('page-header-container').contains('registration data import', {
    matchCase: false,
  });
});

When('the User starts to import new data', () => {
  // TODO: within certain context?
  cy.getByTestId('btn-rdi-import').should('be.visible').click();
});

And('the User selects {word} as their import source', (source) => {
  cy.getByTestId('select-import-from').click();

  cy.getByTestId('select-import-from-options')
    .find('ul')
    .contains(source, { matchCase: false })
    .click();
});

And('the User downloads template', () => {
  cy.getByTestId('a-download-template').click();
});

Then('the XLSX file stored in the system is downloaded', () => {
  cy.getByTestId('a-download-template')
    .click()
    .then((anchor) => {
      const url = anchor.attr('href');

      cy.downloadXlsxData(url).parseXlsxData().as('downloadedXlsx');
    });
});

And(
  'the downloaded XLSX file has the Households, Individuals and Choices sheets',
  () => {
    cy.get<{ workbook: WorkBook }>('@downloadedXlsx').should(({ workbook }) => {
      expect(workbook.SheetNames).to.deep.eq([
        'Households',
        'Individuals',
        'Choices',
      ]);
    });
  },
);

Given(
  'the User is prompted to select a file from the Import Excel screen',
  () => {
    cy.navigateTo('/registration-data-import');

    cy.getByTestId('page-header-container').contains(
      'registration data import',
      {
        matchCase: false,
      },
    );

    // TODO: within certain context?
    cy.getByTestId('btn-rdi-import').should('be.visible').click();
  },
);

And('the User uploads file', () => {
  const fileName = 'rdi-small.xlsx';
  cy.fixture(fileName, 'base64').then((fileContent) => {
    // @ts-ignore
    cy.get('[data-cy=rdi-file-input]').upload({
      fileContent,
      fileName,
      encoding: 'base64',
      mimeType:
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
  });

  cy.getByTestId('loading-container').should('be.visible');
  cy.get('.MuiDialogContent-root').contains(fileName);
  cy.getByTestId('loading-container', { timeout: 10000 }).should(
    'not.be.visible',
  );
});

And('the file has no errors', () => {
  cy.getByTestId('errors-container').should('not.be.visible');
});

And('the User completes all required fields', () => {
  cy.get('.MuiDialogContent-root').within(() => {
    // TODO: add some hash to name
    const uploadName = 'Test RDI Import';
    cy.getByTestId('input-name').type(uploadName);
    cy.wrap(uploadName).as('uploadedXlsx');
  });
});

And('the User confirms the import', () => {
  cy.get('.MuiDialogActions-root')
    .contains('import', { matchCase: false })
    .click();
});

Then('the User is taken to the Import details screen', () => {
  cy.getByTestId('page-header-container').contains('registration data import', {
    matchCase: false,
  });

  cy.get<string>('@uploadedXlsx').then((uploadName) => {
    cy.getByTestId('page-header-container').contains(uploadName);
  });
});

And('the information from uploaded file is visible', () => {
  // TODO: clarify level of details to be tested
  cy.getByTestId('labelized-field-container-households').contains('18');
  cy.getByTestId('labelized-field-container-individuals').contains('72');
});
