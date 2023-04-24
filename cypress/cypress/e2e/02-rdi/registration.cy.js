/// <reference types="cypress" />
context("RDI", () => {
  beforeEach(() => {
    cy.adminLogin()
    cy.visit("/");
    cy.get("span").contains("Registration Data Import").click();
  })
  it("RDI visibility", () => {
    cy.get('[data-cy="button-import"]').should('be.visible')
    cy.get('[data-cy="table-title"]').should('be.visible')
    cy.get('[data-cy="filter-search"]').should('be.visible')
    cy.get('[data-cy="filter-import-date"]').should('be.visible')
    cy.get('[data-cy="filter-status"]').should('be.visible')
  })
  it("Download Template", () => {
    cy.get("button > span").contains("IMPORT").click({ force: true });
    cy.window().document().then(function (doc) {
      doc.addEventListener('click', () => {
        setTimeout(function () { doc.location.reload() }, 5000)
      })
      cy.get('span').contains('DOWNLOAD TEMPLATE').click()
    })
    cy.verifyDownload('registration_data_import_template.xlsx');
  })
 it("Registration Data Import and merge the data and verify merge file and View Ticket", () => {
    uploadRDIFile();
    mergeRDIFile()
    verifyMergedData()
    viewTicket()
    return;
  })
  it("Registration Data Import and Refuse the import", () => {
    uploadRDIFile();
    refuseImport()
    return;
  })
it('RDI- Searches by import title', () => {
    cy.createExcel()
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
    cy.wait(5000)
    cy.get('[data-cy="button-import-rdi"]').click({ force: true })
    cy.get("span").contains("Registration Data Import").click();
    cy.reload()
    cy.get('[data-cy="filter-search"]').type(name)
    cy.get('tbody tr').eq(0).each(($tablerows) => {
      cy.wrap($tablerows).within(() => {
        cy.get('td').eq(0).each(($data) => {
          expect($data.text()).to.contain(name)
        })
      })
    })
  })
  it('RDI- Searches by Date', () => {
    const d = new Date()
    cy.get('[data-cy="filter-import-date"]').type(d.toLocaleDateString('en-CA') + '{enter}')
    cy.get('tbody tr').eq(0).each(($tablerows) => {
      cy.wrap($tablerows).within(() => {
        cy.get('td').eq(2).each(($data) => {
          expect($data.text()).to.contain(d.toLocaleDateString('en-US', { day: "2-digit" }) + " " + d.toLocaleDateString('en-US', { month: "short" }) + " " + d.toLocaleDateString('en-US', { year: "numeric" }))
        })
      })
    })
  })

  it('RDI- Searches Imported by', () => {
    cy.get('input[type="text"]').eq(2).type('cypress@cypress.com{downArrow}{enter}')
    cy.reload()
    cy.get('tbody tr').eq(0).each(($tablerows) => {
      cy.wrap($tablerows).within(() => {
        cy.get('td').eq(5).each(($data) => {
          expect($data.text()).to.contain('cypress@cypress.com')
        })
      })
    })
  })
  it('RDI- Searches by status', () => {
    cy.get('[data-cy="filter-status"]').click()
    cy.get('li[data-value="IN_REVIEW"]').click()
    cy.reload()
    cy.get('tbody tr').eq(0).each(($tablerows) => {
      cy.wrap($tablerows).within(() => {
        cy.get('td').eq(1).each(($data) => {
          expect($data.text()).to.contain('IN REVIEW')
        })
      })
    })
  })

  it('RDI - Searches with all filters', () => {
    cy.createExcel()
    const d = new Date()
    cy.get("h5").contains("Registration Data Import");
    cy.get("span").contains("IMPORT").click({ force: true });
    cy.get("h2").contains("Select File to Import").click();
    cy.get('[data-cy="import-type-select"]').click();
    cy.get('[data-cy="excel-menu-item"]').click();
    cy.get('[data-cy="input-name"]').type(
      "Test import ".concat(d.toISOString())
    );
    const name = "Test import ".concat(d.toISOString())
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
    cy.wait(5000)
    cy.get('[data-cy="button-import-rdi"]').click({ force: true })
    cy.get("span").contains("Registration Data Import").click();
    cy.reload()
    cy.get('[data-cy="filter-search"]').type(name)
    cy.get('[data-cy="filter-import-date"]').type(d.toLocaleDateString('en-CA'))

    cy.get('input[type="text"]').eq(2).type('cypress@cypress.com{downArrow}{enter}')
    cy.get('[data-cy="filter-status"]').click()
    cy.get('li[data-value="IN_REVIEW"]').click()

    cy.get('tbody tr').eq(0).each(($tablerows) => {
      cy.wrap($tablerows).within(() => {
        cy.get('td').each(($data) => {
          cy.log($data.text())
        })
      })
    })
  })
});

