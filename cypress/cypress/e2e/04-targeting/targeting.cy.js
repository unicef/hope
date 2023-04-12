/// <reference types="cypress" />

context("Targeting", () => {
  let programName = "TargetingProgram";

  beforeEach(() => {
    cy.initScenario("targeting");
    cy.visit("/api/unicorn/");
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get("input").contains("Log in").click();
  });

  it.skip("Can visit the targeting page and create a target population", () => {
    cy.visit("/");
    cy.get("span").contains("Targeting").click();
    cy.get("h5").contains("Targeting");
    cy.get('[data-cy="button-target-population-create-new"]').click({
      force: true
    });
    cy.uniqueSeed().then((seed) => {
      const targetPopulationName = `test TP ${seed}`;
      cy.get('[data-cy="input-name"]')
        .eq(1)
        .type(targetPopulationName, { force: true });
      cy.get('[data-cy="input-program"]').first().click();
      cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
      cy.get(`[data-cy="select-option-${programName}-${seed}"]`).click();
      cy.get('[data-cy="button-target-population-add-criteria"]').click();

      cy.get('[data-cy="button-household-rule"]', {
        timeout: 10000
      }).click();
      cy.get('[data-cy="autocomplete-target-criteria"]')
        .click()
        .type("address");

      // TODO
      // cy.contains("Address").click();
      // cy.get('[data-cy="input-filters[0].value"]')
      //   .click()
      //   .type(`TargetingVille-${seed}`);
      // cy.get('[data-cy="button-target-population-add-criteria"]').eq(1).click();
      // cy.get("h6").contains("Households");
      // cy.get(
      //   "[data-cy=button-target-population-create] > .MuiButton-label"
      // ).click();
      // cy.get("h6").contains("Targeting Criteria");
      // cy.get('[data-cy="status-container"]').contains("OPEN");
      // cy.get('[data-cy="button-target-population-lock"]').click({
      //   force: true
      // });
      // cy.get('[data-cy="button-target-population-modal-lock"]').click({
      //   force: true
      // });
      // cy.get("h6").contains("Targeting Criteria");
      // cy.get('[data-cy="status-container"]').contains("LOCKED");
      // cy.get('[data-cy="button-target-population-send-to-hope"]').click({
      //   force: true
      // });
      // cy.get('[data-cy="button-target-population-modal-send-to-hope"]').click();
      // cy.get("h6").contains("Targeting Criteria");
      // cy.get('[data-cy="status-container"]').contains("READY");
    });
  });
});
