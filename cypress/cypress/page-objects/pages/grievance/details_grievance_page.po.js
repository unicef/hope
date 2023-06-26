import BaseComponent from "../../base.component";

export default class GDetailsPage extends BaseComponent {
  // Locators
  title = 'h5[data-cy="page-header-title"]';
  buttonEdit = 'a[data-cy="button-edit"]';
  buttonSetInProgress = 'button[data-cy="button-set-to-in-progress"]';
  // buttonAssignToMe = 'button';
  ticketStatus = 'div[data-cy="label-Status"]';
  ticketPriority = 'div[data-cy="label-Priority"]';
  ticketUrgency = 'div[data-cy="label-Urgency"]';
  ticketAssigment = 'div[data-cy="label-Assigned to"]';
  ticketCategory = 'div[data-cy="label-Category"]';
  ticketHouseholdID = 'div[data-cy="label-Household ID"]';
  ticketIndividualID = 'div[data-cy="label-Individual ID"]';
  ticketPaymentLabel = 'div[data-cy="label-Payment ID"]';
  ticketCategoryBy = 'div[data-cy="label-Created By"]';
  dateCreation = 'div[data-cy="label-Date Created"]';
  lastModifiedDate = 'div[data-cy="label-Last Modified Date"]';
  AdministrativeLevel = 'div[data-cy="label-Administrative Level 2"]';
  AreaVillage = 'div[data-cy="label-Area / Village / Pay point"]';
  languagesSpoken = 'div[data-cy="label-Languages Spoken"]';
  documentation = 'div[data-cy="label-Documentation"]';
  ticketDescription = 'div[data-cy="label-Description"]';
  comments = 'div[data-cy="label-Comments"]';
  // Texts
  textTitle = "Ticket ID: GRV-0000001";
  textStatusNew = "New";
  textPriorityNotSet = "Not set";
  textUrgencyNotSet = "Not set";
  textNotAssigment = "-";
  textNoCategory = "Needs Adjudication";
  // Elements
  getTitle = () => cy.get(this.title);
  getTicketStatus = () => cy.get(this.ticketStatus);
  getTicketPriority = () => cy.get(this.ticketPriority);
  getTicketUrgency = () => cy.get(this.ticketUrgency);
  getTicketAssigment = () => cy.get(this.ticketAssigment);
  getTicketCategory = () => cy.get(this.ticketCategory);

  checkElementsOnPage() {
    this.getTitle().contains(this.textTitle);
    this.getTicketStatus().contains(this.textStatusNew);
    this.getTicketPriority().contains(this.textPriorityNotSet);
    this.getTicketUrgency().contains(this.textUrgencyNotSet);
    this.getTicketAssigment().contains(this.textNotAssigment);
    this.getTicketCategory().contains(this.textNoCategory);
  }
}
