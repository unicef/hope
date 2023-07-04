#!/usr/bin/env node
const { execSync } = require("child_process");

const exec = (command) => {
  execSync(command, {
    stdio: "inherit",
  });
};

const fs = require("fs");
const { Chart } = require("chart.js");

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

      const chart = {
        type: "doughnut",
        data: {
          labels: ["Passed", "Failed", "ToDo"],
          datasets: [
            {
              data: [
                report.stats.passes,
                report.stats.failures,
                report.stats.pending,
              ],
              backgroundColor: [
                "rgb(109,255,99)",
                "rgb(235,54,54)",
                "rgb(86,255,249)",
              ],
              hoverOffset: 4,
            },
          ],
        },
      };
      const encodedChart = encodeURIComponent(JSON.stringify(chart));
      const chartUrl = `https://quickchart.io/chart?c=${encodedChart}`;

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
  }
);
