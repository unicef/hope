import { When, Then, Given } from 'cypress-cucumber-preprocessor/steps';

Given('I am authenticated', () => {
  cy.visit('/api/unicorn/');
  cy.get('input[name="username"]').type(Cypress.env('daUsername'));
  cy.get('input[name="password"]').type(Cypress.env('daPassword'));
  cy.get('input').contains('Log in').click();
});
const clearCache = () => {
  cy.get('[data-cy="menu-user-profile"]').click();
  cy.get('[data-cy="menu-item-clear-cache"]').click();
  // hack to let the page reload
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
};

When('I visit the main dashboard', () => {
  cy.visit('/');
  clearCache();
});

Then('I should see the side panel with Grievance option', () => {
  cy.get('span').contains('Grievance').click({ force: true });
  cy.get('span').contains('Grievance Tickets');
});

When('I click on Grievance Tickets option', () => {
  cy.get('span').contains('Grievance Tickets').click({ force: true });
});

Then('I should see the Grievance page', () => {
  cy.get('h5').contains('Grievance Tickets');
});

When('I click the New Ticket button', () => {
  cy.get('[data-cy="button-new-ticket"').click({ force: true });
});

Then('I should see the New Ticket page', () => {
  cy.get('h5').contains('New Ticket');
});

When('I fill in the form and save', () => {
  cy.get('[data-cy="select-category"]').click();
  cy.contains('Referral').click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="household-table-row"]').eq(0).click();
  cy.contains('LOOK UP INDIVIDUAL').click({ force: true });
  cy.get('[data-cy="individual-table-row"]').eq(0).click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-maleChildrenCount"]').click();
  cy.get('[data-cy="input-childrenDisabledCount"]').click();
  cy.get('[data-cy="input-village"]').click();
  cy.get('[data-cy="input-countryOrigin"]').click();
  cy.get('[data-cy="input-headOfHousehold"]').click();
  cy.get('[data-cy="input-consent"]').click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-description"]').click().type('description');
  cy.get('[data-cy="button-submit"]').click({ force: true });
});

When('I fill in the form without individual and household and save', () => {
  cy.get('[data-cy="select-category"]').click();
  cy.contains('Referral').click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-consent"]').click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-description"]').click().type('description');
  cy.get('[data-cy="button-submit"]').click({ force: true });
});

When('I fill in the form individual data change and save', () => {
  cy.get('[data-cy="select-category"]').click();
  cy.contains('Data Change').click();
  cy.get('[data-cy="select-issueType"]').click();
  cy.contains('Individual Data Update').click({ force: true });
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="household-table-row"]').eq(0).click();
  cy.contains('LOOK UP INDIVIDUAL').click({ force: true });
  cy.get('[data-cy="individual-table-row"]').eq(0).click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-fullName"]').click();
  cy.get('[data-cy="input-birthDate"]').click();
  cy.get('[data-cy="input-sex"]').click();
  cy.get('[data-cy="input-phoneNo"]').click();
  cy.get('[data-cy="input-relationship"]').click();
  cy.get('[data-cy="input-consent"]').click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-description"]')
    .click({ force: true })
    .type('description');
  cy.get('[data-cy="select-individualDataUpdateFields[0].fieldName"]').click({
    force: true,
  });
  cy.contains('Family name').click({ force: true });
  cy.get('[data-cy="input-individualDataUpdateFields[0].fieldValue"]')
    .click({ force: true })
    .type('Kovalsky');
  cy.get('[data-cy="button-add-new-field"]').click();
  cy.get('[data-cy="select-individualDataUpdateFields[1].fieldName"]').click({
    force: true,
  });
  cy.contains('Marital status').click({ force: true });
  cy.get('[data-cy="select-individualDataUpdateFields[1].fieldValue"]').click({
    force: true,
  });
  cy.contains('Widowed').click({ force: true });
  cy.get('[data-cy="button-submit"]').click({ force: true });

  cy.get('[data-cy="button-submit"]').click({ force: true });
});

When('I fill in the form household data change and save', () => {
  cy.get('[data-cy="select-category"]').click();
  cy.contains('Data Change').click();
  cy.get('[data-cy="select-issueType"]').click();
  cy.contains('Household Data Update').click({ force: true });
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="household-table-row"]').eq(0).click();
  cy.contains('LOOK UP INDIVIDUAL').click({ force: true });
  cy.get('[data-cy="individual-table-row"]').eq(0).click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-maleChildrenCount"]').click();
  cy.get('[data-cy="input-femaleChildrenCount"]').click();
  cy.get('[data-cy="input-childrenDisabledCount"]').click();
  cy.get('[data-cy="input-headOfHousehold"]').click();
  cy.get('[data-cy="input-countryOrigin"]').click();
  cy.get('[data-cy="input-consent"]').click();
  cy.get('[data-cy="button-submit"]').click({ force: true });
  cy.get('[data-cy="input-description"]')
    .click({ force: true })
    .type('description');
  cy.get('[data-cy="select-householdDataUpdateFields[0].fieldName"]').click({
    force: true,
  });
  cy.contains('Country of registration').click({ force: true });
  cy.get('[data-cy="select-householdDataUpdateFields[0].fieldValue"]').click({
    force: true,
  });
  cy.contains('Belarus').click({ force: true });
  cy.get('[data-cy="button-add-new-field"]').click();
  cy.get('[data-cy="select-householdDataUpdateFields[1].fieldName"]').click({
    force: true,
  });
  cy.contains('Address').click({ force: true });
  cy.get('[data-cy="input-householdDataUpdateFields[1].fieldValue"]')
    .click({
      force: true,
    })
    .type('Some Address');
  cy.get('[data-cy="button-submit"]').click({ force: true });

  cy.get('[data-cy="button-submit"]').click({ force: true });
});

Then('I should see the Grievance details page', () => {
  cy.contains('Ticket ID:');
});

Then(
  'I should see the Requested Individual Data Change component with correct values',
  () => {
    cy.contains('Requested Data Change');
    cy.contains('Kovalsky');
    cy.contains('Widowed');
  },
);

Then(
  'I should see the Requested Household Data Change component with correct values',
  () => {
    cy.contains('Requested Data Change');
    cy.contains('Belarus');
    cy.contains('Some Address');
  },
);

When('I change states and approve data', () => {
  cy.get('[data-cy="button-set-to-in-progress"]').click({ force: true });
  cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('[data-cy="button-send-for-approval"]').click({ force: true });
  cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.get('[type="checkbox"]').eq(0).check({ force: true });
  cy.get('[type="checkbox"]').eq(1).check({ force: true });
  cy.get('[data-cy="button-approve"]').click({ force: true });
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.contains('Close Ticket').click({ force: true });
});

Then('I should see the ticket is closed and changes are approved', () => {
  cy.contains('Closed');
  cy.get('[data-cy="green-tick"]').should('have.length', 2);
});

When('I edit the Grievance and save', () => {
  cy.get('[data-cy="button-edit"]').click({ force: true });
  cy.get('[data-cy="input-comments"]')
    .click({ force: true })
    .type('comments EDITED');
  cy.get('[data-cy="button-submit"]').click({ force: true });
});

Then('I should see the updated Grievance', () => {
  cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
  cy.contains('EDITED');
});
