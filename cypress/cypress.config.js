const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require('cy-verify-downloads');
//const {downloadFile} = require('cypress-downloadfile/lib/addPlugin')
module.exports = defineConfig({
  reporter: 'cypress-mochawesome-reporter',
  e2e: {
    setupNodeEvents(on, config) {
      on('task', verifyDownloadTasks);
      require('cypress-mochawesome-reporter/plugin')(on);
    },
    projectId: "cypress",
    baseUrl: "http://localhost:8082",
    env: {
      username: 'cypress-username',
      password: 'cypress-password'
    },
   // reporter: "junit",
    failOnStatusCode: false,
    reporterOptions: {
      saveHtml:true,
      mochaFile: "cypress/results/results-[hash].xml",
      toConsole: true,
    },
  },
});
