import { Given } from 'cypress-cucumber-preprocessor/steps';

// assert path within the current business area
Given('I get taken to {word} in current business area', (pathToCheckFor) => {
    cy.location('pathname').then((currentPath) => {
        const businessAreaSlug = currentPath.split('/')[1];
        cy.location('pathname').should('eq', '/'.concat(businessAreaSlug, pathToCheckFor));
    });
});
