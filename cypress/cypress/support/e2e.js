// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import "cypress-file-upload";
import "./commands";
require('cy-verify-downloads').addCustomCommand();
const uniqueSeed = Date.now();
Cypress.Commands.add("uniqueSeed", () => uniqueSeed);
Cypress.Commands.add("createExcel",()=>{
  cy.uniqueSeed().then((seed) => {
    cy.exec(
      `yarn run generate-xlsx-files ${Cypress.config().baseUrl} 1 ${seed}`,{failOnNonZeroExit: false}
    );
  });
})

Cypress.Commands.add("adminLogin", () => {
  cy.visit("/api/unicorn/");
  cy.get('input[name="username"]').type(Cypress.env("username"));
  cy.get('input[name="password"]').type(Cypress.env("password"));
  cy.get("input").contains("Log in").click();
})

Cypress.Commands.add("initScenario", (scenario) => {
  cy.uniqueSeed().then((seed) => {
    cy.exec(
      `yarn init-scenario ${Cypress.config().baseUrl} ${scenario} ${seed}`
    );
  });
})