function uploadRDIFile() {
  cy.createExcel()
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
  cy.wait(5000)
  cy.get('[data-cy="button-import-rdi"]').click({ force: true })
  cy.get("span").contains("Registration Data Import").click();
  cy.reload()
  cy.get('[data-cy="status-container"]').eq(0).should('contain', 'IN REVIEW')
}
function mergeRDIFile() {
  cy.get('[data-cy="status-container"]').eq(0).click({ force: true })
  cy.get('[data-cy="label-Total Number of Households"]').contains("1");
  cy.get('[data-cy="label-Total Number of Individuals"]').contains("1");
  cy.get("span").contains("Merge").click({ force: true });
  cy.get('strong').should('contain', '1 households and 1 individuals will be merged.')
  cy.get("span").contains("MERGE").click({ force: true })

  cy.get("span").contains("Registration Data Import").click();
  cy.reload()
  cy.get('[data-cy="status-container"]').eq(0).should('contain', 'MERGED')
}

function verifyMergedData() {
  let householdId;
  let individualId;
  cy.get('[data-cy="status-container"]').eq(0).click({ force: true })
  cy.log("Looking for householdId");
  cy.get('[data-cy="imported-households-row"]')
    .find("td:nth-child(2)")
    .then(($td) => {
      householdId = $td.text().split(" (")[0];
      cy.log($td.text())
      cy.log(`Saved householdId: ${householdId}`);
    })
    .then(() => {
      cy.get("button> span").contains("Individuals").click({ force: true });
      cy.get('[data-cy="imported-individuals-table"]')
        .find(`tbody > tr:nth-child(1) > td:nth-child(1)`)
        .then(($td) => {
          individualId = $td.text().split(" (")[0];
          cy.log(`Saved individualId: ${individualId}`);
        })
        .then(() => {
          cy.get("span").contains("Population").click();
          cy.get("span").contains("Households").click();
          cy.log(`looking for householdId: ${householdId}`);
          cy.get('[data-cy="hh-filters-search"]')
            .find("input")
            .type(householdId, { force: true });
          cy.get("td").should("contain", householdId);
          cy.get("span").contains("Individuals").click({ force: true });
          cy.log(`looking for individualId: + ${individualId}`);
          cy.get('[data-cy="ind-filters-search"]').type(individualId);
          cy.get("td").should("contain", individualId);
        });
    });
}
function refuseImport() {
  cy.get('[data-cy="status-container"]').eq(0).click({ force: true })
  cy.get('span').contains('Refuse Import').click({ force: true })
  cy.get("span").contains("Registration Data Import").click();
  cy.reload()
  cy.get('[data-cy="status-container"]').eq(0).should('contain', 'REFUSED')
}
 function viewTicket()
 {
  cy.get("span").contains("Registration Data Import").click();
  cy.get('[data-cy="status-container"]').eq(0).click({ force: true })
  cy.get('span').contains('View Tickets').click({ force: true })
  cy.get('h5').should('contain', 'Grievance and Feedback')
 }


