// Cypress scrolls an element into view before clicking. The scrolling algorithm puts the element
// at the top of the page. This causes issues if the top of the page is covered by a floating header.
// For example, such scrolling strategy results in inability to click elements.
// The problem has been reported in Cypress GH, but no resolution has been provided so far:
// - https://github.com/cypress-io/cypress/issues/871
// - https://github.com/cypress-io/cypress/issues/2302
//
// For now, the following workaround is recommended:
// https://github.com/cypress-io/cypress/issues/871#issuecomment-509392310
export const overrideSrollingStrategy = () => {
  Cypress.on('scrolled', ($el) => {
    $el.get(0).scrollIntoView({
      block: 'center',
      inline: 'center',
    });
  });
};
