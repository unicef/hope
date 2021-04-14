const { spawn } = require('child_process');

module.exports.executeShellPlus = (queries) => {
  return new Promise((resolve, reject) => {
    const [
      command,
      ...parameters
    ] = 'docker-compose exec -T backend python ./manage.py shell_plus'.split(
      ' ',
    );

    const shellPlus = spawn(command, parameters);
    shellPlus.stdout.setEncoding('utf8');

    shellPlus.stdout.on('close', (code) => {
      resolve(code);
    });

    shellPlus.stderr.on('data', (data) => {
      reject(new Error(`stderr: ${data.toString()}`));
    });

    queries.forEach((query) => {
      shellPlus.stdin.write(`${query}\n`);
    });
    shellPlus.stdin.write('exit\n');
  });
};
