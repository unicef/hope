import Login from "../../page-objects/pages/login/login.po";

let l = new Login();
context("Login", () => {
  after(() => {
    cy.adminLogin();
  });
  it("login with valid username and valid password", () => {
    cy.scenario([
      "Log in via admin panel",
      "Go to Home page",
      "Check if logged in",
    ]);
    cy.adminLogin();
    cy.navigateToHomePage();
    cy.get("h5").should("contain", "Test Programm");
  });
  it("Check the login with valid username and Invalid password", () => {
    cy.scenario([
      "Log in via admin panel using invalid password",
      "Go to Home page",
      "Check if did not log in",
    ]);
    Cypress.session.clearCurrentSessionData();
    cy.visit("/");
    l.navigateToLoginPage();
    cy.get('input[name="username"]').type(Cypress.env("username"));
    cy.get('input[name="password"]').type("wrong-password");
    cy.get("input").contains("Log in").click();
    cy.get(".errornote").should(
      "contain",
      "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
    );
  });
  it("Check the login with Invalid username and valid password", () => {
    cy.scenario([
      "Log in via admin panel using invalid login",
      "Go to Home page",
      "Check if did not log in",
    ]);
    Cypress.session.clearCurrentSessionData();
    l.navigateToLoginPage();
    cy.get('input[name="username"]').type("wrong-username");
    cy.get('input[name="password"]').type(Cypress.env("password"));
    cy.get("input").contains("Log in").click();
    cy.get(".errornote").should(
      "contain",
      "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
    );
  });
  it("Check the login with Invalid username and Invalid password", () => {
    cy.scenario([
      "Log in via admin panel using invalid login and password",
      "Go to Home page",
      "Check if did not log in",
    ]);
    Cypress.session.clearCurrentSessionData();
    l.navigateToLoginPage();
    cy.get('input[name="username"]').type("wrong-username");
    cy.get('input[name="password"]').type("wrong-password");
    cy.get("input").contains("Log in").click();
    cy.get(".errornote").should(
      "contain",
      "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
    );
  });
  it("176667: Check page after logout", () => {
    cy.scenario([
      "Logout",
      "Check login page",
      "Check main page",
      "Log in via admin panel using valid login and password",
      "Go to Home page",
      "Check if did not log in",
    ]);
    cy.adminLogin();
    cy.navigateToHomePage();
    cy.get("h5").should("contain", "Test Programm");
    l.getMenuUserProfile().click();
    l.getMenuItemLogout().click();
    cy.url().should("include", "login");
    cy.get("p").contains("Login via Active Directory");
    cy.visit("/");
    cy.url().should("include", "login?next=/");
    cy.get("p").contains("Login via Active Directory");
    cy.adminLogin();
    cy.navigateToHomePage();
    cy.get("h5").should("contain", "Test Programm");
  });
});
