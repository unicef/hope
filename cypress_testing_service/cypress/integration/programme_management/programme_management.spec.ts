import { Before, After, When, Then, And, Given } from 'cypress-cucumber-preprocessor/steps';
import { api } from '../../support/api';

const removeProgramme = () => {
  cy.contains('remove', { matchCase: false }).click();

  cy.get('.MuiDialogActions-root').within(() => {
    cy.contains('remove', { matchCase: false }).click();
  });

  cy.contains('programme removed', { matchCase: false });
};

Before({ tags: '@createProgramme' }, () => {
  cy.wrap(undefined).as('programUrl');
});

After({ tags: '@createProgramme' }, () => {
  cy.get('@programUrl').then((programUrl) => {
    cy.navigateTo(`${programUrl}`);
    removeProgramme();
  });
});

// TODO needed?
After({ tags: '@removeProgramme' }, () => {
  cy.getBusinessAreaSlug().then((businessAreaSlug) => {
    api.getAllPrograms(businessAreaSlug).then((response) => {
      const {
        body: {
          data: {
            allPrograms: { edges },
          },
        },
      } = response;

      edges.reduce(async (previousRequest, { node: { id } }) => {
        await previousRequest;
        return new Cypress.Promise((resolve) => {
          api.deleteProgram(id).then(() => resolve());
        });
      }, Cypress.Promise.resolve());
    });
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
        });
    });
  },
);

When('the User takes action to remove Programme', () => {
  removeProgramme();
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
