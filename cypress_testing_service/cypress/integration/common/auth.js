import { Given } from 'cypress-cucumber-preprocessor/steps';


Given('I login to AD as {word}', (user_role) => {
    cy.log('Signing in user to A as ${user_rule}')
    cy.loginToAD(
        Cypress.env(user_role).ad_username, 
        Cypress.env(user_role).ad_password, 
        Cypress.env('loginUrl')
    )
    cy.visit(Cypress.env('loginUrl'))
})
