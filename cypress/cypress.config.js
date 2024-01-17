const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require("cy-verify-downloads");

module.exports = defineConfig({
  experimentalMemoryManagement: true,
  numTestsKeptInMemory: 20,
  retries: 0,
  viewportWidth: 1920,
  viewportHeight: 1080,
  e2e: {
    testIsolation: false,
    experimentalRunAllSpecs: true,
    setupNodeEvents(on, config) {
      on("task", verifyDownloadTasks);
    },
    projectId: "cypress",
    baseUrl: "http://localhost:8082",
    specPattern: [
      "cypress/e2e/00-Login/*.js",
      "cypress/e2e/02-registration-data-import/*.js",
      "cypress/e2e/03-program-management/*.js",
      "cypress/e2e/04-targeting/*.js",
      "cypress/e2e/05-payment-module/*.js",
      "cypress/e2e/06-payment-verification/*.js",
      "cypress/e2e/07-population-module/*.js",
      "cypress/e2e/08-grievance/*.js",
      "cypress/e2e/09-global-program-filter/*.js",
      "cypress/e2e/10-program-details/*.js",
      "cypress/e2e/11-accountability/*.js",
      "cypress/e2e/404/*.js",
    ],
    env: {
      username: "cypress-username",
      password: "cypress-password",
    },
    screenshotOnRunFailure: true,
    screenshotsFolder: "cypress/reports/mochareports/assets/",
    reporter: "cypress-multi-reporters",
    reporterOptions: {
      configFile: "reporterOpts.json",
    },
  },
});
