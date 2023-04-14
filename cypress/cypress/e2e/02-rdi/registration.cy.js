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
    cy.get('.sc-keFjpB > .MuiInputBase-root > .MuiInputBase-input').should('be.visible')
  })

  it("Download Template", () => {
    cy.get("button > span").contains("IMPORT").click({ force: true });
    cy.window().document().then(function (doc) {
      doc.addEventListener('click', () => {
        setTimeout(function () { doc.location.reload() }, 5000)
      })
      cy.get('span.MuiButton-label').contains('DOWNLOAD TEMPLATE').click()
    })
    cy.verifyDownload('registration_data_import_template.xlsx');
  })

  it("Registration Data Import with excel and verfify", () => {
    uploadRDIFile();
    verifyUpload()
    return;
  })
  it("Registration Data Import and merge the data and verify merge file", () => {
    uploadRDIFile();
    mergeRDIFile()
    verifyMergedData()
    return;
  })

  it("Registration Data Import and Refuse the import", () => {
    uploadRDIFile();
    verifyUpload()
    refuseImport()
    verfifyRefuseImport()
    return;
  })
  it('Merged View ticket', () => {
    uploadRDIFile();
    mergeRDIFile()
    cy.get('div.sc-kEYyzF').click({ force: true })
    cy.reload()
    cy.get('tbody tr').eq(0).each(($tablerows) => {
      cy.wrap($tablerows).within(() => {
        cy.get('td').eq(1).each(($data) => {
          if ($data.text() == 'MERGED')
            cy.contains('MERGED').click({ force: true })
        })
      })
    })
    cy.get('a span.MuiButton-label').click({ force: true })
    cy.get('h5').should('contain', 'Grievance and Feedback')
  })
});

function uploadRDIFile() {
  cy.createExcel()
  cy.get("h5").contains("Registration Data Import");
  cy.get("button > span").contains("IMPORT").click({ force: true });
  cy.get("h2").contains("Select File to Import").click();
  cy.get('[data-cy="import-type-select"]').click();
  cy.get('[data-cy="excel-menu-item"]').click();

  cy.get('[data-cy="input-name"]').type(
    "Test import ".concat(new Date().toISOString())
  );
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
  cy.get('[data-cy="button-import-rdi"] > .MuiButton-label').click({ force: true })
  cy.get('div.sc-kEYyzF').click({ force: true })
}

function verifyUpload() {
  cy.reload()
  cy.get('tbody tr').eq(0).each(($tablerows) => {
    cy.wrap($tablerows).within(() => {
      cy.get('td').eq(1).each(($data) => {
        // cy.log($data.text())
        if ($data.text() == 'IN REVIEW')
          expect($data.text()).to.eq('IN REVIEW')
      })
    })
  })
}
function mergeRDIFile() {
  cy.reload()
  cy.get('tbody tr').eq(0).each(($tablerows) => {
    cy.wrap($tablerows).within(() => {
      cy.get('td').eq(1).each(($data) => {
        if ($data.text() == 'IN REVIEW')
          cy.contains('IN REVIEW').click({ force: true })
      })
    })
  })
  cy.get('[data-cy="label-Total Number of Households"]').contains("1");
  cy.get('[data-cy="label-Total Number of Individuals"]').contains("1");
  cy.get("span").contains("Merge").click({ force: true });
  cy.get('strong').should('contain', '1 households and 1 individuals will be merged.')
  cy.get("span").contains("MERGE").click({ force: true })
  cy.wait(2000)
}

function verifyMergedData() {
  let householdId;
  let individualId;
  cy.get('div.sc-kEYyzF').click({ force: true })
  cy.log("Looking for householdId");
  cy.get('tbody tr').eq(0).each(($tablerows) => {
    cy.wrap($tablerows).within(() => {
      cy.get('td').eq(1).each(($data) => {
        cy.contains('MERGED').click({ force: true })
      })
    })
  })
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
  cy.get('tbody tr').eq(0).each(($tablerows) => {
    cy.wrap($tablerows).within(() => {
      cy.get('td').eq(1).each(($data) => {
        if ($data.text() == 'IN REVIEW')
          cy.contains('IN REVIEW').click({ force: true })
      })
    })
  })
  cy.get('span').contains('Refuse Import').click({ force: true })
  cy.wait(2000)
  cy.get('div.sc-kEYyzF').click({ force: true })
}
function verfifyRefuseImport() {
  cy.get('tbody tr').eq(0).each(($tablerows) => {
    cy.wrap($tablerows).within(() => {
      cy.get('td').eq(1).each(($data) => {
        if ($data.text() == 'REFUSED')
          expect($data.text()).to.eq('REFUSED')
      })
    })
  })
}

