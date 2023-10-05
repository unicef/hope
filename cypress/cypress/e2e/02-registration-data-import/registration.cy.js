import RegistrationDataImport from "../../page-objects/pages/registration_data_import/registration_data_import.po";

let registrationDataImport = new RegistrationDataImport();

describe("Registration Data Import", () => {
  beforeEach(() => {
    cy.navigateToHomePage();
    cy.get("span").contains("Registration Data Import").click();
  });

  describe("Smoke tests Registration Data Import", () => {
    it.skip("Check Registration Data Import page", () => {});
    it.skip("Check Registration Data Import Details page", () => {});
  });

  describe("Component tests Registration Data Import", () => {
    context("Registration Data Import - Download Template", () => {
      // ToDo: Refactor this in second milestone
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
      // ToDo: Refactor this in second milestone
      it("Merge Data", () => {
        registrationDataImport.uploadRDIFile();

        return; // TODO: make this work
        registrationDataImport.mergeRDIFile();
        registrationDataImport.verifyMergedData();
      });
      it.skip("Refuse import", () => {});
      context("Registration Data Import Filters", () => {
        it.skip("Registration Data Import Search filter", () => {});
        it.skip("Registration Data Import Import Date filter", () => {});
        it.skip("Registration Data Import Imported By filter", () => {});
        it.skip("Registration Data Import Status filter", () => {});
      });
    });
  });
  describe.skip("E2E tests Registration Data Import", () => {});

  describe("Regression tests Registration Data Import", () => {
    it("174517: Check clear cash", () => {
      cy.scenario([
        "Go to Registration Data Import page",
        "Press Menu User Profile button",
        "Press Clear Cache button",
        "Check if page was opened properly",
      ]);
      registrationDataImport.clearCache();
      cy.get("h5").contains("Registration Data Import");
    });
  });
});
