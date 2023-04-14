const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require('cy-verify-downloads');
const {downloadFile} = require('cypress-downloadfile/lib/addPlugin')
module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      on('task', verifyDownloadTasks);
      on('task', {downloadFile})
      
      // implement node event listeners here
    },
    projectId: "cypress",
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
