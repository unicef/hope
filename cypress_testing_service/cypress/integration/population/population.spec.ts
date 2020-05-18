import { Given, When, Then, Before } from 'cypress-cucumber-preprocessor/steps';
import { overrideSrollingStrategy } from '../../support/utils';

Before(() => {
  overrideSrollingStrategy();
});

Given('the User is viewing the Population Household details screen', () => {
  cy.navigateTo('/population/household');

  cy.getByTestId('page-header-container').contains('households', {
    matchCase: false,
  });

  cy.getByTestId('page-details-container')
    .find('table tbody tr')
    .should('have.length.greaterThan', 1);
});

When('the User enters alphanumeric string in search field', () => {
  cy.get('table thead tr th').each(($header, index) => {
    // TODO: rework to use data-cy to identify specific col
    if ($header.text().toLowerCase().includes('household id')) {
      cy.get('table tbody tr')
        .first()
        .then(($el) => {
          cy.wrap($el.children()[index].textContent).as('searchQuery');
        });
    }
  });

  cy.get<string>('@searchQuery').then((searchQuery) => {
    cy.getByTestId('filters-search').find('input').type(searchQuery);

    cy.getByTestId('page-details-container')
      .getByTestId('loading-container')
      .should('be.visible');
  });
});

Then('a list of the {word} that meet the text in search is shown', () => {
  cy.getByTestId('page-details-container')
    .find('table tbody tr')
    .should('have.length.greaterThan', 1);

  cy.get('@searchQuery').then((searchQuery) => {
    cy.getByTestId('page-details-container')
      .find('table tbody tr')
      .should(($row) => {
        expect($row.text()).contain(searchQuery);
      });
  });
});

When(
  'the user makes at least one selection of filters available for Households',
  () => {
    const filterQuery = 'refugee';
    cy.wrap(filterQuery).as('filterQuery');

    cy.getByTestId('filters-residence-status').click();

    cy.getByTestId('filters-residence-status-options')
      .find('ul')
      .contains(filterQuery, { matchCase: false })
      .click();

    cy.getByTestId('page-details-container')
      .getByTestId('loading-container')
      .should('be.visible');
  },
);

Then(
  'a list of the Housholds the criteria selected in the filters is shown',
  () => {
    cy.getByTestId('page-details-container')
      .find('table tbody tr')
      .should('have.length.greaterThan', 1);

    cy.get<string>('@filterQuery').then((filterQuery) => {
      cy.getByTestId('page-details-container')
        .find('table tbody tr')
        .should(($row) => {
          expect($row.text().toLowerCase()).contain(filterQuery.toLowerCase());
        });
    });
  },
);

Given('the User is viewing the Population Individuals details screen', () => {
  cy.navigateTo('/population/individuals');

  cy.getByTestId('page-header-container').contains('individuals', {
    matchCase: false,
  });

  cy.getByTestId('page-details-container')
    .find('table tbody tr')
    .should('have.length.greaterThan', 1);
});

When(
  'the user makes at least one selection of filters available for Individuals',
  () => {
    const filterQuery = 'male';
    cy.wrap(filterQuery).as('filterQuery');

    cy.getByTestId('filters-sex').click();

    cy.getByTestId('filters-sex-options')
      .find('ul')
      .contains(filterQuery, { matchCase: false })
      .click();

    cy.getByTestId('page-details-container')
      .getByTestId('loading-container')
      .should('be.visible');
  },
);
