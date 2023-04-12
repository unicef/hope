context("Visibility", () => {
    beforeEach(() => {
        cy.adminLogin()
      });
  
    it("Dashboasrd visibility", () => {
     cy.visit("/");
      cy.get('h5').should("contain", "Dashboard");
      cy.get('div.sc-cJSrbW.hzRFUG').eq(0).should("contain",'TOTAL AMOUNT TRANSFERRED')
      cy.get('div.sc-cJSrbW.hzRFUG').eq(1).should("contain",'TOTAL NUMBER OF HOUSEHOLDS REACHED')
      cy.get('div.sc-cJSrbW.hzRFUG').eq(2).should("contain",'TOTAL NUMBER OF INDIVIDUALS REACHED')
      cy.get('div.sc-cJSrbW.hzRFUG').eq(3).should("contain",'TOTAL NUMBER OF CHILDREN REACHED')
      cy.get('.MuiGrid-grid-xs-8 > :nth-child(2) > .MuiBox-root').should("contain",'Number of Programmes by Sector')
      cy.get('.MuiGrid-grid-xs-8 > :nth-child(3) > .MuiBox-root').should('contain','Total Transferred by Month')
      cy.get('.kifCwh').should('contain','Volume by Delivery Mechanism in USD')
      cy.get('.MuiGrid-grid-xs-8 > :nth-child(5)').should("contain",'Payment Verification')
      cy.get('.MuiGrid-spacing-xs-6 > :nth-child(4) > :nth-child(2)').should("contain",'Grievances and Feedback')
      cy.get('.MuiGrid-spacing-xs-6 > :nth-child(4) > :nth-child(3)').should("contain",'Payments')
    })
   


})
