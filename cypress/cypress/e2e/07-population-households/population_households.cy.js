/// <reference types="cypress" />

context("Population Households", () => {
  beforeEach(() => {
    cy.adminLogin()
  
  });
  it("Can visit the Population Households page and go to Population Household Details page", () => {
    cy.visit("/");
    cy.get("span").contains("Population").click();
    cy.get("span").contains("Individuals");
    cy.get("span").contains("Households");
    cy.get("span").contains("Households").click();
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.get("div").contains("Households");
    cy.get('[data-cy="table-title"]').contains("Households");
    cy.get('[data-cy="household-table-row"]').first().click({ force: true });
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.get('[data-cy="page-header-container"]').contains("Household ID:");
    cy.get("h6").contains("Details");
    cy.get("h6").contains("Benefits");
    cy.get("h6").contains("Household Composition");
    cy.get("h6").contains("Individuals in Household");
    cy.get("h6").contains("Payment Records");
    cy.get("h6").contains("Vulnerabilities");
    cy.get("h6").contains("Registration Details");
    cy.get("h6").contains("Activity Log");
  });
});
