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