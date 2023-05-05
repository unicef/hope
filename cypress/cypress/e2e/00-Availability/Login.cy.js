



context("Login", () => {
  

it('Positive Login UI Validation or visibility', () => {
  cy.adminLogin()
  cy.visit("/");  
})

    })