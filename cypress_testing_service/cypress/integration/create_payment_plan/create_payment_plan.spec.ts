import { When, Then, Given, And } from 'cypress-cucumber-preprocessor/steps';
import {
  fillProgramForm,
  fillTargetingForm,
  uniqueSeed,
} from '../../procedures/procedures';

let programName;
let targetPopulationName;

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

  const fileName = 'rdi_import_3_hh_3_ind.xlsx';
  cy.fixture(fileName, 'base64').then((fileContent) => {
    cy.get('[data-cy="rdi-file-input"]').upload({
      fileContent,
      fileName,
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
  cy.get('[data-cy="status-container"]').contains('ACTIVE');
});

Given('I have target population in ready status', () => {
  cy.visit('/');
  cy.get('span').contains('Targeting').click();
  cy.get('[data-cy="button-target-population-create-new"]').click({
    force: true,
  });
  targetPopulationName = fillTargetingForm(cy, programName, uniqueSeed);
  cy.get('[data-cy="button-target-population-add-criteria"]').eq(1).click();
  cy.get(
    '[data-cy=button-target-population-create] > .MuiButton-label',
  ).click();
  cy.get('[data-cy="button-target-population-lock"]').click({ force: true });
  cy.get('[data-cy="button-target-population-modal-lock"]').click({
    force: true,
  });
  cy.get('[data-cy="button-target-population-send-to-hope"]').click({
    force: true,
  });
  cy.get('[data-cy="button-target-population-modal-send-to-hope"]').click({
    force: true,
  });
  cy.get('[data-cy="status-container"]').contains('Ready');
});

When('I visit the main dashboard', () => {
  cy.visit('/');
});

Then('I should see the side panel with Payment Module option', () => {
  cy.get('span').contains('Payment Module', { timeout: 10000 });
});

When('I click on Payment Module option', () => {
  cy.get('span').contains('Payment Module').click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Payment Module page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Payment Module');
});

When('I click the New Payment Plan button', () => {
  cy.get('[data-cy="button-new-payment-plan"]').click({
    force: true,
  });
});

Then('I should see the New Payment Plan page', () => {
  cy.get('[data-cy="page-header-container"]').contains('New Payment Plan');
});

When('I fill out the form fields and save', () => {
  cy.get('[data-cy="input-target-population"]').first().click();
  cy.wait(200); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get(`[data-cy="select-option-${targetPopulationName}"]`).click();

  cy.get('[data-cy="input-start-date"]').click().type('2022-12-12');
  cy.get('[data-cy="input-end-date"]').click().type('2022-12-23');
  cy.get('[data-cy="input-currency"]').first().click();
  cy.get('[data-cy="select-option-Afghan afghani"]').click();
  cy.get('[data-cy="input-dispersion-start-date"]').click().type('2023-12-12');
  cy.get('[data-cy="input-dispersion-end-date"]').click().type('2023-12-23');
  cy.get('[data-cy="button-save-payment-plan"]').click({
    force: true,
  });
});

Then('I should see the Payment Plan details page', () => {
  // TODO: this wait is needed for some reason
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  // cy.get('[data-cy="page-header-container"]').contains('Payment Plan ID'); // TODO
  cy.get('h6').contains('Details');
  cy.get('h6').contains('Results');
  cy.get('h6').contains('Payments List');
  cy.get('h6').contains('Activity Log');
});

When('I lock the Payment Plan', () => {
  cy.get('[data-cy="button-lock-plan"]').click({
    force: true,
  });
  cy.get('[data-cy="button-submit"]').click({
    force: true,
  });
});

Then('I see the entitlements input', () => {
  cy.get('[data-cy=input-entitlement-formula] > .MuiSelect-root').click({
    force: true,
  });
});

When('I choose the steficon rule', () => {
  cy.get('[data-cy="select-option-0"]').click();
});

And('I apply the steficon rule', () => {
  cy.get('[data-cy="button-apply-steficon"]').click({ force: true });
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I see the entitlements calculated', () => {
  cy.get('[data-cy="total-entitled-quantity-usd"]').should('not.be.empty');
});

And('And I am able to set up FSPs', () => {
  cy.get('[data-cy="button-set-up-fsp"]').click({ force: true });
});

Then('I should see the Set up FSP page', () => {
  cy.get('[data-cy="page-header-title"]').contains('Set up FSP');
});
