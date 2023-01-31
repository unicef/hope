/// <reference types="cypress" />

context("RDI", () => {
  beforeEach(() => {
    cy.visit("/api/unicorn/");
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get("input").contains("Log in").click();
  });
  it("Registration Data Import", () => {
    cy.visit("/");
    cy.get("span").contains("Registration Data Import").click();
    cy.get("h5").contains("Registration Data Import");
    cy.get("button > span").contains("IMPORT").click({ force: true });
    cy.get("h2").contains("Select File to Import").click();
  });
});
