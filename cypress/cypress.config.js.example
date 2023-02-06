const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    projectId: "cypress",
    baseUrl: "http://localhost:8082",
    env: {
      username: 'example',
      password: 'example'
    },
    reporter: "junit",
    reporterOptions: {
      mochaFile: "cypress/results/results-[hash].xml",
      toConsole: true,
    },
  },
});
