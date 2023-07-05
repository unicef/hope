import BaseComponent from "../../base.component";

export default class TDetailsPage extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  status = 'div[data-cy="target-population-status"]';
  // Texts
  // Elements
  getTitlePage = () => cy.get(this.titlePage);
  getStatus = () => cy.get(this.status);

  checkElementsOnPage(status) {
    this.getTitlePage().should("be.visible");
    this.getStatus().contains(status);
  }
}
