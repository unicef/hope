import { When } from 'cypress-cucumber-preprocessor/steps';

// figures our business area slug and appends pathname to it
When('I visit {word} in current business area', (newPath) => {
  cy.navigateTo(newPath);
});

// Simply visit an absolute url/path
When('I visit {word}', (path) => {
  cy.visit(path);
});

// Find item in navigation and click it
When('I click {word} in navigation', (navItemLabel) => {
  cy.getByTestId('side-nav').contains(navItemLabel).click();
});

