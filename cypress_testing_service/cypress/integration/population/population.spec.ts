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

  // TODO using force b/c filter is covered by some other element in the UI, investigate
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
  cy.getByTestId('population-household-details-container')
    .find('table tbody tr')
    .should('have.length.greaterThan', 1);

  cy.get('@searchQuery').then((searchQuery) => {
    cy.getByTestId('population-household-details-container')
      .find('table tbody tr')
      .should(($row) => {
        expect($row.text()).contain(searchQuery);
      });
  });
});

When('the user makes at least one selection of filters available', () => {
  const filterQuery = 'refugee';
  cy.wrap(filterQuery).as('filterQuery');

  cy.getByTestId('main-content').scrollTo('top');

  // TODO using force b/c filter is covered by some other element in the UI, investigate
  cy.getByTestId('population-household-filters-residence-status').click({
    force: true,
  });

  // TODO using force b/c filter is covered by some other element in the UI, investigate
  cy.getByTestId('population-household-filters-residence-status-options')
    .find('ul')
    .contains(filterQuery, { matchCase: false })
    .click({ force: true });

  cy.getByTestId('population-household-details-container')
    .getByTestId('loading-container')
    .as('loadingContainer');
});

Then(
  'a list of the Housholds the criteria selected in the filters is shown',
  () => {
    cy.getByTestId('population-household-details-container')
      .find('table tbody tr')
      .should('have.length.greaterThan', 1);

    cy.get<string>('@filterQuery').then((filterQuery) => {
      cy.getByTestId('population-household-details-container')
        .find('table tbody tr')
        .should(($row) => {
          expect($row.text().toLowerCase()).contain(filterQuery.toLowerCase());
        });
    });
  },
);
