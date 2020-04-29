import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';


Then('I should get redirected to login', () => {
    cy.location('pathname').should('eq', '/login')
    cy.get('a').contains('Sign in')
})

Then('I should see the Dashboard', () => {
    cy.get('.MuiList-root').contains('Dashboard')
})

When('I make a request to GraphQL endpoint', () => {
    cy.request('POST', 'api/graphql').as('graphQLRequest')
})

Then('I get a 200 response', () => {
    cy.wait('@graphQLRequest').then((response) => {
        expect(response.status).to.eq(200)
    })
})
