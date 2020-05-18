import {
  Before,
  When,
  Then,
  And,
  Given,
} from 'cypress-cucumber-preprocessor/steps';
import { uuid } from 'uuidv4';
import { api } from '../../support/api';
import { overrideSrollingStrategy } from '../../support/utils';

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
    .getByTestId(`button-${action}-program`)
    .click();

  cy.getByTestId('dialog-actions-container')
    .getByTestId(`button-${action}-program`)
    .click();

  cy.getByTestId(`snackbar-program-${action}-success`);
};

Before(() => {
  // to hold list of ids for programs created during program management
  cy.wrap<string[]>([]).as('programIds');
  overrideSrollingStrategy();
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

  cy.getByTestId('button-new-program').click();
});

Then('the New Programme form is shown', () => {
  cy.getByTestId('dialog-setup-new-programme').should('be.visible');
});

When('the User completes all required fields on the form', () => {
  cy.fixture<{ name: string }>('program').then(({ name }) => {
    const uniqueName = `${name} ${uuid()}`;

    cy.getByTestId('input-name').type(uniqueName);
    cy.wrap(uniqueName).as('uniqueProgramName');

    cy.getByTestId('select-scope').click();
    cy.getByTestId('select-options-scope')
      .getByTestId('select-option-0')
      .click();

    const today = new Date().getDay();
    cy.pickDayOfTheMonth(today, 'startDate');
    cy.pickDayOfTheMonth(today + 1, 'endDate');

    cy.getByTestId('select-sector').click();
    cy.getByTestId('select-options-sector')
      .getByTestId('select-option-0')
      .click();
  });
});

And('the User submits the form', () => {
  cy.getByTestId('dialog-actions-container').getByTestId('button-save').click();
});

Then('the User is redirected to the new Programme details screen', () => {
  cy.getByTestId('main-content').contains('Programme Details');
  cy.get<string>('@uniqueProgramName').then((name) => {
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
    const completeApiRequests = (program) => {
      const { id } = program;

      // to remove created program in tests tear down
      addToProgramIds(id);

      cy.navigateTo(`/programs/${id}`);
      cy.getByTestId('program-details-container').as('programDetails');
      cy.wrap(program).as('program');
    };

    cy.fixture('program').then((program) => {
      const uniqueName = `${program.name} ${uuid()}`;
      const today = new Date().toISOString().split('T')[0];

      api
        .createProgram({
          ...program,
          name: uniqueName,
          startDate: today,
          endDate: today,
        })
        .then((createResponse) => {
          expect(createResponse.status).eq(200);

          const {
            createProgram: { program: createdProgram },
          } = createResponse.body.data;
          const { id } = createdProgram;
          expect(id).not.eq(undefined);

          if (status.toLowerCase() === 'active') {
            // update program status, if needed
            api.updateProgram({ id, status }).then((updateResponse) => {
              const {
                updateProgram: { program: updatedProgram },
              } = updateResponse.body.data;
              completeApiRequests(updatedProgram);
            });
          } else {
            completeApiRequests(createdProgram);
          }
        });

      // verify it's shown in the UI
      expectStatusWithin(cy.get('@programDetails'), status);
      cy.getByTestId('page-header-container').contains(uniqueName);
    });
  },
);

Then('the Programme is soft deleted', () => {
  // TODO checking soft delete state
});

And('the Programme is no longer accessible', () => {
  cy.navigateTo('/programs');
  cy.get<{ name: string }>('@program').then(({ name }) => {
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
