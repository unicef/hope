/// <reference types="cypress" />

context("RDI", () => {
  beforeEach(() => {
    cy.uniqueSeed().then((seed) => {
      cy.exec(`yarn run generate-xlsx-files 1 --seed ${seed}`);
    });
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
    cy.get('[data-cy="import-type-select"]').click();
    cy.get('[data-cy="excel-menu-item"]').click();
    cy.get('[data-cy="input-name"]').type(
      "Test import ".concat(new Date().toISOString())
    );
    cy.uniqueSeed().then((seed) => {
      const fileName = `rdi_import_1_hh_1_ind_seed_${seed}.xlsx`;
      cy.fixture(fileName, "base64").then((fileContent) => {
        cy.get('[data-cy="file-input"]').attachFile({
          fileContent,
          fileName,
          mimeType:
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          encoding: "base64"
        });
      });
    });
    cy.get('[data-cy="number-of-households"]').contains(
      "1 Household available to import",
      {
        timeout: 10000
      }
    );
    cy.get('[data-cy="number-of-individuals"]').contains(
      "1 Individual available to import"
    );
    cy.get("div").contains("Errors").should("not.exist");
    cy.get('[data-cy="button-import-rdi"').click();
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.reload();
    cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
    // it lets the browser load the status

    cy.get("div").contains("IMPORT ERROR").should("not.exist");
    cy.get("div").contains("IN REVIEW");
  });
});
