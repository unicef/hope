import { When, Then, And } from 'cypress-cucumber-preprocessor/steps';

const removeProgramme = () => {
  cy.contains('remove', { matchCase: false }).click();

  cy.get('.MuiDialogActions-root').within(() => {
    cy.contains('remove', { matchCase: false }).click();
  });

  cy.contains('programme removed', { matchCase: false });
};

after(() => {
  cy.get('@programUrl').then((programUrl) => {
    cy.navigateTo(`${programUrl}`);
    removeProgramme();
  });
});

When('User starts creating New Programme', () => {
  cy.navigateTo('/programs');

  cy.getByTestId('main-content').contains('Programme Management');
  cy.getByTestId('btn-new-programme').click();
});

Then('the New Programme form is shown', () => {
  cy.getByTestId('dialog-setup-new-programme').should('be.visible');
});

When('the User completes all required fields on the form', () => {
  cy.getByTestId('input-name').type('John Doe');

  cy.getByTestId('select-field-collapsed-scope').click();
  cy.getByTestId('select-field-options-scope').within(() => {
    cy.contains('Full').click();
  });

  const today = new Date().getDay();
  cy.pickDayOfTheMonth(today, 'startDate');
  cy.pickDayOfTheMonth(today + 1, 'endDate');

  cy.getByTestId('select-field-collapsed-sector').click();
  cy.getByTestId('select-field-options-sector').contains('Education').click();
});

And('the User clicks the {word} button', (action) => {
  cy.getByTestId('dialog-actions-container').contains(action).click();
});

Then('the User is redirected to the new Programme Details screen', () => {
  cy.getByTestId('main-content').contains('Programme Details');

  cy.location('pathname').then((pathname) => {
    const matchGroups = pathname.match(/\/programs\/[^\\/]+$/);
    expect(matchGroups.length).eq(1);

    const programUrl = matchGroups[0];
    cy.wrap(programUrl).as('programUrl');
  });
});

Then('status of this Progrmame is Draft', () => {
  cy.getByTestId('main-content').contains('draft', { matchCase: false });
});

