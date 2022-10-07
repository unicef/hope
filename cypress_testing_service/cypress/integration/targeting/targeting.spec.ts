import { When, Then, Given } from 'cypress-cucumber-preprocessor/steps';
import {
  fillProgramForm,
  fillTargetingForm,
  uniqueSeed,
  getIndividualsFromRdiDetails,
} from '../../procedures/procedures';

let individualIds = [];
let programName;

Given('I am authenticated', () => {
  cy.visit('/api/unicorn/');
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});

const clearCache = () => {
  cy.get('[data-cy="menu-user-profile"]').click();
  cy.get('[data-cy="menu-item-clear-cache"]').click();
  // hack to let the page reload
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
};

Given('There are individuals and households imported', () => {
  cy.exec(`yarn run generate-xlsx-files 3 --seed ${uniqueSeed}`);
  cy.visit('/');
  clearCache();
  cy.get('span')
    .contains('Registration Data Import', { timeout: 10000 })
    .click();
  cy.get('button > span').contains('IMPORT').click({ force: true });

  cy.get('[data-cy="import-type-select"]').click();
  cy.get('[data-cy="excel-menu-item"]').click();

  cy.get('[data-cy="input-name"]').type(
    'Test import '.concat(new Date().toISOString()),
  );

  const rdiFileName = `rdi_import_3_hh_3_ind_seed_${uniqueSeed}.xlsx`;
  cy.fixture(rdiFileName, 'base64').then((fileContent) => {
    cy.get('[data-cy="file-input"]').upload({
      fileContent,
      fileName: rdiFileName,
      mimeType:
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      encoding: 'base64',
    });
  });

  cy.get('[data-cy="button-import-rdi"').click();

  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.reload();
  cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
  // it lets the browser load the status

  cy.get('div').contains('IMPORT ERROR').should('not.exist');
  cy.get('div').contains('IN REVIEW');

  cy.get('span').contains('Merge').click({ force: true }); // top of page
  cy.get('span').contains('MERGE').click({ force: true }); // inside modal

  cy.get('div').contains('MERGING');
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.reload();
  cy.get('div').contains('MERGED');
  cy.get('button > span').contains('Individuals').click({ force: true });
  getIndividualsFromRdiDetails(cy, 3, individualIds);
});

Given('I have an active program', () => {
  cy.visit('/');
  cy.get('span').contains('Programme Management').click();
  cy.get('[data-cy="button-new-program"]').click({ force: true });
  programName = fillProgramForm(cy);
  cy.get('[data-cy="button-save"]').click({ force: true });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('[data-cy="button-activate-program"]').click({ force: true });
  cy.get('[data-cy="button-activate-program-modal"]').click({ force: true });
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('[data-cy="status-container"]').contains('Active');
});

When('I visit the main dashboard', () => {
  cy.visit('/');
});

Then('I should see the side panel with Targeting option', () => {
  cy.get('span').contains('Targeting', { timeout: 10000 });
});

When('I click on Targeting option', () => {
  cy.get('span').contains('Targeting').click();
});

Then('I should see the Targeting page', () => {
  cy.get('h5').contains('Targeting');
});

When('I click the Create New button', () => {
  cy.get('[data-cy="button-target-population-create-new"]').click({
    force: true,
  });
});

Then('I should see the Create Target Population page', () => {
  cy.get('[data-cy="input-name"]')
    .first()
    .find('label')
    .contains('Enter Target Population Name');
});

When('I fill out the form fields and save', () => {
  fillTargetingForm(cy, programName, uniqueSeed);
  cy.get('[data-cy="button-target-population-add-criteria"]').eq(1).click();
});

Then('I should see the Households table', () => {
  cy.get('h6').contains('Households');
});

When('I save the Target Population', () => {
  cy.get(
    '[data-cy=button-target-population-create] > .MuiButton-label',
  ).click();
});

Then('I should see the Target Population details page and status Open', () => {
  cy.get('h6').contains('Targeting Criteria');
  cy.get('[data-cy="status-container"]').contains('Open');
});

When('I Lock Target Population', () => {
  cy.get('[data-cy="button-target-population-lock"]').click({ force: true });
  cy.get('[data-cy="button-target-population-modal-lock"]').click({
    force: true,
  });
});

Then(
  'I should see the Target Population details page and status Locked',
  () => {
    cy.get('h6').contains('Targeting Criteria');
    cy.get('[data-cy="status-container"]').contains('Locked');
  },
);

When('I Send Target Population to HOPE', () => {
  cy.get('[data-cy="button-target-population-send-to-hope"]').click({
    force: true,
  });
  cy.get('[data-cy="button-target-population-modal-send-to-hope"]').click();
});

Then('I should see the Target Population details page and status Ready', () => {
  cy.get('h6').contains('Targeting Criteria');
  cy.get('[data-cy="status-container"]').contains('Ready');
});
