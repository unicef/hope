/* eslint-disable func-names */
const { clear } = Cypress.LocalStorage;

// Workaround allowing to whitelist localStorage entries,
// so that specific items wouldn't be cleared between tests.
// Ref. to https://github.com/cypress-io/cypress/issues/461.
(function (root: Window) {
  Cypress.LocalStorage.clear = function (clearKeys) {
    const getFilteredKeys = () => {
      const currentKeys = Object.keys(root.localStorage || {});
      const { role } = Cypress.env('currentUser') || {};
      const whitelist = Cypress._.get(
        Cypress.env(role),
        'whitelist.localstorage',
        [],
      );

      return currentKeys.filter((key) => whitelist.indexOf(key) === -1);
    };

    return clear.apply(root, [
      (clearKeys || []).length > 0 ? clearKeys : getFilteredKeys(),
    ]);
  };
})(window);
