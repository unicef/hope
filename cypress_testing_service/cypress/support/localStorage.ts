/* eslint-disable func-names */
const { clear } = Cypress.LocalStorage;

// Workaround allowing to whitelist localStorage entries,
// so that specific items wouldn't be cleared between tests.
// Ref. to https://github.com/cypress-io/cypress/issues/461.
(function (root: Window) {
  Cypress.LocalStorage.clear = function (keys) {
    const updatedKeys =
      (keys || []).length > 0
        ? keys
        : Object.keys(root.localStorage || {}).filter(
          (key) => Cypress.env('whitelist').localStorage.indexOf(key) === -1,
        );

    return clear.apply(root, updatedKeys);
  };
})(window);
