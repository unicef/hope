#!/usr/bin/env node
const { execSync } = require("child_process");

const exec = (command) => {
  execSync(command, {
    stdio: "inherit",
  });
};

const request = require("request");
const SLACK_BOT_USER_TOKEN =
"xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ";
const CHANNEL = "C05EKHETMT9"

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
  text: "E2E Tests Report: ",
  channel: CHANNEL,
});

const fs = require("fs");
const { log } = require("console");
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
      const text=`Tests Passed: ${report.stats.passes}
                \nTests Failed: ${report.stats.failures}
                \nTests ToDo: ${report.stats.pending}\n`
        sendMessage({
          text: text,
          channel: CHANNEL,
        });

      let coverage =
        ((report.stats.tests - report.stats.pending) / report.stats.tests) * 100;

const QuickChart = require('quickchart-js');
const chart = new QuickChart();

chart.setWidth(500)
chart.setHeight(300);
chart.setVersion('2.9.4');

chart.setConfig({
  type: 'doughnut',
  data: {
    datasets: [
      {
        data: [
          report.stats.passes,
          report.stats.failures,
          report.stats.pending,
        ],
        backgroundColor: [
          'rgb(75, 192, 192)',
          'rgb(255, 99, 132)',
          'rgb(54, 162, 235)',
        ],
      },
    ],
    labels: ['Pass', 'Failed', 'ToDo'],
  },
  options: {
    plugins: {
      datalabels: {
        color: "#000",
        formatter: (value) => {
          if (value < 1) return '';
          return value;
        },
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
});
const chartUrl = chart.getUrl()
console.log("\n\n" + chartUrl + "\n\n");

      sendMessage({
        text: "Chart data update",
        channel: CHANNEL,
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
      `curl -F file=@report.zip -H "Authorization: Bearer ${SLACK_BOT_USER_TOKEN}" -F channels=${CHANNEL} -X POST https://slack.com/api/files.upload`
    );
  }
);
