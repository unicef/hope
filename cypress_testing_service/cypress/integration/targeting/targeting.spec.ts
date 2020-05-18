import {
  Given,
  When,
  Then,
  And,
  Before,
} from 'cypress-cucumber-preprocessor/steps';
import { uuid } from 'uuidv4';
import { api } from '../../support/api';
import { overrideSrollingStrategy } from '../../support/utils';

const createTargetPopulation = () => {
  cy.navigateTo('/target-population');

  cy.getBusinessAreaSlug().then((businessAreaSlug) => {
    cy.fixture('targetPopulation').then((targetPopulation) => {
      const targetPopulationName = `${targetPopulation.name} ${uuid()}`;
      api
        .createTargetPopulation({
          ...targetPopulation,
          businessAreaSlug,
          name: targetPopulationName,
        })
        .then((response) => {
          expect(response.status).eq(200);

          const {
            data: {
              createTargetPopulation: {
                targetPopulation: createdTargetPopulation,
              },
            },
          } = response.body;

          cy.wrap(createdTargetPopulation).as('targetPopulation');
        });
    });
  });
};

Before(() => {
  overrideSrollingStrategy();
});

Given('the User is viewing the Targeting List screen', () => {
  cy.navigateTo('/target-population');

  cy.getByTestId('page-header-container').contains('targeting', {
    matchCase: false,
  });
});

When('the User starts creating new Target Population', () => {
  cy.getByTestId('button-target-population-create-new')
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
  cy.getByTestId('button-target-population-add-criteria').click();

  cy.getByTestId('autocomplete-target-criteria')
    .click()
    // To simplify, pick residence status as one of the guaranteed core fields.
    // Ref. to backend/hct_mis_api/apps/core/core_fields_attributes.py for more details.
    .type('Residence status');

  cy.getByTestId('autocomplete-target-criteria-options')
    .find('ul li')
    .first()
    .then(($el) => {
      cy.wrap($el.text()).as('targetCriteriaQuestion');
      $el.click();
    });

  cy.getByTestId('autocomplete-target-criteria-values').click();

  cy.getByTestId('select-options-container')
    .getByTestId('select-option-0')
    .then(($el) => {
      cy.wrap($el.text()).as('targetCriteriaAnswer');
      $el.click();
    });
});

And('the User completes creating new Target Population', () => {
  cy.getByTestId('dialog-actions-container')
    .getByTestId('button-target-population-add-criteria')
    .click();

  cy.getByTestId('button-target-population-create').click();
  cy.getByTestId('button-target-population-create').should('not.be.visible');
});

