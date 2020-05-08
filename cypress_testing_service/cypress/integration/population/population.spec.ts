import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';

Given('the User is viewing the Population Household details screen', () => {
  cy.navigateTo('/population/household');

  cy.getByTestId('page-header-container').contains('Households', {
    matchCase: false,
  });

  cy.getByTestId('population-household-details-container')
    .find('table tbody tr')
    .should('have.length.greaterThan', 1);
});

When('the User enters alphanumeric string in search field', () => {
  const searchQuery = 'Julia';
  cy.wrap(searchQuery).as('searchQuery');

  // TODO using force b/c input is covered by some other element
  cy.getByTestId('population-household-filters-search')
    .find('input')
    .type(searchQuery, {
      force: true,
    });

  cy.getByTestId('population-household-details-container')
    .getByTestId('loading-container')
    .as('loadingContainer');
});

Then('a list of the Housholds that meet the text in search is shown', () => {
  cy.get('@searchQuery').then((searchQuery) => {
    cy.getByTestId('population-household-details-container')
      .find('table tbody tr')
      .should(($row) => {
        expect($row.text()).contain(searchQuery);
      });
  });
});
