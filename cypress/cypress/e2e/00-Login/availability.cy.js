import Login from "../../page-objects/pages/login/login.po";

let l = new Login();

context("Availibility", () => {
  it("Main page is available and shows the AD login view", () => {
    cy.scenario(["Go to Home page without login", "Check Login page"]);
<<<<<<< HEAD
    cy.visit("/");
=======
    cy.navigateToHomePage();
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
    cy.get("p").should("contain", "Login via Active Directory");
  });
  it("Admin panel is available", () => {
    cy.scenario(["Go to admin panel without login", "Check admin panel page"]);
    l.navigateToLoginPage();
    cy.get("a").should("contain", "HOPE Administration");
  });
});
