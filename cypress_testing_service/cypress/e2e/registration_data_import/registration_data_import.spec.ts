import { When, Then, Given } from "@badeball/cypress-cucumber-preprocessor";
import { getIndividualsFromRdiDetails } from '../../procedures/procedures';

let householdId;
let individualId;
let individualIds = [];

Given('I am authenticated', () => {
  cy.visit('/api/unicorn/');
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});

Given('There are no RDI imports', () => {
  cy.exec('yarn run generate-xlsx-files');
});

const clearCache = () => {
  cy.get('[data-cy="menu-user-profile"]').click();
  cy.get('[data-cy="menu-item-clear-cache"]').click();
  // hack to let the page reload
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
};

When('I visit the main dashboard', () => {
  cy.visit('/');
  clearCache();
});

Then('I should see the side panel with RDI option', () => {
  cy.get('span').contains('Registration Data Import', { timeout: 10000 });
});

When('I click on RDI option', () => {
  cy.get('span').contains('Registration Data Import').click();
});

Then('I should see the RDI page', () => {
  cy.get('h5').contains('Registration Data Import');
});

When('I click the import button', () => {
  cy.get('button > span').contains('IMPORT').click({ force: true });
});

Then('I should see the file import modal', () => {
  cy.get('h2').contains('Select File to Import').click();
});

When('I select the xlsx file', () => {
  cy.get('[data-cy="import-type-select"]').click();
  cy.get('[data-cy="excel-menu-item"]').click();

  cy.get('[data-cy="input-name"]').type(
    'Test import '.concat(new Date().toISOString()),
  );

  cy.fixture('rdi_import_1_hh_1_ind.xlsx', 'base64').as('rdi_import_1_hh_1_ind');
  cy.get('[data-cy="file-input"]').selectFile('@rdi_import_1_hh_1_ind', { action: 'select', force: true });
});

Then('I see it was chosen', () => {
  cy.get('[data-cy="number-of-households"]').contains(
    '1 Household available to Import',
    {
      timeout: 10000,
    },
  );
  cy.get('[data-cy="number-of-individuals"]').contains(
    '1 Individual available to Import',
  );
  cy.get('div').contains('Errors').should('not.exist');
});

When('I press import', () => {
  cy.get('[data-cy="button-import-rdi"').click();
});

Then('I should see a new import with status in review', () => {
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.reload();
  cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
  // it lets the browser load the status

  cy.get('div').contains('IMPORT ERROR').should('not.exist');
  cy.get('div').contains('IN REVIEW');
});

When('I merge the import', () => {
  cy.get('span').contains('Merge').click({ force: true }); // top of page
  cy.get('span').contains('MERGE').click({ force: true }); // inside modal
});

Then('I see that the status is merging', () => {
  cy.get('div').contains('MERGING');
});

When('I refresh the page', () => {
  cy.reload();
});

Then('I see that the status is merged', () => {
  cy.get('div').contains('MERGED');
  cy.get('tbody > tr > td:nth-child(2)').then(($td) => {
    householdId = $td.text().split(' (')?.[0];
  });
  cy.get('button > span').contains('Individuals').click({ force: true });
  individualId = getIndividualsFromRdiDetails(cy, 1)[0];
});

When('I visit the Households dashboard', () => {
  cy.get('span').contains('Population').click();
  cy.get('span').contains('Households').click();
});

Then('I see a newly imported household', () => {
  // after 10+ runs, it may fail, because there are 10 rows in this table by default
  cy.get('td').should('contain', householdId);
});

When('I visit the Individuals dashboard', () => {
  cy.get('span').contains('Individuals').click();
});

Then('I see the newly imported individuals', () => {
  // after 10+ runs, it may fail, because there are 10 rows in this table by default
  cy.get('td').should('contain', individualId);
  cy.get('tbody > tr > td:nth-child(2)').then(($td) => {
    individualId = $td.text();
    console.log('individualId');
    individualIds.push(individualId);
  });
});
