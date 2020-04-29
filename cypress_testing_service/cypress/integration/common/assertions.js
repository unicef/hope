import { Given, Then } from 'cypress-cucumber-preprocessor/steps';


// assert path within the current business area
Given('I get taken to {word} in current business area', (path_to_check_for) => {
    cy.location('pathname').then((current_path) => {
        const business_area_slug = current_path.split('/')[1]
        cy.location('pathname').should('eq', '/'.concat(business_area_slug, path_to_check_for))
    })
})
