import BaseComponent from "../../base.component";

export default class NewTicket extends BaseComponent {
  // Locators
  title = 'h5[data-cy="page-header-title"]';
  selectCategory = 'div[data-cy="select-category"]';
  issueType = 'div[data-cy="select-issueType"]'
  buttonNext = 'button[data-cy="button-submit"]';
  statusOptions = 'li[role="option"]';

  // Texts
  textTitle = "New Ticket";
  textNext = "Next";
  // Elements
  getTitle = () => cy.get(this.title);
  getSelectCategory = () => cy.get(this.selectCategory);
  getIssueType = () => cy.get(this.issueType);
  getButtonNext = () => cy.get(this.buttonNext);
  getOption = () => cy.get(this.statusOptions);


  checkElementsOnPage() {
    this.getTitle().contains(this.textTitle);
    this.getButtonNext().contains(this.textNext);
    this.getSelectCategory().should("be.visible");
  }

  chooseCategory(category){
    this.getSelectCategory().click()
    this.getOption().contains(category).click()
  }

  chooseIssueType(issue){
    this.getIssueType().should("be.visible").click()
    this.getOption().contains(issue).click()
  }
}
