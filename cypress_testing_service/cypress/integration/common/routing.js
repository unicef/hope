import { Given, Then } from 'cypress-cucumber-preprocessor/steps';


// figures our business area slug and appends pathname to it
Given('I visit {word} in current business area', (new_path) => {
    cy.location('pathname').then((current_path) => {
        const business_area_slug = current_path.split('/')[1]
        cy.visit('/'.concat(business_area_slug,new_path))
    })
})

// Simply visit an absolute url/path
Given('I visit {word}', (path) => {
    cy.visit(path)
})

// Find item in navigation and click it
Given('I click {word} in navigation', (nav_item_label) => {
    cy.get('.MuiDrawer-root').contains(nav_item_label).click()
})
