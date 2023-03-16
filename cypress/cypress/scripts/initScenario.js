#!/usr/bin/env node
const { execSync } = require("child_process");

const exec = (command) => {
  execSync(command, {
    stdio: "inherit",
  });
};

const args = process.argv.slice(2);

const serverAddress = args[0];
const scenario = args[1];
const seed = args[2];

const command = `curl -X POST ${serverAddress}/api/cypress/ --data "command=init-e2e-scenario&scenario=${scenario}&seed=${seed}"`;
exec(command);
