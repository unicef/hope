import { Then } from 'cypress-cucumber-preprocessor/steps';

// assert path within the current business area
Then('I get taken to {word} in current business area', (pathToCheckFor) => {
  cy.location('pathname').then((currentPath) => {
    const businessAreaSlug = currentPath.split('/')[1];
    cy.location('pathname').should(
      'eq',
      '/'.concat(businessAreaSlug, pathToCheckFor),
    );
  });
});

Then('I see user profile menu', () => {
  cy.getByTestId('menu-btn-user-profile').should('be.visible');
});
