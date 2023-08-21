import AllProgrammes from "../../page-objects/pages/all_programmes/all_programmes.po";

let programmesPage = new AllProgrammes();

describe("Country Dashboard", () => {
  beforeEach(() => {
    programmesPage.navigateToProgrammePage();
  });

  describe("Smoke tests Global Program Filter", () => {
    it("Check All Programmes - Programme Management page", () => {
      cy.scenario([
        "1. Go to main page (All programmes set)",
        "2. Check if all elements on page exist",
      ]);
      programmesPage.getMenuButtonProgrammeManagement().should("be.visible");
      programmesPage.getMenuButtonFeedback().should("not.exist");
      programmesPage.getMenuButtonRegistrationDataImport().should("not.exist");
      programmesPage.getMenuButtonProgrammePopulation().should("not.exist");
      programmesPage.getMenuButtonHouseholds().should("not.exist");
      programmesPage.getMenuButtonIndividuals().should("not.exist");
      programmesPage.getMenuButtonProgrammeDetails().should("not.exist");
      programmesPage.getMenuButtonCashAssist().should("not.exist");
      programmesPage.getMenuButtonPaymentModule().should("not.exist");
      programmesPage.getMenuButtonReporting().should("not.exist");
      programmesPage.getMenuButtonProgrammeUsers().should("not.exist");
      programmesPage.getMenuButtonActivityLog().should("not.exist");
      programmesPage.getMenuButtonResourcesKnowledgeBase().should("be.visible");
      programmesPage.getMenuButtonResourcesConversations().should("be.visible");
      programmesPage
        .getMenuButtonResourcesToolsAndMaterials()
        .should("be.visible");
      programmesPage.getMenuButtonResourcesReleaseNote().should("be.visible");
      programmesPage.getMenuButtonGrievanceTickets().should("not.exist");
      programmesPage.getButtonNewProgram().should("be.visible");
      programmesPage.getFiltersSearch().should("be.visible");
      programmesPage.getFiltersStartDate().should("be.visible");
      programmesPage.getFiltersEndDate().should("be.visible");
      programmesPage.getFiltersSector().should("be.visible");
      programmesPage.getFiltersNumberOfHouseholdsMin().should("be.visible");
      programmesPage.getFiltersNumberOfHouseholdsMax().should("be.visible");
      programmesPage.getFiltersBudgetMin().should("be.visible");
      programmesPage.getFiltersBudgetMax().should("be.visible");
      programmesPage
        .getPageHeaderTitle()
        .contains(programmesPage.textPageHeaderTitle);
      programmesPage
        .getGlobalProgramFilter()
        .contains(programmesPage.textAllProgrammes);
      programmesPage.getButtonApply().should("be.visible");
      programmesPage.getButtonClear().should("be.visible");
      programmesPage.getTabTitle().contains(programmesPage.textProgrammes);
      programmesPage.getName().should("be.visible");
      programmesPage.getStatus().should("be.visible");
      programmesPage.getTimeframe().should("be.visible");
      programmesPage.getSelector().should("be.visible");
      programmesPage.getNumOfouseholds().should("be.visible");
      programmesPage.getBudget().should("be.visible");
      programmesPage.getProgrammesRows().should("have.length", 2);
    });
    it.skip("Choose program", () => {});
    it.skip("Come back to All Programmes", () => {});
  });

  describe("Component tests All Programmes - Global Program Filter", () => {
    context("Filters", () => {
      it.skip("Search filter", () => {});
      it.skip("Status filter", () => {});
      it.skip("Start Date filter", () => {});
      it.skip("End Date filter", () => {});
      it.skip("Sector filter", () => {});
      it.skip("Num. of Households filter From", () => {});
      it.skip("Num. of Households filter To", () => {});
      it.skip("Budget From filter", () => {});
      it.skip("Budget To filter", () => {});
    });
    context("Add New Programme", () => {
      it.skip("Add New Programme", () => {});
      it.skip("Cancel New Programme", () => {});
    });
  });
  describe.skip("E2E tests Country Dashboard", () => {});

  describe.skip("Regression tests Country Dashboard", () => {});
});
