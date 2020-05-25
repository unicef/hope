const { clear } = Cypress.LocalStorage;

// manually clear the storage before session
localStorage.clear();

// Workaround allowing to whitelist localStorage entries,
// so that specific items wouldn't be cleared between tests.
// Ref. to https://github.com/cypress-io/cypress/issues/461.
Cypress.LocalStorage.clear = (keys, ...rest) => {
  const updatedKeys =
    keys && keys.length > 0
      ? keys
      : localStorage && localStorage.length > 0 &&
        Object.keys(localStorage).filter(
          (key) => Cypress.env('whitelist').localStorage.indexOf(key) === -1,
        );

  return clear.apply(this, updatedKeys, ...rest);
};
