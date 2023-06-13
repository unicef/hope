import RegistrationDataImport from "../../page-objects/pages/registration_data_import/registration_data_import.po";

let rdi = new RegistrationDataImport();

describe("Registration Data Import", () => {
  beforeEach(() => {
    cy.adminLogin();
    cy.navigateToHomePage();
    cy.get("span").contains("Registration Data Import").click();
  });

  describe("Smoke tests Registration Data Import", () => {
    it.skip("Check Registration Data Import page", () => {});
    it.skip("Check Registration Data Import Details page", () => {});
  });

  describe("Component tests Registration Data Import", () => {
    context("Registration Data Import - Download Template", () => {
      it("Import Template", () => {
        cy.get("span").contains("IMPORT").click({ force: true });
        cy.window()
          .document()
          .then(function (doc) {
            doc.addEventListener("click", () => {
              setTimeout(function () {
                doc.location.reload();
              }, 5000);
            });
            cy.get("span").contains("DOWNLOAD TEMPLATE").click();
          });
        cy.verifyDownload("registration_data_import_template.xlsx", {
          timeout: 20000,
        });
      });
      it("Merge Data", () => {
        rdi.uploadRDIFile();

        return; // TODO: make this work
        rdi.mergeRDIFile();
        rdi.verifyMergedData();
      });
      it.skip("Refuse import", () => {});
      context("Registration Data Import Filters", () => {
        it.skip("Registration Data Import Search filter", () => {
          // ToDo
        });
        it.skip("Registration Data Import Import Date filter", () => {
          // ToDo
        });
        it.skip("Registration Data Import Imported By filter", () => {
          // ToDo
        });
        it.skip("Registration Data Import Status filter", () => {
          // ToDo
        });
      });
    });
  });
});
