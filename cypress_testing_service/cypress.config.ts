import { defineConfig } from "cypress";

export default defineConfig({
  viewportWidth: 1366,
  viewportHeight: 768,
  reporter: "mocha-junit-reporter",

  reporterOptions: {
    mochaFile: "cypress/reports/junit/test-results.[hash].xml",
    testsuitesTitle: false,
  },

  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    // https://docs.cypress.io/guides/references/migration-guide#Plugins-File-Removed
    setupNodeEvents(on, config) {
      return require("./cypress/plugins/index.ts")(on, config);
    },
    baseUrl: "http://localhost:8082/",
    specPattern: "cypress/e2e/**/*.feature",
  },

  component: {
    devServer: {
      framework: "create-react-app",
      bundler: "webpack",
    },
  },
});
