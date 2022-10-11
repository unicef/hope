export const uniqueSeed = Date.now().toString();

export const fillProgramForm = (cy) => {
  const programName = `test program ${uniqueSeed}`;
  cy.get('[data-cy="input-programme-name"]').type(programName);
  cy.get('[data-cy="input-cash-assist-scope"]').first().click();
  cy.get('[data-cy="select-option-Unicef"]').click();
  cy.get('[data-cy="input-sector"]').first().click();
  cy.get('[data-cy="select-option-Multi Purpose"]').click();
  cy.get('[data-cy="input-start-date"]').click().type('2022-12-12');
  cy.get('[data-cy="input-end-date"]').click().type('2022-12-23');
  cy.get('[data-cy="input-description"]')
    .first()
    .click()
    .type('test description');
  cy.get('[data-cy="input-budget"]')
    .first()
    .click()
    .type('{backspace}{backspace}{backspace}{backspace}9999');
  cy.get('[data-cy="input-admin-area"]').click().type('Some Admin Area');
  cy.get('[data-cy="input-population-goal"]')
    .click()
    .type('{backspace}{backspace}{backspace}{backspace}4000');
  return programName;
};

export const fillTargetingForm = (cy, programName, address) => {
  const targetPopulationName = `test TP ${address}`;
  cy.get('[data-cy="input-name"]').first().type(targetPopulationName);
  cy.get('[data-cy="input-program"]').first().click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get(`[data-cy="select-option-${programName}"]`).click();
  cy.get('[data-cy="button-target-population-add-criteria"]').click();

  cy.get('[data-cy="button-household-rule"]', {
    timeout: 10000,
  }).click();
  cy.get('[data-cy="autocomplete-target-criteria"]').click().type('address');
  cy.contains('Address').click();
  cy.get('[data-cy="input-filters[0].value"]').click().type(address);
};

export const getIndividualsFromRdiDetails = (cy, expectedNumber, container) => {
  for (let i = 0; i < expectedNumber; i++) {
    cy.get('[data-cy="imported-individuals-table"]')
      .find(`tbody > tr:nth-child(${i + 1}) > td:nth-child(1)`)
      .then(($td) => {
        const individualId = $td.text().split(' (')[0];
        cy.log(`Saved individualId: ${individualId}`);
        container.push(individualId);
      });
  }
};
