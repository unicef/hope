/// <reference types="cypress" />

describe('User auth flows', () => {

    context('Before user is logged in', () => {
        it('loads the login screen', () => {
            cy.visit('/')
            cy.location('pathname').should('eq', '/login')
            cy.get('a').contains('Sign in')
        })

        it('redirects to login screen if accessing internal url', () => {
            cy.visit('/afghanistan/')
            cy.location('pathname').should('eq', '/login')
        })
    })

    context('User logs in', () => {

        before(function() {
            cy.log('Signing in user to AD')
            cy.loginToAD(
                Cypress.env('country_admin').ad_username, 
                Cypress.env('country_admin').ad_password, 
                Cypress.env('loginUrl')
            )
            cy.visit(Cypress.env('loginUrl'))
        })
    
        it('shows user navigation with dashboard option in it', function() {
            cy.visit('/')
            cy.get('.MuiList-root').contains('Dashboard')
            // cy.location('pathname').should('eq', '/afghanistan')
        })
    })

})
