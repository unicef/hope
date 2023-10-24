const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require("cy-verify-downloads");

module.exports = defineConfig({
  experimentalMemoryManagement: true,
<<<<<<< HEAD
  numTestsKeptInMemory: 20,
=======
  numTestsKeptInMemory: 0,
>>>>>>> develop
  retries: 0,
  viewportWidth: 1920,
  viewportHeight: 1080,
  e2e: {
    testIsolation: false,
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
