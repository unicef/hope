import { When } from 'cypress-cucumber-preprocessor/steps';

// figures our business area slug and appends pathname to it
When('I visit {word} in current business area', (newPath) => {
  cy.location('pathname').then((currentPath) => {
    const businessAreaSlug = currentPath.split('/')[1];
    cy.visit('/'.concat(businessAreaSlug, newPath));
  });
});

// Simply visit an absolute url/path
When('I visit {word}', (path) => {
  cy.visit(path);
});

// Find item in navigation and click it
When('I click {word} in navigation', (navItemLabel) => {
  cy.get('.MuiDrawer-root').contains(navItemLabel).click();
});

