import {
  Given,
  When,
  And,
  Then,
  Before,
} from 'cypress-cucumber-preprocessor/steps';
import { uuid } from 'uuidv4';
import { WorkBook } from 'xlsx';
import { apiUrl, api } from '../../support/api';
import { overrideScrollingStrategy } from '../../support/utils';
import '../../support/before';

Before(() => {
  overrideScrollingStrategy();

  // workaround due to app code issue:
  // 'Warning: validateDOMNesting(...): <h6> cannot appear as a child of <h2>.'
  Cypress.on('uncaught:exception', () => {
    return false;
  });
});

Given('the User is viewing the Registration Data Import screen', () => {
  cy.navigateTo('/registration-data-import');

  cy.getByTestId('page-header-container').contains('registration data import', {
    matchCase: false,
  });
});

When('the User starts to import new data', () => {
  cy.getByTestId('page-header-container')
    .getByTestId('button-import')
    .should('be.visible')
    .click();
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
      // https://github.com/cypress-io/cypress/issues/949
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

    cy.getByTestId('page-header-container')
      .getByTestId('button-import')
      .should('be.visible')
      .click();
  },
);

And('the User uploads file', () => {
  const path = 'documents/rdi';
  cy.fixture(`${path}/meta`).then(({ valid }) => {
    const { fileName, ...otherMeta } = valid;
    cy.fixture(`${path}/${fileName}`, 'base64').then((fileContent) => {
      cy.getByTestId('rdi-file-input').upload({
        fileName,
        fileContent,
        encoding: 'base64',
        ...otherMeta,
      });
    });

    cy.getByTestId('loading-container').should('be.visible');
    cy.getByTestId('dialog-root').contains(fileName);
    cy.getByTestId('loading-container', { timeout: 10000 }).should(
      'not.be.visible',
    );
  });
});

And('the file has no errors', () => {
  cy.getByTestId('errors-container').should('not.be.visible');
  cy.getByTestId('import-available-households-counter').should('be.visible');
  cy.getByTestId('import-available-individuals-counter').should('be.visible');
});

And('the User completes all required fields', () => {
  cy.fixture('rdi').then(({ name }) => {
    const uniqueName = `${name} ${uuid()}`;
    cy.getByTestId('dialog-root').getByTestId('input-name').type(uniqueName);

    cy.wrap(uniqueName).as('uploadedXlsx');
  });
});

And('the User confirms the import', () => {
  cy.getByTestId('dialog-actions-container')
    .getByTestId('button-import')
    .click();
  cy.getByTestId('dialog-root').should('not.be.visible');
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
  cy.getByTestId('labelized-field-container-households').should('be.visible');
  cy.getByTestId('labelized-field-container-individuals').should('be.visible');
});

Given('the User has an RDI import in review', () => {
  cy.getBusinessAreaSlug().then((businessAreaSlug) => {
    const path = 'documents/rdi';
    cy.fixture(`${path}/meta`).then(({ valid }) => {
      const { fileName } = valid;
      cy.fixture(`${path}/${fileName}`, 'base64')
        .then((file) => {
          // https://github.com/abramenal/cypress-file-upload/issues/12
          return Cypress.Blob.base64StringToBlob(
            file,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          );
        })
        .as('blob');
    });

    cy.get<Blob>('@blob').then((blob) => {
      cy.gqlUploadFile(
        apiUrl,
        api.getUploadImportDataXlsxFileOperation(businessAreaSlug),
        blob,
        'valid.xlsx',
      ).as('fileUploadResponse');
    });

    cy.get<{ data: any }>('@fileUploadResponse').then((fileUploadResponse) => {
      const {
        data: {
          uploadImportDataXlsxFile: {
            importData: { id: importDataId },
          },
        },
      } = fileUploadResponse;

      const name = `Automated RDI Import ${uuid()}`;
      api
        .createRegistrationDataImport({
          name,
          businessAreaSlug,
          importDataId,
        })
        .then((response) => {
          const {
            data: {
              registrationXlsxImport: { registrationDataImport },
            },
          } = response.body;
          cy.wrap(registrationDataImport).as('registrationDataImport');
        });
    });
  });

  cy.get<{ id: string }>('@registrationDataImport').then(({ id }) => {
    cy.navigateTo(`/registration-data-import/${id}`);

    const getStatus = (status: string) => {
      cy.getByTestId('status-container').then(($status) => {
        if ($status.text().toLowerCase().includes(status)) {
          cy.wrap($status).as('status');
          return;
        }

        // eslint-disable-next-line cypress/no-unnecessary-waiting
        cy.wait(5000);
        cy.reload();
        getStatus(status);
      });
    };

    getStatus('in review');

    // NOTE:
    // Change from 'importing' to 'in review' takes a lot of time,
    // possibly there is an issue on the app side that needs to be
    // fixed, using explicit timeout combined with page refreshing
    // periodically for now.
    cy.get('@status', { timeout: 60000 });
  });
});

And('the User has reviewed all import data content', () => {
  cy.getByTestId('labelized-field-container-households').should('be.visible');
  cy.getByTestId('labelized-field-container-individuals').should('be.visible');
});

When('the User approves the RDI import', () => {
  cy.getByTestId('page-header-container')
    .getByTestId('button-approve')
    // using '{ force: true }' as a workaround due to app code issue:
    // 'Warning: validateDOMNesting(...): <h6> cannot appear as a child of <h2>.'
    .click({ force: true });

  cy.getByTestId('dialog-actions-container')
    .getByTestId('button-approve')
    .click();
});

Then('the RDI import becomes approved', () => {
  cy.getByTestId('status-container').contains('approved', { matchCase: false });
});

When('the User unapproves the RDI import', () => {
  cy.getByTestId('page-header-container')
    .getByTestId('button-unapprove')
    .click();

  cy.getByTestId('dialog-actions-container')
    .getByTestId('button-unapprove')
    .click();
});

Then('the RDI import changes status to in review', () => {
  cy.getByTestId('status-container').contains('in review', {
    matchCase: false,
  });
});
