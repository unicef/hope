/// <reference types="cypress" />

context("Payment", () => {
  const downloadsFolder = Cypress.config("downloadsFolder");

  const fileName = (id) => `payment_plan_payment_list_${id}`;

  const xlsxFileName = (id) => `${fileName(id)}.xlsx`;
  const zipFileName = (id) => `${fileName(id)}.zip`;

  beforeEach(() => {
    cy.uniqueSeed().then((seed) => {
      cy.exec(`yarn init-scenario payment_plan --seed ${seed}`);
    });
    cy.visit("/api/unicorn/");
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get("input").contains("Log in").click();
    cy.visit("/api/unicorn/core/businessarea/");
    cy.get("th").contains("Afghanistan").parent().find("a").click();
    cy.get("#id_is_payment_plan_applicable").should("be.checked");
  });

  it("Can create a payment plan", () => {
    let targetPopulationName = "PaymentPlanTargetPopulation";
    let paymentPlanUnicefId;

    //New Payment Plan page
    cy.visit("/");
    cy.get("span").contains("Payment Module").click();
    cy.get('[data-cy="page-header-container"]').contains("Payment Module");
    cy.get('[data-cy="button-new-payment-plan"]').click({
      force: true,
    });
    cy.get('[data-cy="page-header-container"]').contains("New Payment Plan");

    //fill in the form and save
    cy.get('[data-cy="input-target-population"]').first().click();
    cy.wait(200); // eslint-disable-line cypress/no-unnecessary-waiting

    return; // TODO: target population is not always showing
    cy.uniqueSeed().then((seed) => {
      cy.get(
        `[data-cy="select-option-${targetPopulationName}-${seed}"]`
      ).click();
    });
    cy.get('[data-cy="input-start-date"]').click().type("2022-12-12");
    cy.get('[data-cy="input-end-date"]').click().type("2022-12-23");
    cy.get('[data-cy="input-currency"]').first().click();
    cy.get('[data-cy="select-option-Afghan afghani"]').click();
    cy.get('[data-cy="input-dispersion-start-date"]')
      .click()
      .type("2023-12-12");
    cy.get('[data-cy="input-dispersion-end-date"]').click().type("2023-12-23");
    cy.get('[data-cy="button-save-payment-plan"]').click({
      force: true,
    });
    cy.wait(3000); // eslint-disable-line cypress/no-unnecessary-waiting

    //Payment Plan Details page
    cy.get('[data-cy="page-header-container"]').contains("Payment Plan ID", {
      timeout: 10000,
    });
    cy.get('[data-cy="pp-unicef-id"]').then(($el) => {
      paymentPlanUnicefId = $el.text();
    });
    cy.get("h6").contains("Details");
    cy.get("h6").contains("Results");
    cy.get("h6").contains("Payments List");
    cy.get("h6").contains("Activity Log");

    //Lock plan
    cy.get('[data-cy="button-lock-plan"]').click({
      force: true,
    });
    cy.get('[data-cy="button-submit"]').click({
      force: true,
    });

    //Entitlements
    cy.get("[data-cy=input-entitlement-formula]").should("exist");
    cy.get("[data-cy=input-entitlement-formula] > .MuiSelect-root").click({
      force: true,
    });
    cy.get('[data-cy="input-entitlement-formula"]').click({ force: true });
    cy.uniqueSeed().then((seed) => {
      cy.get("li").contains(`Rule-${seed}`).click({ force: true });
    });
    cy.get('[data-cy="button-apply-steficon"]').click({ force: true });
    cy.reload();
    cy.get('[data-cy="total-entitled-quantity-usd"]').contains("USD");
    // TODO: check the amount

    //Set up FSP
    cy.get('[data-cy="button-set-up-fsp"]').click({ force: true });
    cy.get('[data-cy="page-header-container"]').contains("Set up FSP", {
      timeout: 10000,
    });
    cy.get(
      '[data-cy="select-deliveryMechanisms[0].deliveryMechanism"]'
    ).click();
    cy.get('[data-cy="select-option-Transfer"]').click();
    cy.get('[data-cy="button-next-save"]').click({ force: true });
    cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]');
    cy.get('[data-cy="select-deliveryMechanisms[0].fsp"]').click();
    cy.get('[data-cy="select-option-Test FSP Transfer"]').click();
    cy.get('[data-cy="button-next-save"]').click({ force: true });
    cy.contains("Volume by Delivery Mechanism in USD");
    cy.get("[data-cy='button-lock-plan']").click({ force: true });
    cy.get("[data-cy='button-submit']").click({ force: true });
    cy.get("[data-cy='status-container']").contains("FSP Locked");

    //Acceptance Process
    cy.get("[data-cy='button-send-for-approval']").click({ force: true });
    cy.contains("Acceptance Process");
    cy.get("[data-cy='button-approve']").click({ force: true });
    cy.get("[data-cy='button-submit']").click({ force: true });
    cy.get('[data-cy="status-container"]').contains("In Authorization");
    cy.get("[data-cy='button-authorize']").click({ force: true });
    cy.get("[data-cy='button-submit']").click({ force: true });
    cy.get('[data-cy="status-container"]').contains("In Review");
    cy.get("[data-cy='button-mark-as-reviewed']").click({ force: true });
    cy.get("[data-cy='button-submit']").click({ force: true });
    cy.get('[data-cy="status-container"]').contains("Accepted");

    //XLSX template
    cy.get('[data-cy="button-export-xlsx"]').click({ force: true });
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.reload();
    cy.wait(1000); // eslint-disable-line cypress/no-unnecessary-waiting
    const nameXlsx = xlsxFileName(paymentPlanUnicefId);
    const downloadedFilePathXlsx = `${downloadsFolder}/${nameXlsx}`;
    cy.exec(
      `node cypress/scripts/fillXlsxEntitlements.js ${downloadedFilePathXlsx}`
    );
    cy.get('[data-cy="button-download-template"]').click({ force: true });
    const nameTemplate = xlsxFileName(paymentPlanUnicefId);
    const filledFilePathTemplate = `out_${nameTemplate}`;
    cy.log(filledFilePathTemplate);
    cy.get('[data-cy="button-import"]').click({ force: true });
    cy.fixture(filledFilePathTemplate, "base64").then((fileContent) => {
      cy.get('[data-cy="file-input"]').upload({
        fileContent,
        fileName: name,
        mimeType:
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        encoding: "base64",
      });
    });
    cy.get('[data-cy="button-import-entitlement"').click({ force: true });
    cy.wait(2000); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.reload();
    cy.get("td").should("not.contain", "Missing");
    cy.get('[data-cy="button-export-xlsx"]').click({ force: true });
    cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
    cy.reload();
    cy.get('[data-cy="button-download-xlsx"]').click({ force: true });
    cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
    const nameZip = zipFileName(paymentPlanUnicefId);
    const downloadedFilePathZip = `${downloadsFolder}/${nameZip}`;
    cy.exec(`unzip ${downloadedFilePathZip} -d ${downloadsFolder}`);
    const currentRunFileName = fileName(paymentPlanUnicefId);
    cy.exec(
      `find ${downloadsFolder} | grep ${currentRunFileName} | grep FSP | sed 's@.*/@@'`
    )
      .then((result) => {
        let fspXlsxFilenames = result.stdout.split("\n");
        cy.log(fspXlsxFilenames);
        expect(fspXlsxFilenames.length).to.eq(count);
      })
      .then(() => {
        //Reconciliation Info
        const fspFilename1 = fspXlsxFilenames[0];
        cy.log(downloadsFolder);
        const downloadedFilePath = `${downloadsFolder}/${fspFilename1}`;
        cy.log(downloadedFilePath);
        cy.exec(
          `node cypress/scripts/fillXlsxReconciliation.js "${downloadedFilePath}"`
        );
        const fspFilename2 = fspXlsxFilenames[0];
        const filledFilePath = `out_${fspFilename2}`;
        cy.log(filledFilePath);
        cy.get('[data-cy="button-import"]').click({ force: true });
        cy.fixture(filledFilePath, "base64").then((fileContent) => {
          cy.get('[data-cy="file-input"]').upload({
            fileContent,
            fileName: fspFilename,
            mimeType:
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            encoding: "base64",
          });
        });
        cy.get('[data-cy="file-input"').click({ force: true });
        // cy.get('[data-cy="imported-file-name"]').should('exist'); // TODO
        cy.get('[data-cy="button-import-submit"').click({ force: true });
        cy.wait(500); // eslint-disable-line cypress/no-unnecessary-waiting
        cy.reload();
        cy.get('[data-cy="delivered-quantity-cell"]').each(($el) => {
          cy.wrap($el).should("contain", "AFN");
          cy.wrap($el).should("contain", "100");
        });
      });
  });
});
