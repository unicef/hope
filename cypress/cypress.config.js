const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require('cy-verify-downloads');
module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
      on('task', verifyDownloadTasks);
    },
    projectId: "cypress",
    failOnNonZeroExit: false,
    baseUrl: "http://localhost:8082",
    env: {
      username: 'cypress-username',
      password: 'cypress-password'
    },
    reporter: "junit",
    reporterOptions: {
      mochaFile: "cypress/results/results-[hash].xml",
      toConsole: true,
    },
  },
});
