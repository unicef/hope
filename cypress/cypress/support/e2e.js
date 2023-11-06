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
  Cypress.session.clearCurrentSessionData();
  Cypress.session.clearAllSavedSessions();
  cy.visit("/");
  const expected_url =
    Cypress.config().baseUrl + "/api/unicorn/login/?next=/api/unicorn/";
  function checkApiUrl(n) {
    cy.url().then((url) => {
      if (expected_url !== url) {
        cy.reload();
        cy.wait(1000);
        cy.visit("/api/unicorn/");
        cy.get('div[id="header"]')
          .invoke("css", "background-color")
          .then((bgcolor) => {
            //rgb(255, 102, 0)
            cy.log(bgcolor.toString());
          });
        if (n > 0) {
          return checkApiUrl(n - 1);
        } else {
          return false;
        }
      } else {
        return true;
      }
    });
  }
  function resolveAThing(n) {
    cy.visit("/api/unicorn/");
    checkApiUrl(5);
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get("input").contains("Log in").click();
    cy.get("a").contains("HOPE Administration");
    cy.navigateToHomePage();
    cy.get("div")
      .find("div")
      .find("div")
      .eq(1)
      .then(($text) => {
        if ($text.text() === "Sign in" && n > 0) {
          cy.log("retry: " + (10 - n + 1));
          return resolveAThing(n - 1);
        }
      });
  }
  return resolveAThing(10);
});

Cypress.Commands.add("checkIfLoggedIn", () => {
  cy.visit("/");
  function retryCheck(n) {
    cy.url().should("contain", Cypress.config().baseUrl);
    cy.url().then((url) => {
      cy.log(url);
      if (url.includes("login")) {
        cy.adminLogin();
      } else if (url.includes("programs")) {
        return;
      }
      if (n === 0) cy.url().should("include", "/programs/all/list");
      cy.wait(1000);
      return retryCheck(n - 1);
    });
  }
  return retryCheck(10);
});

Cypress.Commands.add("checkStatus", (status = "IN REVIEW", repeat = 10) => {
  function retryCheck(n) {
    cy.wait(100);
    cy.get('[data-cy="status-container"]').then((value) => {
      cy.log(value.text());
      if (value.text().includes(status)) {
        return;
      }
      if (n === 0) cy.get('[data-cy="status-container"]').contains(status);
      cy.wait(500);
      return retryCheck(n - 1);
    });
  }
  return retryCheck(repeat);
});

Cypress.Commands.add("navigateToHomePage", () => {
  cy.visit("/");
  cy.url().should("include", "/programs/all/list");
  cy.get('div[data-cy="global-program-filter"]', { timeout: 10000 })
    .contains("All Programmes", { timeout: 10000 })
    .click();
  cy.get('li[role="option"]').contains("Test Program").click();
});

Cypress.Commands.add("initScenario", (scenario) => {
  cy.uniqueSeed().then((seed) => {
    cy.exec(
      `yarn init-scenario ${Cypress.config().baseUrl} ${scenario} ${seed}`
    );
    cy.wait(1000);
  });
});

Cypress.Commands.add(
  "containsIfExist",
  { prevSubject: "element" },
  (subject, data) => {
    if (data) {
      return cy.get(subject).contains(data);
    }
    return cy.get(subject);
  }
);

Cypress.Commands.add("scenario", (steps) => {
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
  throw error;
});
