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

let state: any = {
  createdProgram: {},
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
  overrideSrollingStrategy();
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

    cy.getByTestId('select-scope').click();
    cy.getByTestId('select-options-scope')
      .getByTestId('select-option-0')
      .click();

    const startDate = new Date().getDay();
    const endDate = startDate + 1;

    cy.pickDayOfTheMonth(startDate, 'startDate');
    cy.pickDayOfTheMonth(endDate, 'endDate');

    cy.getByTestId('select-sector').click();
    cy.getByTestId('select-options-sector')
      .getByTestId('select-option-0')
      .click();

    state = {
      ...state,
      createdProgram: {
        name: uniqueName,
        startDate,
        endDate,
      },
    };
  });
});

And('the User submits the form', () => {
  cy.getByTestId('dialog-actions-container').getByTestId('button-save').click();
});

Then('the User is redirected to the new Programme details screen', () => {
  cy.getByTestId('main-content').contains('Programme Details');
  const {
    createdProgram: { name },
  } = state;
  cy.getByTestId('main-content').contains(name);

  cy.location('pathname').then((pathname) => {
    const matchGroups = pathname.match(/[^\\/]+$/);
    expect(matchGroups.length).eq(1);

    const id = matchGroups[0];
    const { createdProgram } = state;
    state = {
      ...state,
      createdProgram: { ...createdProgram, id },
    };
  });
});

Then('status of this Programme is {word}', (status) => {
  cy.getByTestId('program-details-container')
    .getByTestId('status-container')
    .contains(status, {
      matchCase: false,
    });
});

Given('the User is viewing an existing Programme', () => {
  cy.fixture<{ name: string }>('program').then(({ name, ...program }) => {
    const uniqueName = `${name} ${uuid()}`;
    const startDate = new Date().toISOString().split('T')[0];
    const endDate = startDate;

    api
      .createProgram({
        ...program,
        name: uniqueName,
        startDate,
        endDate,
      })
      .then((createResponse) => {
        expect(createResponse.status).eq(200);

        const {
          createProgram: { program: createdProgram },
        } = createResponse.body.data;
        const { id } = createdProgram;
        expect(id).not.eq(undefined);

        state = {
          ...state,
          createdProgram,
        };
      });
  });
});

And('the Programme is in {word} state', (status: string) => {
  const {
    createdProgram: { name, id },
  } = state;

  api.updateProgram({ id, status: status.toUpperCase() });
  cy.navigateTo(`/programs/${id}`);
  cy.getByTestId('program-details-container')
    .getByTestId('status-container')
    .contains(status, {
      matchCase: false,
    });

  cy.getByTestId('page-header-container').contains(name);
});

Then('the Programme is soft deleted', () => {
  // TODO checking soft delete state
});

And('the Programme is no longer accessible', () => {
  cy.navigateTo('/programs');
  const {
    createdProgram: { name },
  } = state;
  cy.getByTestId('main-content').contains(name).should('not.be.visible');
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
