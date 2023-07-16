import BaseComponent from "../../base.component";

export default class PaymentModule extends BaseComponent {
  // Locators

  // Texts

  // Elements

  createPaymentPlan(targetPopulationName) {
    cy.visit("/");
    cy.get("span").contains("Payment Module").click();
    cy.get('[data-cy="page-header-container"]').contains("Payment Module");
    cy.get('[data-cy="button-new-payment-plan"]').click({
      force: true,
    });
    cy.get('[data-cy="page-header-container"]').contains("New Payment Plan");

    //fill in the form and save
    cy.get('[data-cy="input-target-population"]').first().click();
    cy.wait(200); // eslint-disable-line cypress/no-unnecessary-waiting

    cy.contains(`${targetPopulationName}`);
    cy.uniqueSeed().then((seed) => {
      cy.get(
        `[data-cy="select-option-${targetPopulationName}-${seed}"]`
      ).click();
    });
    cy.wait(1000);
    cy.get('[data-cy="input-start-date"]')
      .should("be.visible")
      .click()
      .type("2032-12-12");
    cy.get('[data-cy="input-end-date"]')
      .should("be.visible")
      .click()
      .type("2032-12-23");
    cy.get('[data-cy="input-currency"]')
      .should("be.visible")
      .click()
      .type("Afghan")
      .type("{downArrow}{enter}");
    cy.get('[data-cy="input-dispersion-start-date"]')
      .should("be.visible")
      .click()
      .type("2033-12-12");
    cy.get('[data-cy="input-dispersion-end-date"]')
      .should("be.visible")
      .click()
      .type("2033-12-23");
    cy.get('[data-cy="button-save-payment-plan"]').click({
      force: true,
    });
  }
}
