#!/usr/bin/env node
const { execSync } = require("child_process");

const exec = (command) => {
  execSync(command, {
    stdio: "inherit",
  });
};

exec(
  'curl -d "text=E2E Tests Report: " -d "channel=C05EKHETMT9" -H "Authorization: Bearer xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ" -X POST https://slack.com/api/chat.postMessage'
);
const fs = require("fs");
fs.readFile(
  "./cypress/reports/mochareports/report.json",
  "utf8",
  (err, jsonString) => {
    if (err) {
      console.log("File read failed:", err);
      return;
    }
    try {
      const report = JSON.parse(jsonString);
      const command = `curl -d "text=Tests Passed: ${report.stats.passes} 
        \nTests Failed: ${report.stats.failures}
        \nTests ToDo: ${report.stats.pending}\n" -d "channel=C05EKHETMT9" -H "Authorization: Bearer xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ" -X POST https://slack.com/api/chat.postMessage`;
      exec(command);
      exec("zip -r -j report.zip ./cypress/reports/mochareports");

      let coverage =
        ((report.stats.tests - report.stats.pending) / report.stats.tests) *
        100;
      const chart = {
        type: "doughnut",
        data: {
          labels: ["Passed", "Failed", "ToDo"],
          labelColors: "#000",
          datasets: [
            {
              data: [
                report.stats.passes,
                report.stats.failures,
                report.stats.pending,
              ],
              borderColor: "rgba(255,255,255,0.8)",
              backgroundColor: [
                "rgb(72,159,52)",
                "rgb(215,64,95)",
                "rgb(36,113,164)",
              ],
              hoverOffset: 40,
            },
          ],
        },
        options: {
          plugins: {
            datalabels: {
              color: ["#000", "#000", "#000"],
              anchor: "end",
              align: "end",
            },
            doughnutlabel: {
              labels: [
                {
                  text: coverage.toFixed(0).toString() + "%",
                  color: "#000",
                  font: { size: 30 },
                },
                { text: "Coverage", color: "#000" },
              ],
            },
          },
        },
      };
      const encodedChart = encodeURIComponent(JSON.stringify(chart));
      const chartUrl = `https://quickchart.io/chart?format=jpg&bkg=white&c=${encodedChart}`;
      console.log("\n\n" + chartUrl + "\n\n");

      const request = require("request");

      const SLACK_BOT_USER_TOKEN =
        "xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ";

      function sendMessage(data) {
        request(
          {
            url: "https://slack.com/api/chat.postMessage",
            method: "POST",
            json: data,
            headers: {
              "Content-Type": "application/json; charset=utf-8",
              Authorization: `Bearer ${SLACK_BOT_USER_TOKEN}`,
            },
          },
          function (error, response, body) {
            if (error || response.statusCode !== 200) {
              console.error("Error sending slack response:", error);
            } else if (!response.body.ok) {
              console.error("Slack responded with error:", response.body);
            } else {
              // All good!
            }
          }
        );
      }

      sendMessage({
        text: "Chart data update",
        channel: "C05EKHETMT9",
        blocks: [
          {
            type: "image",
            title: {
              type: "plain_text",
              text: "Latest data",
            },
            block_id: "quickchart-image",
            image_url: chartUrl,
            alt_text: "Chart showing latest data",
          },
        ],
      });
    } catch (err) {
      console.log("Error parsing JSON string:", err);
    }
    exec(
      'curl -F file=@report.zip -H "Authorization: Bearer xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ"  -F channels=C05EKHETMT9 -X POST https://slack.com/api/files.upload'
    );
  }
);
