import { When, Then, Given, And } from 'cypress-cucumber-preprocessor/steps';
import {
  fillProgramForm,
  fillTargetingForm,
  getIndividualsFromRdiDetails,
  uniqueSeed,
} from '../../procedures/procedures';

let programName;
let targetPopulationName;
let individualIds;

const maxInt = 2147483647;

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
  cy.get('button > span').contains('Individuals').click({ force: true });
  individualIds = getIndividualsFromRdiDetails(cy, 3);
});

Given('Each imported individual has a payment channel', () => {
  individualIds.forEach((individualId) => {
    cy.visit('/api/unicorn/payment/paymentchannel/add/');
    cy.get('#id_individual').select(individualId);
    cy.get('#id_delivery_mechanism').select('Transfer');
    cy.get('input[name="_save"]').click();
  });
});

Given('There are steficon rules provided', () => {
  cy.visit('/api/unicorn/steficon/rule/add/')
  cy.get("#id_name").type(uniqueSeed)
  cy.get("#id_type").select("Payment Plan")
  cy.get('#id_definition_container').click().type('result.value=0')
  cy.get('input[name="enabled"]').click();
  cy.get('input[name="_save"]').click();
  cy.get('p').contains('Please correct the error below.').should('not.exist');

  cy.visit('/api/unicorn/steficon/rulecommit/add/');
  cy.get("#id_rule").select(uniqueSeed);
  cy.get('#id_definition').clear().type('result.value=100');
  cy.get('input[name="is_release"]').click();
  cy.get('input[name="enabled"]').click();
  cy.get('input[name="version"]').type((parseInt(uniqueSeed) % maxInt).toString());
  cy.get('input[name="affected_fields"]').type('[]');
  cy.get('input[name="_save"]').click();
  cy.get('p').contains('Please correct the error below.').should('not.exist');

  cy.visit('/');
  clearCache();
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
  cy.wait(3000); // eslint-disable-line cypress/no-unnecessary-waiting
});

Then('I should see the Payment Plan details page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Payment Plan ID', {
    timeout: 10000,
  });
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
  // cy.get('[data-cy="select-option-0"]').click();
  cy.get('[data-cy="input-entitlement-formula"]').click({force: true});
  // cy.get(`[data-cy="select-option-${uniqueSeed}"`).click({force: true});
  cy.get('li').contains(uniqueSeed).click({force: true});
});

And('I apply the steficon rule', () => {
  cy.get('[data-cy="button-apply-steficon"]').click({ force: true });
  cy.reload();
});

Then('I see the entitlements calculated', () => {
  cy.get('[data-cy="total-entitled-quantity-usd"]').contains('USD');
});

And('I am able to set up FSPs', () => {
  cy.get('[data-cy="button-set-up-fsp"]', {
    timeout: 10000,
  }).click({ force: true });
});

Then('I should see the Set up FSP page', () => {
  cy.get('[data-cy="page-header-container"]').contains('Set up FSP', {
    timeout: 10000,
  });
});

When('I select the delivery mechanisms', () => {
  cy.get('[data-cy="select-deliveryMechanisms[0].deliveryMechanism"]').click();
  cy.get('[data-cy="select-option-Transfer"]').click();
  cy.get('[data-cy="button-next-save"]').click({ force: true });
});

Then('I should be able to assign FSPs', () => {
  cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]');
});

When('I select the FSPs and save', () => {
  cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]').click();
  cy.get('[data-cy="select-option-Test FSP Transfer"]').click();
  cy.get('[data-cy="button-next-save"]').click({ force: true });
})

Then('I should see volumes by delivery mechanisms', () => {
  // TODO
  // cy.get("h6").contains("Volume by Delivery Mechanism in USD", {timeout: 10000});
})

When("I lock the FSPs", () => {
  cy.get("[data-cy='button-lock-plan']").click({ force: true })
  cy.get("[data-cy='button-submit']").click({ force: true })

})

Then("I should see that the status is FSP Locked", () => {
  cy.get("[data-cy='status-container']").contains("FSP Locked")
})