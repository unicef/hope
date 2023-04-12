/// <reference types="cypress" />

context("Payment Verification", () => {
  beforeEach(() => {
    cy.visit("/api/unicorn/");
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get("input").contains("Log in").click();
  });

  it.skip("Can see the Cash Plan Details Page", () => {
    cy.visit("/");
    cy.get("span").contains("Payment Verification").click();
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.get("h6").contains("List of Cash Plans");
    return; // TODO: must seed with some cash plan
    cy.get('[data-cy="cash-plan-table-row"]').first().click();
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.get('[data-cy="page-header-container"]').contains("Payment Plan");
    cy.get("h6").contains("Cash Plan Details");
    cy.get("h6").contains("Verification Plans Summary");
  });
});
