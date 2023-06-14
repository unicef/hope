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
import addContext from "mochawesome/addContext";

require("cy-verify-downloads").addCustomCommand();
const uniqueSeed = Date.now();
Cypress.Commands.add("uniqueSeed", () => uniqueSeed);
Cypress.Commands.add("createExcel", () => {
  cy.uniqueSeed().then((seed) => {
    cy.exec(
      `yarn run generate-xlsx-files ${Cypress.config().baseUrl} 1 ${seed}`,
      { failOnNonZeroExit: false }
    );
  });
});
Cypress.Commands.add("adminLogin", () => {
  cy.session("testSessionName", () => {
    cy.visit("/api/unicorn/");
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get("input").contains("Log in").click();
  });
});

Cypress.Commands.add("navigateToHomePage", () => {
  cy.visit("/");
});

Cypress.Commands.add("initScenario", (scenario) => {
  cy.uniqueSeed().then((seed) => {
    cy.exec(
      `yarn init-scenario ${Cypress.config().baseUrl} ${scenario} ${seed}`
    );
  });
});

Cypress.Commands.add("scenario", (steps: Array) => {
  let outputText = "";
  steps.forEach((step, index) => {
    outputText += index + 1 + ". " + step + "\n";
  });
  Cypress.once("test:after:run", (test) => {
    addContext(
      { test },
      {
        title: "Scenario",
        value: outputText,
      }
    );
  });
});

Cypress.on("fail", (error, runnable) => {
  Cypress.once("test:after:run", (test) => {
    addContext(
      { test },
      {
        title: "Error",
        value: error.stack,
      }
    );
  });
  Cypress.once("test:after:run", (test) => {
    let pathName = runnable.titlePath();
    let lastElementInPathName = pathName.pop();
    if (lastElementInPathName.includes("after each")) {
      lastElementInPathName = test.title + " -- after each hook";
    }
    if (lastElementInPathName.includes("before each")) {
      lastElementInPathName = test.title + " -- before each hook";
    }
    const screenshot = `/cypress/cypress/cypress/reports/mochareports/assets/${Cypress.spec.relative
      .split("/")
      .at(-2)}/${Cypress.spec.name}/${pathName.join(
      " -- "
    )} -- ${lastElementInPathName} (failed).png`;

    addContext({ test }, screenshot);
  });
  throw new Error();
});
