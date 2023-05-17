const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require('cy-verify-downloads');
module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      on('task', verifyDownloadTasks);
    },
    projectId: "cypress",
    defaultCommandTimeout:10000,
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
