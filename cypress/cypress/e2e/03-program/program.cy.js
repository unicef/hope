/// <reference types="cypress" />

context("Program", () => {
  beforeEach(() => {
    cy.adminLogin()
    cy.visit("/");
    cy.get("span").contains("Programme Management").click();
    cy.get("h5").should('contain', "Programme Management");
    });
  it("visit the Programs page and create a program", () => {
    cy.get('[data-cy="button-new-program"]').click({ force: true });
    cy.get("h6").contains("Set-up a new Programme");
    cy.uniqueSeed().then((seed) => {
      const programName = `test program ${seed}`;
      cy.get('[data-cy="input-programme-name"]').type(programName);
      cy.get('[data-cy="input-cash-assist-scope"]').first().click();
      cy.get('[data-cy="select-option-Unicef"]').click();
      cy.get('[data-cy="input-sector"]').first().click();
      cy.get('[data-cy="select-option-Multi Purpose"]').click();
      cy.get('[data-cy="input-start-date"]').click().type("2023-04-10");
      cy.get('[data-cy="input-end-date"]').click().type("2025-04-30");
      cy.get('[data-cy="input-description"]')
        .first()
        .click()
        .type("test description");
      cy.get('[data-cy="input-budget"]')
        .first()
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}9999");
      cy.get('[data-cy="input-admin-area"]').click().type("Some Admin Area");
      cy.get('[data-cy="input-population-goal"]')
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}4000");
      cy.get('[data-cy="button-save"]').click({ force: true });
      cy.get("h6").should('contain', "Programme Details");
      cy.get('[data-cy="button-activate-program"]').click({ force: true });
      cy.get('[data-cy="button-activate-program-modal"]').click({ force: true });
      cy.get('[data-cy="status-container"]').should('contain', "ACTIVE");
    });
  });


  })



