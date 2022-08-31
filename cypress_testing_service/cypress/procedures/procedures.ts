export const fillProgramForm = (cy) => {
  cy.get('[data-cy="input-programme-name"]').type(`test program ${uniqueSeed}`);
  cy.get('[data-cy="input-cash-assist-scope"]').first().click();
  cy.get('[data-cy="select-option-1"]').click();
  cy.get('[data-cy="input-sector"]').first().click();
  cy.get('[data-cy="select-option-1"]').click();
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
};

export const uniqueSeed = Date.now().toString();
