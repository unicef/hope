const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require('cy-verify-downloads');
module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      on('task', verifyDownloadTasks);
    },
    projectId: "cypress",
    baseUrl: "http://localhost:8082",
    env: {
      username: 'root',
      password: 'fKXRA1FRYTA1lKfdg'
    },
    reporter: "junit",
    reporterOptions: {
      mochaFile: "cypress/results/results-[hash].xml",
      toConsole: true,
    },
  },
});
