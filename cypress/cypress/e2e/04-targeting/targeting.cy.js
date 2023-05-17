/// <reference types="cypress" />
context("Targeting", () => {
  let programName = "TargetingProgram";
  beforeEach(() => {
    cy.adminLogin()
    cy.visit("/");
    cy.initScenario("targeting");
    cy.get("span").contains("Targeting").click();
    cy.get("h5").should('contain', "Targeting");
  });
  it("Create a target population", () => {
    cy.get('[data-cy="button-target-population-create-new"]').click({ force: true });
    cy.uniqueSeed().then((seed) => {
      const targetPopulationName = `test TP ${seed}`;
      cy.get('input[data-cy="input-name"]').type(targetPopulationName, { force: true });
      cy.get('[data-cy="input-program"]').first().click();
      cy.get(`[data-cy="select-option-${programName}-${seed}"]`).click();
      cy.get('[data-cy="button-target-population-add-criteria"]').click();
      cy.get('[data-cy="button-individual-rule"]').should('be.not.disabled',{timeout:100000}).click({ force: true })
      cy.get('[data-cy="autocomplete-target-criteria"]').should("be.visible")
      cy.get('[data-cy="autocomplete-target-criteria-option-0"]').type('Age {downArrow}{enter}')
      cy.get('[data-cy="input-individualsFiltersBlocks[0].individualBlockFilters[0].value.from"]').type('0')
      cy.get('[data-cy="input-individualsFiltersBlocks[0].individualBlockFilters[0].value.to"]').type('100')
      cy.get('[data-cy="button-target-population-add-criteria"]').eq(1).click({ force: true })
      cy.get('[data-cy="criteria-container"]').should('to.visible')
      cy.get("[data-cy='button-target-population-create']").click({ force: true });
      cy.get('[data-cy="status-container"]').should('contain', "OPEN");
      cy.get('[data-cy="button-target-population-lock"]').should('to.visible',{timeout:100000},{ force: true });
      cy.get('[data-cy="label-Total Number of Households"]').invoke('text').should('not.contain', ' 0 ');
      cy.get('[data-cy="label-Targeted Individuals"]').invoke('text').should('not.contain', ' 0 ');
      cy.get('[data-cy="button-target-population-lock"]').click({ force: true });
      cy.get('[data-cy="button-target-population-modal-lock"]').click({ force: true });
      cy.get('[data-cy="status-container"]').should('contain', "LOCKED");
      cy.get('[data-cy="button-target-population-send-to-hope"]').click({ force: true });
      cy.get('[data-cy="button-target-population-modal-send-to-hope"]').click({ force: true });
      cy.get('[data-cy="status-container"]').should('contain', "READY FOR PAYMENT MODULE");
    });
  });
});
