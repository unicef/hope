/// <reference types="cypress" />

context("Payment", () => {
  beforeEach(() => {
    cy.initScenario("payment_plan");
    cy.adminLogin();
    cy.visit("/");

  });

  it("Can create a payment plan", () => {
    const downloadsFolder = Cypress.config("downloadsFolder");
    const fileName = id => `payment_plan_payment_list_${id}`;
    const zipFileName = id => `${fileName(id)}.zip`;
    let targetPopulationName = "PaymentPlanTargetPopulation";
    let paymentPlanUnicefId;
    let fspXlsxFilenames;


    createPaymentPlan(targetPopulationName);

    cy.get('[data-cy="page-header-container"]').should('contain',"Payment Plan ID");
    cy.get("h6").should('contain',"Details");

    cy.get("h6").should('contain',"Results");
    cy.get("h6").should('contain',"Payee List");
    cy.get("h6").should('contain',"Activity Log");

    // cy.get('[data-cy="pp-unicef-id"]')
    //   .then($el => {
    //     paymentPlanUnicefId = $el.text();
    //     cy.log(paymentPlanUnicefId)
    //   })
    //   .then(() => {
    //     cy.get("h6").contains("Details");
    //     cy.get("h6").contains("Results");
    //     cy.get("h6").contains("Payee List");
    //     cy.get("h6").contains("Activity Log");
    //   })

      //  cy.get('[data-cy="button-lock-plan"]',{timeout: 10000}).should('be.visible')
      //   cy.get('[data-cy="button-lock-plan"]',{timeout: 10000}).click({ force: true});
      //   cy.get('[data-cy="button-submit"]').click({ force: true});

    //     //Entitlements
        // cy.get("[data-cy=input-entitlement-formula]").should("exist");
        // cy.get("[data-cy=input-entitlement-formula] > .MuiSelect-root").click({
        //   force: true
        // });
        // cy.get('[data-cy="input-entitlement-formula"]').click({ force: true });
        // cy.uniqueSeed().then(seed => {
        //   cy.get("li")
        //     .contains(`Rule-${seed}`)
        //     .click({ force: true });
        // });
        // cy.get('[data-cy="button-apply-steficon"]').click({ force: true });
        // cy.reload();
        // cy.get('[data-cy="total-entitled-quantity-usd"]').should('contain',"USD");

    //     //Set up FSP
        // cy.get('[data-cy="button-set-up-fsp"]').click({ force: true });
        // cy.get('[data-cy="page-header-container"]').contains("Set up FSP", {timeout: 10000});
        // cy.get('[data-cy="select-deliveryMechanisms[0].deliveryMechanism"]').click();
        // cy.get('[data-cy="select-option-Cash"]').click()
 
       // cy.get('[data-cy="select-option-Transfer"]').click();
       // cy.get('[data-cy="button-next-save"]').click({ force: true });
        // cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]');
        // cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]').click();
        // // cy.get('[data-cy="select-option-Test FSP Transfer"]').click();
        // cy.get('[data-cy="button-next-save"]').click({ force: true });
        // cy.contains("Volume by Delivery Mechanism");
        // cy.get("[data-cy='button-lock-plan']").click({ force: true });
        // cy.get("[data-cy='button-submit']").click({ force: true });
        // cy.get("[data-cy='status-container']").contains("FSP LOCKED");

    //     //Acceptance Process
    //     cy.get("[data-cy='button-send-for-approval']").click({ force: true });
    //     cy.wait(1000);
    //     cy.reload(); // this shouldn't be needed but there's some bug here with which reload helps
    //     cy.contains("Acceptance Process");
    //     cy.get("[data-cy='button-approve']").click({ force: true });
    //     cy.get("[data-cy='button-submit']").click({ force: true });
    //     cy.get('[data-cy=""]').contains("IN AUTHORIZATION");
    //     cy.get("[data-cy='button-authorize']").click({ force: true });
    //     cy.get("[data-cy='button-submit']").click({ force: true });
    //     cy.get('[data-cy="status-container"]').contains("IN REVIEW");
    //     cy.get("[data-cy='button-mark-as-released']").click({ force: true });
    //     cy.get("[data-cy='button-submit']").click({ force: true });
    //     cy.get('[data-cy="status-container"]').contains("ACCEPTED");

    //     // //XLSX template - can be used in another spec
    //     // cy.get('[data-cy="button-export-xlsx"]').click({ force: true });
    //     // cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    //     // cy.reload();
    //     // cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    //     // const nameXlsx = xlsxFileName(paymentPlanUnicefId);
    //     // const downloadedFilePathXlsx = `${downloadsFolder}/${nameXlsx}`;
    //     // cy.exec(
    //     //   `node cypress/scripts/fillXlsxEntitlements.js ${downloadedFilePathXlsx}`
    //     //   );
    //     // cy.get('[data-cy="button-download-template"]').click({ force: true });
    //     // const nameTemplate = xlsxFileName(paymentPlanUnicefId);
    //     // const filledFilePathTemplate = `out_${nameTemplate}`;
    //     // cy.get('[data-cy="button-import"]').click({ force: true });
    //     // cy.fixture(filledFilePathTemplate, "base64").then((fileContent) => {
    //     //   cy.get('[data-cy="file-input"]').upload({
    //     //     fileContent,
    //     //     fileName: name,
    //     //     mimeType:
    //     //       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    //     //     encoding: "base64",
    //     //   });
    //     // });
    //     // cy.get('[data-cy="button-import-entitlement"').click({ force: true });
    //     // cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
    //     // cy.reload();
    //     // cy.get("td").should("not.contain", "Missing");

    //     cy.get('[data-cy="button-export-xlsx"]').click({ force: true });
    //     cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
    //     cy.reload();
    //     cy.get('[data-cy="button-download-xlsx"]').click({ force: true });
    //     cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
    //     const nameZip = zipFileName(paymentPlanUnicefId);
    //     const downloadedFilePathZip = `${downloadsFolder}/${nameZip}`;
    //     cy.exec(`unzip ${downloadedFilePathZip} -d ${downloadsFolder}`);
    //     const currentRunFileName = fileName(paymentPlanUnicefId);
    //     cy.exec(
    //       `find ${downloadsFolder} | grep ${currentRunFileName} | grep FSP | sed 's@.*/@@'`
    //     )
    //       .then(result => {
    //         fspXlsxFilenames = result.stdout.split("\n");
    //         expect(fspXlsxFilenames.length).to.eq(1);
    //       })
    //       .then(() => {
    //         //Reconciliation Info
    //         const fspFilename = fspXlsxFilenames[0];
    //         const downloadedFilePath = `${downloadsFolder}/${fspFilename}`;
    //         cy.exec(
    //           `node cypress/scripts/fillXlsxReconciliation.js "${downloadedFilePath}"`
    //         );
    //         const filledFilePath = `out_${fspFilename}`;
    //         cy.log(filledFilePath);
    //         cy.get('[data-cy="button-import"]').click({ force: true });
    //         cy.fixture(filledFilePath, "base64").then(fileContent => {
    //           cy.get('[data-cy="file-input"]').attachFile({
    //             fileContent,
    //             fileName: filledFilePath,
    //             mimeType:
    //               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    //             encoding: "base64"
    //           });
    //         });
    //         cy.get('[data-cy="file-input"').click({ force: true });
    //         // cy.get('[data-cy="imported-file-name"]').should('exist'); // TODO
    //         cy.get('[data-cy="button-import-submit"').click({ force: true });
    //         cy.wait(1000);
    //         cy.get("p").should("not.contain", "Errors");
    //         cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
    //         cy.reload();
    //         cy.get('[data-cy="delivered-quantity-cell"]').each($el => {
    //           cy.wrap($el).should("contain", "AFN");
    //           cy.wrap($el).should("contain", "500");
    //         });
    //         cy.get('[data-cy="status-container"]').contains("FINISHED");
    //       });
    //   });
  });
});

function createPaymentPlan(targetPopulationName) {
  cy.get("span").contains("Payment Module").click();
  cy.get('[data-cy="page-header-container"]').should('contain',"Payment Module");
  cy.get('[data-cy="button-new-payment-plan"]').should('be.visible')
  cy.get('[data-cy="button-new-payment-plan"]').click({force: true});
  cy.get('[data-cy="page-header-container"]').contains("New Payment Plan");
  cy.get('[data-cy="input-target-population"]').first().click();
  cy.uniqueSeed().then(seed => {
    cy.get(`[data-cy="select-option-${targetPopulationName}-${seed}"]`).click();
  });
  cy.get('[data-cy="input-start-date"]').click().type("2023-12-12");
  cy.get('[data-cy="input-end-date"]').click().type("2023-12-23");
  cy.get('[data-cy="input-currency"]').click().type("Afghan")
    .type("{downArrow}{enter}");
  cy.get('[data-cy="input-dispersion-start-date"]').click().type("2033-12-12");
  cy.get('[data-cy="input-dispersion-end-date"]').click().type("2033-12-23");
  cy.get('[data-cy="button-save-payment-plan"]').click({force: true});



}

