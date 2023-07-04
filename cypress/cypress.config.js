const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require("cy-verify-downloads");
const { execSync } = require("child_process");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      on("task", verifyDownloadTasks);
      on("after:run", (results) => {
        console.log("Gagagaggaga");
        const { execSync } = require("child_process");
        const exec = (command) => {
          execSync(command, {
            stdio: "inherit",
          });
        };
        exec(
          'curl -d "text=Slack Report from tests:" -d "channel=C05EKHETMT9" -H "Authorization: Bearer xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ" -X POST https://slack.com/api/chat.postMessage'
        );
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
