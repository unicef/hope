#!/usr/bin/env node
const { execSync } = require("child_process");

const exec = (command) => {
    execSync(command, {
        stdio: "inherit",
    });
};

const fs = require("fs");
fs.readFile("./cypress/reports/mochareports/report.json", "utf8", (err, jsonString) => {
    if (err) {
        console.log("File read failed:", err);
        return;
    }
    try {
        const report = JSON.parse(jsonString);
        const command = `curl -d "text=
        Tests Passed: ${report.stats.passes} \n
        Tests Failed: ${report.stats.failures}\n
        Tests ToDo: ${report.stats.pending}\n" -d "channel=C05EKHETMT9" -H "Authorization: Bearer xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ" -X POST https://slack.com/api/chat.postMessage`;
        exec(command);
    } catch (err) {
        console.log("Error parsing JSON string:", err);
    }});
