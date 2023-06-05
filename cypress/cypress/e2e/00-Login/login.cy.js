/// <reference types="cypress" />
context("Login", () => {
    it('login with valid username and valid password', () => {
        cy.adminLogin()
        cy.visit("/");
        cy.get("h5").should('contain', "Dashboard")
    })
    it('Check the login with valid username and Invalid password', () => {
        cy.visit("/api/unicorn/");
        cy.get('input[name="username"]').type(Cypress.env("username"));
        cy.get('input[name="password"]').type("wrong-password");
        cy.get("input").contains("Log in").click();
        cy.get('.errornote').should('contain', "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.")
    })
    it('Check the login with Invalid username and valid password', () => {
        cy.visit("/api/unicorn/");
        cy.get('input[name="username"]').type("wrong-username");
        cy.get('input[name="password"]').type(Cypress.env("password"));
        cy.get("input").contains("Log in").click();
        cy.get('.errornote').should('contain', "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.")

    })
    it('Check the login with Invalid username and Invalid password', () => {
        cy.visit("/api/unicorn/");
        cy.get('input[name="username"]').type("wrong-username");
        cy.get('input[name="password"]').type("wrong-password");
        cy.get("input").contains("Log in").click();
        cy.get('.errornote').should('contain', "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive.")
    })
})
