/* eslint-disable func-names */
const { clear } = Cypress.LocalStorage;

// Workaround allowing to whitelist localStorage entries,
// so that specific items wouldn't be cleared between tests.
// Ref. to https://github.com/cypress-io/cypress/issues/461.
(function (root: Window) {
  Cypress.LocalStorage.clear = function (keys) {
    const getFilteredKeys = () => {
      const entries = Object.keys(root.localStorage || {});
      const { role } = Cypress.env('currentUser') || {};
      const whitelist = Cypress._.get(
        Cypress.env(role),
        'whitelist.localstorage',
        [],
      );

      if (!whitelist.length) {
        return entries;
      }

      return entries.filter((key) => whitelist.indexOf(key) === -1);
    };

    const updatedKeys = (keys || []).length > 0 ? keys : getFilteredKeys();

    return clear.apply(root, [...updatedKeys]);
  };
})(window);
