/// <reference types="cypress" />

context("Availibility", () => {
  it("Main page is available and shows the AD login view", () => {
    cy.visit("/");
    cy.get("p").should("contain", "Login via Active Directory");
  });
  it("Admin panel is available", () => {
    cy.visit("/api/unicorn/");
    cy.get("a").should("contain", "HOPE Administration");
  });
});
