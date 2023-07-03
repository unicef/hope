const { defineConfig } = require("cypress");
const { verifyDownloadTasks } = require("cy-verify-downloads");
module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      on("task", verifyDownloadTasks);
      on("after:run", (results) => {
        //curl -d "text=Hi I am a bot that can post messages to any public channel." -d "channel=C05EKHETMT9" -H "Authorization: Bearer xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ" -X POST https://slack.com/api/chat.postMessage
        console.log("Gagagaggaga");
        // request("POST", "https://slack.com/api/chat.postMessage", {
        //   auth: "Bearer xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ",
        //   body: {
        //     text: "Hi I am a bot that can post messages to any public channel.",
        //     channel: "C05EKHETMT9",
        //   },
        // }).then((res) => {
        //   console.log("Gugugugugu");
        //   console.log(res);
        fetch("https://slack.com/api/chat.postMessage", {
          method: "POST",
          headers: {
            "Content-type": "application/json",
            Authorization:
              "Bearer xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ",
          },
          data: JSON.stringify({
            text: "Hi I am a bot that can post messages to any public channel.",
            channel: "C05EKHETMT9",
          }),
        }).then((r) => {
          console.log(r.status);
        });
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
