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

const AzureAdSingleSignOn = require('./azure-ad-sso/plugin').AzureAdSingleSignOn

module.exports = (on, config) => {
    on('task', {AzureAdSingleSignOn:AzureAdSingleSignOn})
}
