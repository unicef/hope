export const fillProgramForm = (cy) => {
  const programName = `test program ${uniqueSeed}`
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

export const fillTargetingForm = (cy, programName, seed) => {
  const targetPopulationName = `test TP ${seed}`;
  cy.get('[data-cy="input-name"]').first().type(targetPopulationName);
  cy.get('[data-cy="input-program"]').first().click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get(`[data-cy="select-option-${programName}"]`).click();
  cy.get('[data-cy="button-target-population-add-criteria"]').click();
  cy.get('[data-cy="button-household-rule"]', {
    timeout: 10000,
  }).click();
  cy.get('[data-cy="autocomplete-target-criteria"]')
    .click()
    .type('residence status');
  cy.contains('Residence status').click();
  // TODO: add filter for e.g. minutes_to_school == seed
  cy.get('[data-cy="select-filters[0].value"]').click();
  cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('li').eq(3).click(); // TODO: improve that
  return targetPopulationName
};

export const uniqueSeed = Date.now().toString();
