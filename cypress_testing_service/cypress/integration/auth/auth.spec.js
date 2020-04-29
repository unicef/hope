import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';


Given('I visit {word}', (path) => {
    cy.visit(path)
})

Then('I should get redirected to login', () => {
    cy.location('pathname').should('eq', '/login')
    cy.get('a').contains('Sign in')
})

Then('I should see the Dashboard', () => {
    cy.get('.MuiList-root').contains('Dashboard')
})
