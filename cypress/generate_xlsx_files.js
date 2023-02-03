#!/usr/bin/env node
const { execSync } = require("child_process");

const exec = (command) => {
  execSync(command, {
    stdio: "inherit",
  });
};

const args = process.argv.slice(2);

const size = args[0];
const seed = args[1];

const command = `curl -X POST http://localhost:8082/api/cypress/ --data "command=generate-xlsx-files&size=${size}&seed=${seed}"`;
// const command = `cd ../ && docker-compose run --rm backend ./manage.py generate_rdi_xlsx_files ${size} --seed ${seed}`;
exec(command);

const copy = require("copy");
copy("../backend/generated/*", "cypress/fixtures", function (err, files) {
  if (err) throw err;
  console.log("Files copied successfully");
});