Then(
  'the User will be directed to the Programme Population details screen',
  () => {
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

And(
  'the Status of the Programme Population will be set to {word}',
  (status) => {
    cy.getByTestId('page-header-container')
      .getByTestId('status-container')
      .contains(status, { matchCase: false });
  },
);

Given('the User is viewing existing Target Population in Open state', () => {
  createTargetPopulation();
  cy.get<{ id: string }>('@targetPopulation').then(({ id }) => {
    cy.navigateTo(`/target-population/${id}`);
    cy.getByTestId('criteria-container').then(($el) => {
      cy.wrap($el.text()).as('targetPopulationCriteria');
    });
  });
});

When('the User closes the Programme Population', () => {
  cy.getByTestId('button-target-population-close').click();
});

Then(
  'the confirmation dialog for closing Programme Population is shown',
  () => {
    cy.getByTestId('dialog-root').contains('close programme population', {
      matchCase: false,
    });

    cy.getByTestId('dialog-root').contains('are you sure you want to approve', {
      matchCase: false,
    });
  },
);

And('the User is asked to provide associated Program', () => {
  cy.getByTestId('dialog-root').contains('please select a programme', {
    matchCase: false,
  });
});

When('the User selects a Programme to associate with', () => {
  cy.getByTestId('select-program').click();

  cy.getByTestId('select-options-container')
    .getByTestId('select-option-0')
    .click();
});

And('the User confirms to close the Programme Population', () => {
  cy.getByTestId('dialog-actions-container')
    .getByTestId('button-target-population-close')
    .click();
});

Then('the Programme population becomes Closed', () => {
  cy.getByTestId('status-container').contains('closed', { matchCase: false });
});

And('the User can no longer edit the Programme Population', () => {
  cy.getByTestId('page-header-container')
    .contains('edit')
    .should('not.be.visible');
});

And('the Programme Population details are locked', () => {
  cy.getByTestId('target-population-details-container').contains('close date', {
    matchCase: false,
  });
});

Given('the User is viewing existing Target Population in Closed state', () => {
  createTargetPopulation();
  cy.get<{ id: string }>('@targetPopulation').then(({ id }) => {
    cy.navigateTo(`/target-population/${id}`);

    // perform sequence of UI steps to close target population
    cy.getByTestId('button-target-population-close').click();
    cy.getByTestId('select-program').click();
    cy.getByTestId('select-options-container').getByTestId('select-option-0').click();
    cy.getByTestId('dialog-actions-container')
      .getByTestId('button-target-population-close')
      .click();

    cy.getByTestId('status-container').contains('closed', { matchCase: false });
  });
});

When('the User sends the Target Population to Cash Assist', () => {
  cy.getByTestId('button-target-population-send-to-cash-assist').click();
});

Then('the confirmation dialog for Send to Cash Assist is shown', () => {
  cy.getByTestId('dialog-root').contains('send to cash assist', {
    matchCase: false,
  });

  cy.getByTestId('dialog-root').contains('are you sure you want to', {
    matchCase: false,
  });
});

When('the User confirms sending to Cash Assist', () => {
  cy.getByTestId('dialog-actions-container')
    .getByTestId('button-target-population-send-to-cash-assist')
    .click();
});

Then('the details for the Target Population are sent to Cash Assist', () => {
  cy.getByTestId('page-header-container')
    .getByTestId('status-container')
    .contains('sent', { matchCase: false });
});

When('the User starts duplicating the existing Target Population', () => {
  cy.getByTestId('button-target-population-duplicate').click();
});

Then(
  'the confirmation dialog for duplicating Target Population is shown',
  () => {
    cy.getByTestId('dialog-root').contains('duplicate target population', {
      matchCase: false,
    });
  },
);

When('the User provides a unique name for copy of Target Population', () => {
  cy.fixture<{ name: string }>('targetPopulation').then(({ name }) => {
    const duplicatedTargetPopulationName = `${name} ${uuid()}`;
    cy.getByTestId('dialog-root')
      .getByTestId('input-name')
      .type(duplicatedTargetPopulationName);

    cy.wrap(duplicatedTargetPopulationName).as(
      'duplicatedTargetPopulationName',
    );
  });
});

And('the User confirms to duplicate the Target Population', () => {
  cy.getByTestId('dialog-actions-container')
    .getByTestId('button-target-population-duplicate')
    .click();
});

Then(
  'the User is directed to the duplicated Target Population details screen',
  () => {
    cy.getByTestId('page-header-container').contains('targeting', {
      matchCase: false,
    });
  },
);

And(
  'the duplicated Target Population has title as provided by the User',
  () => {
    cy.get<string>('@duplicatedTargetPopulationName').then(
      (duplicatedTargetPopulationName) => {
        cy.getByTestId('page-header-container').contains(
          duplicatedTargetPopulationName,
        );
      },
    );
  },
);

And(
  'the duplicated Target Population have other details as original Target Population',
  () => {
    cy.get<string>('@targetPopulationCriteria').then(
      (targetPopulationCriteria) => {
        cy.getByTestId('criteria-container').then(($el) => {
          expect($el.text()).eq(targetPopulationCriteria);
        });
      },
    );
  },
);
