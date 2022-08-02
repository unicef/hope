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


When("I select the xlsx file", () => {
    cy.get('[data-cy="import-type-select"]').click();
    cy.get('[data-cy="excel-menu-item"]').click();
    
    cy.get('[data-cy="input-name"]').type("Test import ".concat((new Date()).toISOString()));

    const fileName = 'rdi_1_hh_4_ind.xlsx'
    // check if file under that name is present
    // and generate file (instead of storing binary xlsx in repo)

    cy.fixture(fileName, 'base64').then(fileContent => {
        cy.get('[data-cy="rdi-file-input"]').upload({ fileContent, fileName, mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', encoding: 'base64' })
    })
})


Then("I see it was chosen", () => {
    cy.get('div').contains('1 Household available to import', { timeout: 10000 });
    cy.get('div').contains('4 Individuals available to import');
    cy.get('div').contains('Errors').should('not.exist');
})

When("I press import", () => {
    cy.get('[data-cy="button-import-rdi"').click();
})

Then("I should see a new import with status importing", () => {
    cy.get('div').contains('Status')
    cy.get('div').contains('IMPORTING')

    cy.wait(1000)
    cy.reload()
    cy.wait(500)
    cy.get('div').contains('IMPORT ERROR').should('not.exist');
})