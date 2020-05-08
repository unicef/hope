import {
  Before,
  When,
  Then,
  And,
  Given,
} from 'cypress-cucumber-preprocessor/steps';
import { api } from '../../support/api';

const addToProgramIds = (programId: string) => {
  cy.get<string[]>('@programIds').then((programIds) => {
    cy.wrap([...programIds, programId]).as('programIds');
  });
};

Before(() => {
  // to hold list of ids for programs created during program management
  cy.wrap<string[]>([]).as('programIds');
});

after(() => {
  // remove programs created during test suite run
  cy.get<string[]>('@programIds').then((programIds) => {
    programIds.reduce(async (previousRequest, programId) => {
      await previousRequest;
      return new Cypress.Promise((resolve) => {
        api.deleteProgram(programId).then(() => resolve());
      });
    }, Cypress.Promise.resolve());
  });
});

When('User starts creating New Programme', () => {
  cy.navigateTo('/programs');
  cy.getByTestId('main-content').contains('Programme Management');
  cy.getByTestId('programs-page-container')
    .children('a')
    .should('have.length.gte', 0);
  cy.getByTestId('main-content').scrollTo('top');
  // TODO: check why its not able to scroll properly and hence we're using force:true for now
  cy.getByTestId('btn-new-programme').click({ force: true });
});

Then('the New Programme form is shown', () => {
  cy.getByTestId('dialog-setup-new-programme').should('be.visible');
});

When('the User completes all required fields on the form', () => {
  cy.fixture('program').then((program) => {
    const { name } = program;

    cy.getByTestId('input-name').type(name);

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
});

And('the User clicks the {word} button', (action) => {
  cy.getByTestId('dialog-actions-container').contains(action).click();
});

Then('the User is redirected to the new Programme Details screen', () => {
  cy.getByTestId('main-content').contains('Programme Details');
  cy.fixture('program').then(({ name }) => {
    cy.getByTestId('main-content').contains(name);
  });

  cy.location('pathname').then((pathname) => {
    // get program id from url pathname
    const matchGroups = pathname.match(/[^\\/]+$/);
    expect(matchGroups.length).eq(1);

    const programId = matchGroups[0];
    addToProgramIds(programId);
  });
});

Then('status of this Programme is {word}', (status) => {
  cy.getByTestId('program-details-container').contains(status, {
    matchCase: false,
  });
});

Given(
  'the User is viewing existing Programme in {word} state',
  (status: string) => {
    const today = new Date().toISOString().split('T')[0];

    cy.fixture('program').then((program) => {
      const { name } = program;

      api
        .createProgram({ ...program, startDate: today, endDate: today })
        .then((response) => {
          expect(response.status).eq(200);

          const {
            createProgram: {
              program: { id, status: receivedStatus },
            },
          } = response.body.data;

          expect(id).not.eq(undefined);
          expect(receivedStatus).eq(status.toUpperCase());

          cy.navigateTo(`/programs/${id}`);
          cy.getByTestId('main-content').contains(name);

          // to remove created program in 'After'
          addToProgramIds(id);
        });
    });
  },
);

When('the User removes the Programme', () => {
  cy.contains('remove', { matchCase: false }).click();

  cy.get('.MuiDialogActions-root').within(() => {
    cy.contains('remove', { matchCase: false }).click();
  });

  cy.contains('programme removed', { matchCase: false });
});

Then('the Programme is soft deleted', () => {
  // TODO checking soft delete state
});

And('the Programme is no longer accessible', () => {
  cy.navigateTo('/programs');
  cy.fixture('program').then(({ name }) => {
    cy.getByTestId('main-content').contains(name).should('not.be.visible');
  });
});

When('the User activates the Programme', () => {
  const action = 'activate';

  cy.get('[data-cy^=program-container]')
    .contains(action, { matchCase: false })
    .click();
  cy.get('.MuiDialogActions-root').within(() => {
    cy.contains(action, { matchCase: false }).click();
  });

  cy.contains('programme activated', { matchCase: false });
});
