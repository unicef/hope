const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require("cy-verify-downloads");
module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      on("task", verifyDownloadTasks);
      on("after:run", (results) => {
        if (results) {
          const fs = require("fs");
          fs.writeFile(
            "cypress/reports/test.txt",
            results.totalPassed.toString(),
            (err) => {
              if (err) {
                console.error(err);
              }
              // file written successfully
            }
          );
          // if (results.totalPassed !== results.totalTests) {
          //   throw "Tests fails: " + results.totalFailed.toString();
          // }
          // results will be undefined in interactive mode
          // console.log(
          //   results.totalPassed,
          //   "out of",
          //   results.totalTests,
          //   "passed"
          // );
        }
      });
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
