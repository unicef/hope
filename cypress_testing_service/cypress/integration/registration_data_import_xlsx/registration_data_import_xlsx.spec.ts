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
    cy.get<{ workbook: WorkBook }>('@downloadedXlsx').should(
      ({ workbook }) => {
        expect(workbook.SheetNames).to.deep.eq([
          'Households',
          'Individuals',
          'Choices',
        ]);
      },
    );
  },
);
