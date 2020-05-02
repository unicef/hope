import { Given } from 'cypress-cucumber-preprocessor/steps';

Given('I login to AD as {word}', (userRole) => {
    cy.log(`Signing in user to A as ${userRole}`);
    cy.loginToAD(
        Cypress.env(userRole).ad_username,
        Cypress.env(userRole).ad_password,
        Cypress.env('loginUrl'),
    );
    // TODO: see if there is a better way to do this?
    Cypress.env('logged_in_user_username', Cypress.env(userRole).ad_username);
    cy.visit(Cypress.env('loginUrl'));
});
