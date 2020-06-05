import { Then } from 'cypress-cucumber-preprocessor/steps';

// Detect a string on the page
Then('I see {string} on the page', (words) => {
  cy.contains(words);
});
