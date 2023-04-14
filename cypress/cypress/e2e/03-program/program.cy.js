/// <reference types="cypress" />

context("Program", () => {
  beforeEach(() => {
    cy.adminLogin()
    cy.visit("/");
    cy.get("span").contains("Programme Management").click();
    cy.get("h5").contains("Programme Management");
  
  });
  it("Can visit the Programs page and create a program", () => {
    
    cy.get('[data-cy="button-new-program"]').click({ force: true });
    cy.get("h6").contains("Set-up a new Programme");
    cy.uniqueSeed().then((seed) => {
      const programName = `test program ${seed}`;
      cy.get('[data-cy="input-programme-name"]').type(programName);
      cy.get('[data-cy="input-cash-assist-scope"]').first().click();
      cy.get('[data-cy="select-option-Unicef"]').click();
      cy.get('[data-cy="input-sector"]').first().click();
      cy.get('[data-cy="select-option-Multi Purpose"]').click();
      cy.get('[data-cy="input-start-date"]').click().type("2023-04-10");
      cy.get('[data-cy="input-end-date"]').click().type("2023-04-30");
      cy.get('[data-cy="input-description"]')
        .first()
        .click()
        .type("test description");
      cy.get('[data-cy="input-budget"]')
        .first()
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}9999");
      cy.get('[data-cy="input-admin-area"]').click().type("Some Admin Area");
      cy.get('[data-cy="input-population-goal"]')
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}4000");
      cy.get('[data-cy="button-save"]').click({ force: true });
cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
      cy.get("h6").contains("Programme Details");
      cy.get('[data-cy="button-activate-program"]').click({ force: true });
      cy.get('[data-cy="button-activate-program-modal"]').click({force: true});
      cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
     cy.get('[data-cy="status-container"]').should('contain',"ACTIVE");
    });
  });

  it("Edit Program", () => {
    cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({force:true})
   cy.get('[data-value="ACTIVE"]').click({force:true})
  
  cy.get('tbody tr').eq(0).each(($tablerows) => {
    cy.wrap($tablerows).within(() => {
      cy.get('td').eq(1).each(($data) => {
        if ($data.text() == 'ACTIVE')
       cy.contains('ACTIVE').click({ force: true })
      })
    })
  })
  cy.contains('EDIT PROGRAMME').click({ force: true })
  cy.get('[data-cy="input-programme-name"]').clear().type('Edited Name');
  cy.get('[data-cy="input-cash-assist-scope"]').first().click();
  cy.get('[data-cy="select-option-Unicef"]').click();
  cy.get('[data-cy="input-sector"]').first().click();
  cy.get('[data-cy="select-option-Multi Purpose"]').click();
  cy.get('[data-cy="input-start-date"]').click().type("2023-05-1");
  cy.get('[data-cy="input-end-date"]').click().type("2023-05-30");
  cy.get('[data-cy="input-description"]')
    .first().clear().type("Edit Test description");
  cy.get('[data-cy="input-budget"]')
    .first()
    .click()
    .type("{backspace}{backspace}{backspace}{backspace}8888");
  cy.get('[data-cy="input-admin-area"]').clear().type("Some Admin Area");
  cy.get('[data-cy="input-population-goal"]')
    .click()
    .type("{backspace}{backspace}{backspace}{backspace}2000");
  cy.get('[data-cy="button-save"]').click({ force: true });

})

it("Finish Program", () => {
  cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({force:true})
 cy.get('[data-value="ACTIVE"]').click({force:true})

cy.get('tbody tr').eq(0).each(($tablerows) => {
  cy.wrap($tablerows).within(() => {
    cy.get('td').eq(1).each(($data) => {
      if ($data.text() == 'ACTIVE')
     cy.contains('ACTIVE').click({ force: true })
    })
  })
})
cy.contains('Finish Programme').click({ force: true })
cy.get('[data-cy="button-finish-program"]').eq(1).click({force: true})
cy.get('[data-cy="status-container"]').should('contain',"FINISHED");
})

it("Reactivate Program", () => {
  cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({force:true})
 cy.get('[data-value="FINISHED"]').click({force:true})
cy.wait(2000)
cy.get('tbody tr').eq(0).each(($tablerows) => {
  cy.wrap($tablerows).within(() => {
    cy.get('td').eq(1).each(($data) => {
      if ($data.text() == 'FINISHED')
     cy.contains('FINISHED').click({ force: true })
    })
  })
})
cy.contains('Reactivate').click({ force: true })
cy.get('.MuiDialogActions-root > .MuiButton-contained').click({force: true})
cy.get('[data-cy="status-container"]').should('contain',"ACTIVE");
})

it("Delete Program", () => {

   cy.get('[data-cy="button-new-program"]').click({ force: true });
    cy.get("h6").contains("Set-up a new Programme");
    cy.uniqueSeed().then((seed) => {
      const programName = `program ${seed}`;
      cy.get('[data-cy="input-programme-name"]').type(programName);
      cy.get('[data-cy="input-cash-assist-scope"]').first().click();
      cy.get('[data-cy="select-option-Unicef"]').click();
      cy.get('[data-cy="input-sector"]').first().click();
      cy.get('[data-cy="select-option-Multi Purpose"]').click();
      cy.get('[data-cy="input-start-date"]').click().type("2023-04-13");
      cy.get('[data-cy="input-end-date"]').click().type("2023-05-20");
      cy.get('[data-cy="input-description"]')
        .first()
        .click()
        .type("Draft description");
      cy.get('[data-cy="input-budget"]')
        .first()
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}3533");
      cy.get('[data-cy="input-admin-area"]').click().type("Admin");
      cy.get('[data-cy="input-population-goal"]')
        .click()
        .type("{backspace}{backspace}{backspace}{backspace}3000");
      cy.get('[data-cy="button-save"]').click({ force: true });
      
      cy.wait(2000);
      cy.get('[data-cy="status-container"]').should('contain',"DRAFT");
      cy.get('div.sc-kEYyzF').click({ force: true })
    })
cy.get('[data-mui-test="SelectDisplay"]').eq(0).click({force:true})
 cy.get('[data-value="DRAFT"]').click({force:true})
 cy.wait(2000)
cy.get('tbody tr').eq(0).each(($tablerows) => {
  cy.wrap($tablerows).within(() => {
    cy.get('td').eq(1).each(($data) => {
      if ($data.text() == 'DRAFT')
     cy.contains('DRAFT').click({ force: true })
    })
  })
})
cy.get('[data-cy="button-remove-program"]').click({force: true})
cy.get('[data-cy="button-remove-program"]').eq(1).click({force: true})


})
})
