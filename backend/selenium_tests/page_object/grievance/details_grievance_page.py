from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class GrievanceDetailsPage(BaseComponents):
    # Locators
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    title = 'h5[data-cy="page-header-title"]'
    buttonEdit = 'a[data-cy="button-edit"]'
    buttonSetInProgress = 'button[data-cy="button-set-to-in-progress"]'
    buttonCloseTicket = 'button[data-cy="button-close-ticket"]'
    buttonConfirm = 'button[data-cy="button-confirm"]'
    buttonAssignToMe = 'button[data-cy="button-assign-to-me"]'
    ticketStatus = 'div[data-cy="label-Status"]'
    ticketPriority = 'div[data-cy="label-Priority"]'
    ticketUrgency = 'div[data-cy="label-Urgency"]'
    ticketAssigment = 'div[data-cy="label-Assigned to"]'
    ticketCategory = 'div[data-cy="label-Category"]'
    labelIssueType = 'div[data-cy="label-Issue Type"]'
    ticketHouseholdID = 'div[data-cy="label-Household ID"]'
    ticketIndividualID = 'div[data-cy="label-Individual ID"]'
    ticketPaymentLabel = 'div[data-cy="label-Payment ID"]'
    ticketCategoryBy = 'div[data-cy="label-Created By"]'
    dateCreation = 'div[data-cy="label-Date Created"]'
    lastModifiedDate = 'div[data-cy="label-Last Modified Date"]'
    administrativeLevel = 'div[data-cy="label-Administrative Level 2"]'
    areaVillage = 'div[data-cy="label-Area / Village / Pay point"]'
    languagesSpoken = 'div[data-cy="label-Languages Spoken"]'
    documentation = 'div[data-cy="label-Documentation"]'
    ticketDescription = 'div[data-cy="label-Description"]'
    comments = 'div[data-cy="label-Comments"]'
    createLinkedTicket = 'button[data-cy="button-create-linked-ticket"]'
    markDuplicate = 'button[data-cy="button-mark-duplicate"]'
    cellIndividualID = 'th[data-cy="table-cell-individual-id"]'
    cellHouseholdID = 'th[data-cy="table-cell-household-id"]'
    cellFullName = 'th[data-cy="table-cell-full-name"]'
    cellGender = 'th[data-cy="table-cell-gender"]'
    cellDateOfBirth = 'th[data-cy="table-cell-date-of-birth"]'
    cellSimilarityScore = 'th[data-cy="table-cell-similarity-score"]'
    cellLastRegistrationDate = 'th[data-cy="table-cell-last-registration-date"]'
    cellDocType = 'th[data-cy="table-cell-doc-type"]'
    cellDoc = 'th[data-cy="table-cell-doc-number"]'
    cellAdminLevel2 = 'th[data-cy="table-cell-admin-level2"]'
    cellVillage = 'th[data-cy="table-cell-village"]'
    newNoteField = 'textarea[data-cy="input-newNote"]'
    buttonNewNote = 'button[data-cy="button-add-note"]'
    labelGENDER = 'div[data-cy="label-GENDER"]'
    labelRole = 'div[data-cy="label-role"]'
    labelPhoneNo = 'div[data-cy="label-phone no"]'
    labelPregnant = 'div[data-cy="label-pregnant"]'
    labelFullName = 'div[data-cy="label-full name"]'
    labelBirthDate = 'div[data-cy="label-birth date"]'
    labelDisability = 'div[data-cy="label-disability"]'
    labelGivenName = 'div[data-cy="label-given name"]'
    labelFamilyName = 'div[data-cy="label-family name"]'
    labelMiddleName = 'div[data-cy="label-middle name"]'
    labelWorkStatus = 'div[data-cy="label-work status"]'
    labelRelationship = 'div[data-cy="label-relationship"]'
    labelMaritalStatus = 'div[data-cy="label-marital status"]'
    labelCommsDisability = 'div[data-cy="label-comms disability"]'
    labelCommsDisability1 = 'div[data-cy="label-comms disability"]'
    labelSeeingDisability = 'div[data-cy="label-seeing disability"]'
    labelWhoAnswersPhone = 'div[data-cy="label-who answers phone"]'
    labelHearingDisability = 'div[data-cy="label-hearing disability"]'
    labelObservedDisability = 'div[data-cy="label-observed disability"]'
    labelPhysicalDisability = 'div[data-cy="label-physical disability"]'
    labelSelfcareDisability = 'div[data-cy="label-selfcare disability"]'
    labelEstimatedBirthDate = 'div[data-cy="label-estimated birth date"]'
    labelPhoneNoAlternative = 'div[data-cy="label-phone no alternative"]'
    labelWhoAnswersAltPhone = 'div[data-cy="label-who answers alt phone"]'
    labelTickets = 'div[data-cy="label-Tickets"]'
    checkbox = 'tr[role="checkbox"]'
    labelPartner = 'div[data-cy="label-Partner"]'

    # Texts
    textTitle = "Ticket ID: "
    textStatusNew = "New"
    textStatusAssigned = "Assigned"
    textPriorityNotSet = "Not set"
    textPriorityMedium = "Medium"
    textPriorityLow = "Low"
    textPriorityHigh = "High"
    textUrgencyNotUrgent = "Not urgent"
    textUrgencyUrgent = "Urgent"
    textUrgencyVeryUrgent = "Very urgent"
    textUrgencyNotSet = "Not set"
    textNotAssigment = "-"
    textAssigmentRootRootkowski = "Root Rootkowski"
    textNoCategory = "Needs Adjudication"

    # Elements

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getTitle(self) -> WebElement:
        return self.wait_for(self.title)

    def getButtonAssignToMe(self) -> WebElement:
        return self.wait_for(self.buttonAssignToMe)

    def getButtonCloseTicket(self) -> WebElement:
        return self.wait_for(self.buttonCloseTicket)

    def getButtonConfirm(self) -> WebElement:
        return self.wait_for(self.buttonConfirm)

    def getTicketStatus(self) -> WebElement:
        return self.wait_for(self.ticketStatus)

    def getTicketPriority(self) -> WebElement:
        return self.wait_for(self.ticketPriority)

    def getTicketUrgency(self) -> WebElement:
        return self.wait_for(self.ticketUrgency)

    def getTicketAssigment(self) -> WebElement:
        return self.wait_for(self.ticketAssigment)

    def getTicketCategory(self) -> WebElement:
        return self.wait_for(self.ticketCategory)

    def getTicketHouseholdID(self) -> WebElement:
        return self.wait_for(self.ticketHouseholdID)

    def getTicketIndividualID(self) -> WebElement:
        return self.wait_for(self.ticketIndividualID)

    def getTicketPaymentLabel(self) -> WebElement:
        return self.wait_for(self.ticketPaymentLabel)

    def getLabelPartner(self) -> WebElement:
        return self.wait_for(self.labelPartner)

    def getTicketCategoryBy(self) -> WebElement:
        return self.wait_for(self.ticketCategoryBy)

    def getDateCreation(self) -> WebElement:
        return self.wait_for(self.dateCreation)

    def getLastModifiedDate(self) -> WebElement:
        return self.wait_for(self.lastModifiedDate)

    def getAdministrativeLevel(self) -> WebElement:
        return self.wait_for(self.administrativeLevel)

    def getAreaVillage(self) -> WebElement:
        return self.wait_for(self.areaVillage)

    def getLanguagesSpoken(self) -> WebElement:
        return self.wait_for(self.languagesSpoken)

    def getDocumentation(self) -> WebElement:
        return self.wait_for(self.documentation)

    def getTicketDescription(self) -> WebElement:
        return self.wait_for(self.ticketDescription)

    def getCreateLinkedTicket(self) -> WebElement:
        return self.wait_for(self.createLinkedTicket)

    def getMarkDuplicate(self) -> WebElement:
        return self.wait_for(self.markDuplicate)

    def getCellIndividualID(self) -> WebElement:
        return self.wait_for(self.cellIndividualID)

    def getCellHouseholdID(self) -> WebElement:
        return self.wait_for(self.cellHouseholdID)

    def getLabelIssueType(self) -> WebElement:
        return self.wait_for(self.labelIssueType)

    def getCellFullName(self) -> WebElement:
        return self.wait_for(self.cellFullName)

    def getCellGender(self) -> WebElement:
        return self.wait_for(self.cellGender)

    def getCellDateOfBirth(self) -> WebElement:
        return self.wait_for(self.cellDateOfBirth)

    def getCellSimilarityScore(self) -> WebElement:
        return self.wait_for(self.cellSimilarityScore)

    def getCellLastRegistrationDate(self) -> WebElement:
        return self.wait_for(self.cellLastRegistrationDate)

    def getCellDocType(self) -> WebElement:
        return self.wait_for(self.cellDocType)

    def getCellDoc(self) -> WebElement:
        return self.wait_for(self.cellDoc)

    def getCellAdminLevel2(self) -> WebElement:
        return self.wait_for(self.cellAdminLevel2)

    def getCellVillage(self) -> WebElement:
        return self.wait_for(self.cellVillage)

    def getNewNoteField(self) -> WebElement:
        return self.wait_for(self.newNoteField)

    def getLabelGENDER(self) -> WebElement:
        return self.wait_for(self.labelGENDER)

    def getLabelRole(self) -> WebElement:
        return self.wait_for(self.labelRole)

    def getLabelPhoneNo(self) -> WebElement:
        return self.wait_for(self.labelPhoneNo)

    def getLabelPregnant(self) -> WebElement:
        return self.wait_for(self.labelPregnant)

    def getLabelFullName(self) -> WebElement:
        return self.wait_for(self.labelFullName)

    def getLabelBirthDate(self) -> WebElement:
        return self.wait_for(self.labelBirthDate)

    def getLabelDisability(self) -> WebElement:
        return self.wait_for(self.labelDisability)

    def getLabelGivenName(self) -> WebElement:
        return self.wait_for(self.labelGivenName)

    def getLabelFamilyName(self) -> WebElement:
        return self.wait_for(self.labelFamilyName)

    def getLabelMiddleName(self) -> WebElement:
        return self.wait_for(self.labelMiddleName)

    def getLabelWorkStatus(self) -> WebElement:
        return self.wait_for(self.labelWorkStatus)

    def getLabelRelationship(self) -> WebElement:
        return self.wait_for(self.labelRelationship)

    def getLabelMaritalStatus(self) -> WebElement:
        return self.wait_for(self.labelMaritalStatus)

    def getLabelCommsDisability(self) -> WebElement:
        return self.wait_for(self.labelCommsDisability)

    def getLabelCommsDisability1(self) -> WebElement:
        return self.wait_for(self.labelCommsDisability1)

    def getLabelSeeingDisability(self) -> WebElement:
        return self.wait_for(self.labelSeeingDisability)

    def getLabelWhoAnswersPhone(self) -> WebElement:
        return self.wait_for(self.labelWhoAnswersPhone)

    def getLabelHearingDisability(self) -> WebElement:
        return self.wait_for(self.labelHearingDisability)

    def getLabelObservedDisability(self) -> WebElement:
        return self.wait_for(self.labelObservedDisability)

    def getLabelPhysicalDisability(self) -> WebElement:
        return self.wait_for(self.labelPhysicalDisability)

    def getLabelSelfcareDisability(self) -> WebElement:
        return self.wait_for(self.labelSelfcareDisability)

    def getLabelEstimatedBirthDate(self) -> WebElement:
        return self.wait_for(self.labelEstimatedBirthDate)

    def getLabelPhoneNoAlternative(self) -> WebElement:
        return self.wait_for(self.labelPhoneNoAlternative)

    def getLabelWhoAnswersAltPhone(self) -> WebElement:
        return self.wait_for(self.labelWhoAnswersAltPhone)

    def getLabelTickets(self) -> WebElement:
        return self.wait_for(self.labelTickets)

    def getCheckbox(self) -> WebElement:
        return self.wait_for(self.checkbox)
