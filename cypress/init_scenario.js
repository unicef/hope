#!/usr/bin/env node
const { execSync } = require("child_process");

const exec = (command) => {
  execSync(command, {
    stdio: "inherit",
  });
};

const args = process.argv.slice(2);

const scenario = args[0];
const seed = args[1];

const command = `curl -X POST http://localhost:8082/api/cypress/ --data "command=init-e2e-scenario&scenario=${scenario}&seed=${seed}"`;
exec(command);
