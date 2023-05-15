/// <reference types="cypress" />
context("RDI", () => {
  beforeEach(() => {
    cy.adminLogin()
    cy.visit("/");
  cy.get("span").contains("Registration Data Import").click();
  });
  it("RDI - Download Template", () => {
    cy.get("span").contains("IMPORT").click({ force: true });
    cy.window().document().then(function (doc) {
      doc.addEventListener('click', () => {
        setTimeout(function () { doc.location.reload() }, 5000)
      })
      cy.get('span').contains('DOWNLOAD TEMPLATE').click()
    })
    cy.verifyDownload('registration_data_import_template.xlsx',{timeout:20000});
  })
  it("Registration Data Import", () => {
    uploadRDIFile();
    return;
  })
  
  it("RDI - Merge the data and verify the merge", () => {
    uploadRDIFile();
    mergeRDIFile()
    verifyMergedData()
    return;
  })
});

function uploadRDIFile() {
  cy.get("h5").contains("Registration Data Import");
  cy.get("span").contains("IMPORT").click({ force: true });
  cy.get("h2").contains("Select File to Import").click();
  cy.get('[data-cy="import-type-select"]').click();
  cy.get('[data-cy="excel-menu-item"]').click();
  cy.get('[data-cy="input-name"]').type(
    "Test import ".concat(new Date().toISOString())
  );
  const name = "Test import ".concat(new Date().toISOString())
  cy.uniqueSeed().then((seed) => {
    const fileName = `rdi_import_1_hh_1_ind_seed_${seed}.xlsx`;
    cy.fixture(fileName, "base64").then((fileContent) => {
      cy.get('[data-cy="file-input"]').attachFile({
        fileContent,
        fileName,
        mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        encoding: "base64",
      });
    });
  });
  cy.get('[data-cy="button-import-rdi"]', { timeout: 20000 }).should('be.enabled').click()
  cy.get("span").contains("Registration Data Import").click();
  cy.reload()
  cy.get('[data-cy="status-container"]').eq(0).should('contain', 'IN REVIEW')
}
function mergeRDIFile() {
  cy.get('[data-cy="number-of-households"]').contains(
    "1 Household available to import",
    {
      timeout: 10000,
    }
  );
  cy.get('[data-cy="number-of-individuals"]').contains(
    "1 Individual available to import"
  );
  cy.get("div").contains("Errors").should("not.exist");
  cy.get('[data-cy="button-import-rdi"').click();

  cy.wait(1000);
  cy.reload();
  cy.wait(500);
  // it lets the browser load the status

  cy.get("div").contains("IMPORT ERROR").should("not.exist");
  cy.get("div").contains("IN REVIEW");

  cy.get("span").contains("Merge").click({ force: true }); // top of page
  cy.get("span").contains("MERGE").click({ force: true }); // inside modal

  cy.get("div").contains("MERGING");

  cy.reload();

  cy.get("div").contains("MERGED");
}
