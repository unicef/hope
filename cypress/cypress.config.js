const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require("cy-verify-downloads");
module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      on("task", verifyDownloadTasks);
    },
    projectId: "cypress",
    baseUrl: "http://localhost:8082",
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
