import { Given, Then } from 'cypress-cucumber-preprocessor/steps';


// Detect a string on the page
Given('I see {string} on the page', (words) => {
    cy.contains(words)
})
