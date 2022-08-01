import { When, Then, And, Given } from 'cypress-cucumber-preprocessor/steps';

Given("I am authenticated", () => {
    cy.visit('/api/unicorn/');
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get('input').contains('Log in').click();
})

When("I visit the main dashboard", () => {
    cy.visit("/")
})

Then("I should see the side panel with RDI option", () => {
    cy.get('span').contains('Registration Data Import');
})

When("I click on RDI option", () => {
    cy.get('span').contains('Registration Data Import').click();
})

Then("I should see the RDI page", () => {
    cy.get('h5').contains('Registration Data Import');
})

When("I click the import button", () => {
    cy.get('button > span').contains('IMPORT').click({ force: true });
})

Then("I should see the file import modal", () => {
    cy.get("h2").contains("Select File to Import").click();
})


function hexStringToByte(str) {
    if (!str) {
      return new Uint8Array(0);
    }
    
    var a = [];
    for (var i = 0, len = str.length; i < len; i+=2) {
      a.push(parseInt(str.substr(i,2),16));
    }
    
    return new Uint8Array(a);
  }

When("I select the xlsx file", () => {
    cy.get('[data-cy="import-type-select"]').click();
    cy.get('[data-cy="excel-menu-item"]').click();
    const fileName = 'RDI-VALID.xlsx'
    const filePath = "cypress/fixtures/" + fileName
    

})


Then("I see it was chosen", () => {

})

When("I press import", () => {
    // cy.get('button > span').contains('IMPORT').click({ force: true });
})