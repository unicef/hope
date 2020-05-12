import { Given, When, Then, And } from 'cypress-cucumber-preprocessor/steps';
import { uuid } from 'uuidv4';

Given('the User is viewing the Targeting List screen', () => {
  cy.navigateTo('/target-population');

  cy.getByTestId('page-header-container').contains('targeting', {
    matchCase: false,
  });
});

When('the User starts creating new Target Population', () => {
  cy.getByTestId('btn-target-population-create-new')
    .should('be.visible')
    .click();
});

And('the User gives new Target Population a name', () => {
  cy.fixture('targetPopulation').then(({ name }) => {
    const targetPopulationName = `${name} ${uuid()}`;
    cy.getByTestId('main-content')
      .getByTestId('input-name')
      .type(targetPopulationName);

    cy.wrap(targetPopulationName).as('targetPopulationName');
  });
});

And('the User selects at least one Target Criteria', () => {
  cy.getByTestId('btn-target-population-add-criteria').click();

  cy.getByTestId('autocomplete-target-criteria-options').first().click();
  cy.get('.MuiAutocomplete-popper')
    .find('ul li')
    .first()
    .then(($el) => {
      cy.wrap($el.text()).as('targetCriteriaQuestion');
      $el.click();
    });

  cy.getByTestId('autocomplete-target-criteria-values').first().click();
  cy.get('.MuiPopover-root')
    .find('ul li')
    .first()
    .then(($el) => {
      cy.wrap($el.text()).as('targetCriteriaAnswer');
      $el.click();
    });
});

And('the User completes creating new Target Population', () => {
  cy.get('.MuiDialogActions-root')
    .contains('save', { matchCase: false })
    .click();

  cy.getByTestId('btn-target-population-create').click({ force: true });
  cy.getByTestId('btn-target-population-create').should('not.be.visible');
});

Then(
  'the User will be directed to the Programme Population details screen',
  () => {
    cy.getByTestId('main-content').scrollTo('top');

    cy.getByTestId('page-header-container').contains('targeting', {
      matchCase: false,
    });

    cy.get<string>('@targetPopulationName').then((targetPopulationName) => {
      cy.getByTestId('page-header-container').contains(targetPopulationName);
    });

    cy.get<string>('@targetCriteriaQuestion').then((question) => {
      cy.getByTestId('criteria-container').contains(question);
    });

    cy.get<string>('@targetCriteriaAnswer').then((answer) => {
      cy.getByTestId('criteria-container').contains(answer);
    });

    cy.getByTestId('target-population-tabs-0')
      .find('button')
      .first()
      .contains('programme population', { matchCase: false });
  },
);

And('the Status of the Programme Population will be set to {word}', (status) => {
  cy.getByTestId('status-container').contains(status, { matchCase: false });
});
