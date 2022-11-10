const {
    execSync
} = require('child_process');

const exec = (command) => {
    execSync(command, {
        stdio: 'inherit'
    });
}

const args = process.argv.slice(2);
exec("docker-compose run --rm backend ./manage.py generate_rdi_xlsx_files " + args.join(" "));

const copy = require('copy');
copy('../backend/generated/*', 'cypress/fixtures', function (err, files) {
    if (err) throw err;
    console.log("Files copied successfully");
})