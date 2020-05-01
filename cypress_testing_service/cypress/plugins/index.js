// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

// https://gist.github.com/csuzw/845b589549b61d3a5fe18e49592e166f

const AzureAdSingleSignOn = require('./azure-ad-sso/plugin').AzureAdSingleSignOn;
const cucumber = require('cypress-cucumber-preprocessor').default;
const browserify = require('@cypress/browserify-preprocessor');

module.exports = (on, config) => {
    const options = browserify.defaultOptions;

    options.browserifyOptions.plugin.unshift([
        'tsify',
        { project: 'cypress/tsconfig.json' },
    ]);

    on('file:preprocessor', cucumber(options));
    on('task', { AzureAdSingleSignOn: AzureAdSingleSignOn });
};
