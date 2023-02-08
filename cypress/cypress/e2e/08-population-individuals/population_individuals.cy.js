/// <reference types="cypress" />

context("Population Individuals", () => {
  beforeEach(() => {
    cy.visit("/api/unicorn/");
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get("input").contains("Log in").click();
  });
  it("Can visit the Population Individuals page and go to Population Individual Details page", () => {
    cy.visit("/");
    cy.get("span").contains("Population").click();
    cy.get("span").contains("Individuals");
    cy.get("span").contains("Households");
    cy.get("span").contains("Individuals").click();
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.get("div").contains("Individuals");
    cy.get('[data-cy="table-title"]').contains("Individuals");
    cy.get('[data-cy="individual-table-row"]').first().click({ force: true });
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.get('[data-cy="page-header-container"]').contains("Individual ID:");
    cy.get("h6").contains("Bio Data");
    cy.get("h6").contains("Vulnerabilities");
    cy.get("h6").contains("Activity Log");
  });
});
