import Login from "../../page-objects/pages/login/login.po";

let l = new Login();

context("Availibility", () => {
  it.skip("Main page is available and shows the AD login view", () => {
    // ToDo: Global Programme changes
    cy.navigateToHomePage();
    cy.get("p").should("contain", "Login via Active Directory");
  });
  it("Admin panel is available", () => {
    l.navigateToLoginPage();
    cy.get("a").should("contain", "HOPE Administration");
  });
});
