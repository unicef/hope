import BaseComponent from "../../base.component";

export default class NewTicket extends BaseComponent {
  // Locators
  title = 'h5[data-cy="page-header-title"]';
  selectCountry = 'div[data-cy="select-category"]';
  buttonNext = 'button[data-cy="button-submit"]';
  // Texts
  textTitle = "New Ticket";
  textNext = "Next";
  // Elements
  getTitle = () => cy.get(this.title);
  getSelectCountry = () => cy.get(this.selectCountry);
  getButtonNext = () => cy.get(this.buttonNext);
  checkElementsOnPage() {
    this.getTitle().contains(this.textTitle);
    this.getButtonNext().contains(this.textNext);
    this.getSelectCountry().should("be.visible");
  }
}
