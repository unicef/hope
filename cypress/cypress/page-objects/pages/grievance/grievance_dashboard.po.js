import BaseComponent from "../../base.component";

export default class GrievanceDashboard extends BaseComponent {
  // Locators
  title = 'h5[data-cy="page-header-title"]';
  userGenerated = 'div[data-cy="label-USER-GENERATED"]';
  systemGenerated = 'div[data-cy="label-SYSTEM-GENERATED"]';
  averageResolution = 'div[data-cy="tickets-average-resolution-top-number"]';
  totalClosed = 'div[data-cy="total-number-of-closed-tickets-top-number"]';
  totalTickets = 'div[data-cy="total-number-of-tickets-top-number"]';
  // Texts
  textTitle = "Grievance Dashboard";
  // Elements
  getTitle = () => cy.get(this.title);
  getAverageResolution = () => cy.get(this.averageResolution);
  getTotalClosed = () => cy.get(this.totalClosed);
  getTotalTickets = () => cy.get(this.totalTickets);
  getUserGeneratedResolutions = () => cy.get(this.userGenerated).eq(2);
  getUserGeneratedClosed = () => cy.get(this.userGenerated).eq(1);
  getUserGeneratedTickets = () => cy.get(this.userGenerated).eq(0);
  getSystemGeneratedResolutions = () => cy.get(this.systemGenerated).eq(2);
  getSystemGeneratedClosed = () => cy.get(this.systemGenerated).eq(1);
  getSystemGeneratedTickets = () => cy.get(this.systemGenerated).eq(0);

  checkElementsOnPage() {
    this.getTitle().contains(this.textTitle);
    this.getAverageResolution().should("be.visible");
    this.getTotalClosed().should("be.visible");
    this.getTotalTickets().should("be.visible");
    this.getUserGeneratedResolutions().should("be.visible");
    this.getUserGeneratedClosed().should("be.visible");
    this.getUserGeneratedTickets().should("be.visible");
    this.getSystemGeneratedResolutions().should("be.visible");
    this.getSystemGeneratedClosed().should("be.visible");
    this.getSystemGeneratedTickets().should("be.visible");
  }
}
