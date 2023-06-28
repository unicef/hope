import BaseComponent from "../../base.component";

export default class GrievanceDashboard extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  userGenerated = 'div[data-cy="label-USER-GENERATED"]';
  systemGenerated = 'div[data-cy="label-SYSTEM-GENERATED"]';
  averageResolution = 'div[data-cy="tickets-average-resolution-top-number"]';
  totalClosed = 'div[data-cy="total-number-of-closed-tickets-top-number"]';
  totalTickets = 'div[data-cy="total-number-of-tickets-top-number"]';
  // Texts
  textTitle = "Grievance Dashboard";
  // Elements
  getTitle = () => cy.get(this.titlePage);
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
    this.getAverageResolution().scrollIntoView().should("be.visible");
    this.getTotalClosed().scrollIntoView().should("be.visible");
    this.getTotalTickets().scrollIntoView().should("be.visible");
    this.getUserGeneratedResolutions().scrollIntoView().should("be.visible");
    this.getUserGeneratedClosed().scrollIntoView().should("be.visible");
    this.getUserGeneratedTickets().scrollIntoView().should("be.visible");
    this.getSystemGeneratedResolutions().scrollIntoView().should("be.visible");
    this.getSystemGeneratedClosed().scrollIntoView().should("be.visible");
    this.getSystemGeneratedTickets().scrollIntoView().should("be.visible");
  }
}
