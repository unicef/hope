/* eslint-disable func-names */
const { clear } = Cypress.LocalStorage;

// Workaround allowing to whitelist localStorage entries,
// so that specific items wouldn't be cleared between tests.
// Ref. to https://github.com/cypress-io/cypress/issues/461.
Cypress.LocalStorage.clear = (keys) => {
  const getWhitelistedKeys = () => {
    const { role } = Cypress.env('currentUser') || {};
    const whitelist = Cypress._.get(
      Cypress.env(role),
      'whitelist.localstorage',
      [],
    );

    return Object.keys(localStorage || {}).filter(
      (key) => whitelist.indexOf(key) === -1,
    );
  };

  return clear.apply((keys || []).length > 0 ? keys : getWhitelistedKeys());
};
