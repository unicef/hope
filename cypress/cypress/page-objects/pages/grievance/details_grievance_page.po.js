import BaseComponent from "../../base.component";

export default class GrievanceDetailsPage extends BaseComponent {
  // Locators
  pageHeaderContainer = 'div[data-cy="page-header-container"]';
  title = 'h5[data-cy="page-header-title"]';
  buttonEdit = 'a[data-cy="button-edit"]';
  buttonSetInProgress = 'button[data-cy="button-set-to-in-progress"]';
  buttonCloseTicket = 'button[data-cy="button-close-ticket"]';
  buttonConfirm = 'button[data-cy="button-confirm"]';
  buttonAssignToMe = 'button[data-cy="button-assign-to-me"]';
  ticketStatus = 'div[data-cy="label-Status"]';
  ticketPriority = 'div[data-cy="label-Priority"]';
  ticketUrgency = 'div[data-cy="label-Urgency"]';
  ticketAssigment = 'div[data-cy="label-Assigned to"]';
  ticketCategory = 'div[data-cy="label-Category"]';
  labelIssueType = 'div[data-cy="label-Issue Type"]';
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
  labelGENDER = 'div[data-cy="label-GENDER"]';
  labelRole = 'div[data-cy="label-role"]';
  labelPhoneNo = 'div[data-cy="label-phone no"]';
  labelPregnant = 'div[data-cy="label-pregnant"]';
  labelFullName = 'div[data-cy="label-full name"]';
  labelBirthDate = 'div[data-cy="label-birth date"]';
  labelDisability = 'div[data-cy="label-disability"]';
  labelGivenName = 'div[data-cy="label-given name"]';
  labelFamilyName = 'div[data-cy="label-family name"]';
  labelMiddleName = 'div[data-cy="label-middle name"]';
  labelWorkStatus = 'div[data-cy="label-work status"]';
  labelRelationship = 'div[data-cy="label-relationship"]';
  labelMaritalStatus = 'div[data-cy="label-marital status"]';
  labelCommsDisability = 'div[data-cy="label-comms disability"]';
  labelCommsDisability1 = 'div[data-cy="label-comms disability"]';
  labelSeeingDisability = 'div[data-cy="label-seeing disability"]';
  labelWhoAnswersPhone = 'div[data-cy="label-who answers phone"]';
  labelHearingDisability = 'div[data-cy="label-hearing disability"]';
  labelObservedDisability = 'div[data-cy="label-observed disability"]';
  labelPhysicalDisability = 'div[data-cy="label-physical disability"]';
  labelSelfcareDisability = 'div[data-cy="label-selfcare disability"]';
  labelEstimatedBirthDate = 'div[data-cy="label-estimated birth date"]';
  labelPhoneNoAlternative = 'div[data-cy="label-phone no alternative"]';
  labelWhoAnswersAltPhone = 'div[data-cy="label-who answers alt phone"]';
  labelTickets = 'div[data-cy="label-Tickets"]';
  checkbox = 'tr[role="checkbox"]';
  labelPartner = 'div[data-cy="label-Partner"]';

  // Texts
  textTitle = "Ticket ID: ";
  textStatusNew = "New";
  textStatusAssigned = "Assigned";
  textPriorityNotSet = "Not set";
  textPriorityMedium = "Medium";
  textPriorityLow = "Low";
  textPriorityHigh = "High";
  textUrgencyNotUrgent = "Not urgent";
  textUrgencyUrgent = "Urgent";
  textUrgencyVeryUrgent = "Very urgent";
  textUrgencyNotSet = "Not set";
  textNotAssigment = "-";
  textAssigmentRootRootkowski = "Root Rootkowski";
  textNoCategory = "Needs Adjudication";
  // Elements
  getPageHeaderContainer = () => cy.get(this.pageHeaderContainer);
  getTitle = () => cy.get(this.title);
  getButtonAssignToMe = () => cy.get(this.buttonAssignToMe);
  getButtonCloseTicket = () => cy.get(this.buttonCloseTicket);
  getButtonConfirm = () => cy.get(this.buttonConfirm);
  getTicketStatus = () => cy.get(this.ticketStatus);
  getTicketPriority = () => cy.get(this.ticketPriority);
  getTicketUrgency = () => cy.get(this.ticketUrgency);
  getTicketAssigment = () => cy.get(this.ticketAssigment);
  getTicketCategory = () => cy.get(this.ticketCategory);
  getTicketHouseholdID = () => cy.get(this.ticketHouseholdID);
  getTicketIndividualID = () => cy.get(this.ticketIndividualID);
  getTicketPaymentLabel = () => cy.get(this.ticketPaymentLabel);
  getLabelPartner = () => cy.get(this.labelPartner);
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
  getLabelIssueType = () => cy.get(this.labelIssueType);
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
  getLabelGENDER = () => cy.get(this.labelGENDER);
  getLabelRole = () => cy.get(this.labelRole);
  getLabelPhoneNo = () => cy.get(this.labelPhoneNo);
  getLabelPregnant = () => cy.get(this.labelPregnant);
  getLabelFullName = () => cy.get(this.labelFullName);
  getLabelBirthDate = () => cy.get(this.labelBirthDate);
  getLabelDisability = () => cy.get(this.labelDisability);
  getLabelGivenName = () => cy.get(this.labelGivenName);
  getLabelFamilyName = () => cy.get(this.labelFamilyName);
  getLabelMiddleName = () => cy.get(this.labelMiddleName);
  getLabelWorkStatus = () => cy.get(this.labelWorkStatus);
  getLabelRelationship = () => cy.get(this.labelRelationship);
  getLabelMaritalStatus = () => cy.get(this.labelMaritalStatus);
  getLabelCommsDisability = () => cy.get(this.labelCommsDisability);
  getLabelCommsDisability1 = () => cy.get(this.labelCommsDisability1);
  getLabelSeeingDisability = () => cy.get(this.labelSeeingDisability);
  getLabelWhoAnswersPhone = () => cy.get(this.labelWhoAnswersPhone);
  getLabelHearingDisability = () => cy.get(this.labelHearingDisability);
  getLabelObservedDisability = () => cy.get(this.labelObservedDisability);
  getLabelPhysicalDisability = () => cy.get(this.labelPhysicalDisability);
  getLabelSelfcareDisability = () => cy.get(this.labelSelfcareDisability);
  getLabelEstimatedBirthDate = () => cy.get(this.labelEstimatedBirthDate);
  getLabelPhoneNoAlternative = () => cy.get(this.labelPhoneNoAlternative);
  getLabelWhoAnswersAltPhone = () => cy.get(this.labelWhoAnswersAltPhone);
  getLabelTickets = () => cy.get(this.labelTickets);
  getCheckbox = () => cy.get(this.checkbox);

  checkElementsOnPage(
    status = this.textStatusNew,
    priority = this.textPriorityNotSet,
    urgency = this.textUrgencyNotSet,
    assigment = this.textNotAssigment,
    category = this.textNoCategory
  ) {
    this.getTitle().contains(this.textTitle);
    this.getTicketStatus().contains(status);
    this.getTicketPriority().contains(priority);
    this.getTicketUrgency().contains(urgency);
    this.getTicketAssigment().contains(assigment);
    this.getTicketCategory().contains(category);
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
  }

  checkElementsCells() {
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

  pressBackButton() {
    this.getPageHeaderContainer().find("svg").eq(0).click();
  }
}
