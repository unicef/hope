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

const expectStatusWithin = <E>(
  chainable: Cypress.Chainable<JQuery<E>>,
  status: string,
) => {
  return chainable.within(() => {
    cy.getByTestId('status-container').contains(status, {
      matchCase: false,
    });
  });
};

const executeProgramAction = (action) => {
  cy.getByTestId('page-header-container')
    .contains(action, { matchCase: false })
    .click();
  cy.get('.MuiDialogActions-root').within(() => {
    cy.contains(action, { matchCase: false }).click();
  });

  // TODO: data-cy for confirmation modal
  cy.contains(`programme ${action}`, { matchCase: false });
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
  // TODO: move to given
  cy.navigateTo('/programs');
  cy.getByTestId('main-content').contains('Programme Management');
  cy.getByTestId('programs-page-container')
    .children('a')
    .should('have.length.gte', 0);
  cy.getByTestId('main-content').scrollTo('top');
  // TODO: check why its not able to scroll properly, using { force: true } for now
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

And('the User submits the form', () => {
  cy.getByTestId('dialog-actions-container')
    .contains('save', { matchCase: false })
    .click();
});

Then('the User is redirected to the new Programme details screen', () => {
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
  expectStatusWithin(cy.getByTestId('program-details-container'), status);
});

Given(
  'the User is viewing existing Programme in {word} state',
  (status: string) => {
    const completeApiRequests = (programId: string) => {
      // to remove created program in tests tear down
      addToProgramIds(programId);
      cy.navigateTo(`/programs/${programId}`);
      cy.getByTestId('program-details-container').as('programDetails');
    };

    cy.fixture('program').then((program) => {
      const { name } = program;
      const today = new Date().toISOString().split('T')[0];

      api
        .createProgram({ ...program, startDate: today, endDate: today })
        .then((response) => {
          expect(response.status).eq(200);

          const {
            createProgram: {
              program: { id },
            },
          } = response.body.data;

          expect(id).not.eq(undefined);

          if (status.toLowerCase() === 'active') {
            // update program status, if needed
            api.updateProgram({ id, status }).then(() => {
              completeApiRequests(id);
            });
          } else {
            completeApiRequests(id);
          }
        });

      // verify it's shown in the UI
      expectStatusWithin(cy.get('@programDetails'), status);
      cy.getByTestId('page-header-container').contains(name);
    });
  },
);

Then('the Programme is soft deleted', () => {
  // TODO checking soft delete state
});

And('the Programme is no longer accessible', () => {
  cy.navigateTo('/programs');
  cy.fixture('program').then(({ name }) => {
    cy.getByTestId('main-content').contains(name).should('not.be.visible');
  });
});

When('the User removes the Programme', () => {
  executeProgramAction('remove');
});

When('the User activates the Programme', () => {
  executeProgramAction('activate');
});

When('the User finishes the Programme', () => {
  executeProgramAction('finish');
});
