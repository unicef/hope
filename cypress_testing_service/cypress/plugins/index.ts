// ***********************************************************
// This plugins/index.js can be used to load plugins
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

// https://gist.github.com/csuzw/845b589549b61d3a5fe18e49592e166f

const cucumber = require('cypress-cucumber-preprocessor').default;
const browserify = require('@cypress/browserify-preprocessor');

module.exports = (on) => {
  const options = {
    ...browserify.defaultOptions,
    typescript: require.resolve('typescript'),
  };

  options.browserifyOptions.plugin.unshift([
    'tsify',
    { project: 'cypress/tsconfig.json' },
  ]);

  on('file:preprocessor', browserify());
  on('file:preprocessor', cucumber(options));
  on('before:browser:launch', (browser, launchOptions) => {
    if (browser.name === 'chrome') {
      launchOptions.args.push('--disable-dev-shm-usage');
    }
    return launchOptions;
  });
};

const xlsx = require('node-xlsx').default;
const fs = require('fs'); // for file
const path = require('path'); // for file path

module.exports = (on, config) => {
  // `on` is used to hook into various events Cypress emits
  on('task', {
    parseXlsx({ filePath }) {
      return new Promise((resolve, reject) => {
        try {
          const jsonData = xlsx.parse(fs.readFileSync(filePath));
          resolve(jsonData);
        } catch (e) {
          reject(e);
        }
      });
    },
  });
};

module.exports = (on, config) => {
  on('task', {
    readXlsx: readXlsx.read,
  });
};
