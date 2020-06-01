// ***********************************************************
// This support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
// ***********************************************************

import 'cypress-file-upload';
import './commands';
import './chai';
// temp. commented due to issues with removing storage items
// import './localStorage';
import './before';
