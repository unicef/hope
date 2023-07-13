import BaseComponent from "../../base.component";

export default class GrievanceDetailsPage extends BaseComponent {
  // Locators
<<<<<<< HEAD
  pageHeaderContainer = 'div[data-cy="page-header-container"]';
=======
>>>>>>> staging
  title = 'h5[data-cy="page-header-title"]';
  buttonEdit = 'a[data-cy="button-edit"]';
  buttonSetInProgress = 'button[data-cy="button-set-to-in-progress"]';
  buttonAssignToMe = 'button[data-cy="button-assign-to-me"]';
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
  administrativeLevel = 'div[data-cy="label-Administrative Level 2"]';
  areaVillage = 'div[data-cy="label-Area / Village / Pay point"]';
  languagesSpoken = 'div[data-cy="label-Languages Spoken"]';
  documentation = 'div[data-cy="label-Documentation"]';
  ticketDescription = 'div[data-cy="label-Description"]';
  comments = 'div[data-cy="label-Comments"]';
  createLinkedTicket = 'button[data-cy="button-create-linked-ticket"]';
  markDuplicate = 'button[data-cy="button-mark-duplicate"]';
  cellIndividualID = 'th[data-cy="table-cell-individual-id"]';
  cellHouseholdID = 'th[data-cy="table-cell-household-id"]';
  cellFullName = 'th[data-cy="table-cell-full-name"]';
  cellGender = 'th[data-cy="table-cell-gender"]';
  cellDateOfBirth = 'th[data-cy="table-cell-date-of-birth"]';
  cellSimilarityScore = 'th[data-cy="table-cell-similarity-score"]';
  cellLastRegistrationDate = 'th[data-cy="table-cell-last-registration-date"]';
  cellDocType = 'th[data-cy="table-cell-doc-type"]';
  cellDoc = 'th[data-cy="table-cell-doc-number"]';
  cellAdminLevel2 = 'th[data-cy="table-cell-admin-level2"]';
  cellVillage = 'th[data-cy="table-cell-village"]';
  newNoteField = 'textarea[data-cy="input-newNote"]';
  buttonNewNote = 'button[data-cy="button-add-note"]';
  // Texts
<<<<<<< HEAD
  textTitle = "Ticket ID: ";
=======
  textTitle = "Ticket ID: GRV-0000001";
>>>>>>> staging
  textStatusNew = "New";
  textPriorityNotSet = "Not set";
  textUrgencyNotSet = "Not set";
  textNotAssigment = "-";
<<<<<<< HEAD
  textAssigmentRootRootkowski = "Root Rootkowski"
  textNoCategory = "Needs Adjudication";
  // Elements
  getPageHeaderContainer = () => cy.get(this.pageHeaderContainer);
=======
  textNoCategory = "Needs Adjudication";
  // Elements
>>>>>>> staging
  getTitle = () => cy.get(this.title);
  getButtonAssignToMe = () => cy.get(this.buttonAssignToMe);
  getTicketStatus = () => cy.get(this.ticketStatus);
  getTicketPriority = () => cy.get(this.ticketPriority);
  getTicketUrgency = () => cy.get(this.ticketUrgency);
  getTicketAssigment = () => cy.get(this.ticketAssigment);
  getTicketCategory = () => cy.get(this.ticketCategory);
  getTicketHouseholdID = () => cy.get(this.ticketHouseholdID);
  getTicketIndividualID = () => cy.get(this.ticketIndividualID);
  getTicketPaymentLabel = () => cy.get(this.ticketPaymentLabel);
  getTicketCategoryBy = () => cy.get(this.ticketCategoryBy);
  getDateCreation = () => cy.get(this.dateCreation);
  getLastModifiedDate = () => cy.get(this.lastModifiedDate);
  getAdministrativeLevel = () => cy.get(this.administrativeLevel);
  getAreaVillage = () => cy.get(this.areaVillage);
  getLanguagesSpoken = () => cy.get(this.languagesSpoken);
  getDocumentation = () => cy.get(this.documentation);
  getTicketDescription = () => cy.get(this.ticketDescription);
  getCreateLinkedTicket = () => cy.get(this.createLinkedTicket);
  getMarkDuplicate = () => cy.get(this.markDuplicate);
  getCellIndividualID = () => cy.get(this.cellIndividualID);
  getCellHouseholdID = () => cy.get(this.cellHouseholdID);
  getCellFullName = () => cy.get(this.cellFullName);
  getCellGender = () => cy.get(this.cellGender);
  getCellDateOfBirth = () => cy.get(this.cellDateOfBirth);
  getCellSimilarityScore = () => cy.get(this.cellSimilarityScore);
  getCellLastRegistrationDate = () => cy.get(this.cellLastRegistrationDate);
  getCellDocType = () => cy.get(this.cellDocType);
  getCellDoc = () => cy.get(this.cellDoc);
  getCellAdminLevel2 = () => cy.get(this.cellAdminLevel2);
  getCellVillage = () => cy.get(this.cellVillage);
  getNewNoteField = () => cy.get(this.newNoteField);

  checkElementsOnPage() {
    this.getTitle().contains(this.textTitle);
    this.getTicketStatus().contains(this.textStatusNew);
    this.getTicketPriority().contains(this.textPriorityNotSet);
    this.getTicketUrgency().contains(this.textUrgencyNotSet);
    this.getTicketAssigment().contains(this.textNotAssigment);
    this.getTicketCategory().contains(this.textNoCategory);
    this.getButtonAssignToMe().should("be.visible");
    this.getTicketHouseholdID().should("be.visible");
    this.getTicketIndividualID().should("be.visible");
    this.getTicketPaymentLabel().should("be.visible");
    this.getTicketCategoryBy().should("be.visible");
    this.getDateCreation().should("be.visible");
    this.getLastModifiedDate().should("be.visible");
    this.getAdministrativeLevel().should("be.visible");
    this.getAreaVillage().should("be.visible");
    this.getLanguagesSpoken().should("be.visible");
    this.getDocumentation().should("be.visible");
    this.getTicketDescription().scrollIntoView().should("be.visible");
    this.getCreateLinkedTicket().scrollIntoView().should("be.visible");
    this.getMarkDuplicate().scrollIntoView().should("be.visible");
    this.getCellIndividualID().scrollIntoView().should("be.visible");
    this.getCellHouseholdID().scrollIntoView().should("be.visible");
    this.getCellFullName().scrollIntoView().should("be.visible");
    this.getCellGender().scrollIntoView().should("be.visible");
    this.getCellDateOfBirth().scrollIntoView().should("be.visible");
    this.getCellSimilarityScore().scrollIntoView().should("be.visible");
    this.getCellLastRegistrationDate().scrollIntoView().should("be.visible");
    this.getCellDocType().scrollIntoView().should("be.visible");
    this.getCellDoc().scrollIntoView().should("be.visible");
    this.getCellAdminLevel2().scrollIntoView().should("be.visible");
    this.getCellVillage().scrollIntoView().should("be.visible");
    this.getNewNoteField().scrollIntoView().should("be.visible");
  }
<<<<<<< HEAD

  pressBackButton() {
    this.getPageHeaderContainer().find("svg").eq(0).click();
  }
=======
>>>>>>> staging
}
