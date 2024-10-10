from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.page_object.base_components import BaseComponents


class GrievanceDetailsPage(BaseComponents):
    # Locators
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    title = 'h5[data-cy="page-header-title"]'
    buttonEdit = 'a[data-cy="button-edit"]'
    buttonSetInProgress = 'button[data-cy="button-set-to-in-progress"]'
    buttonSendBack = 'button[data-cy="button-send-back"]'
    buttonCloseTicket = 'button[data-cy="button-close-ticket"]'
    buttonConfirm = 'button[data-cy="button-confirm"]'
    buttonAssignToMe = 'button[data-cy="button-assign-to-me"]'
    buttonSendForApproval = 'button[data-cy="button-send-for-approval"]'
    buttonApproval = 'button[data-cy="button-approve"]'
    ticketStatus = 'div[data-cy="label-Status"]'
    ticketPriority = 'div[data-cy="label-Priority"]'
    ticketUrgency = 'div[data-cy="label-Urgency"]'
    ticketAssigment = 'div[data-cy="label-Assigned to"]'
    ticketCategory = 'div[data-cy="label-Category"]'
    labelIssueType = 'div[data-cy="label-Issue Type"]'
    ticketHouseholdID = 'div[data-cy="label-Household ID"]'
    ticketIndividualID = 'div[data-cy="label-Individual ID"]'
    ticketPaymentLabel = 'div[data-cy="label-Payment ID"]'
    labelPaymentPlan = 'div[data-cy="label-Payment Plan"]'
    labelPaymentPlanVerification = 'div[data-cy="label-Payment Plan Verification"]'
    labelProgramme = 'div[data-cy="label-Programme"]'
    ticketCategoryBy = 'div[data-cy="label-Created By"]'
    dateCreation = 'div[data-cy="label-Date Created"]'
    lastModifiedDate = 'div[data-cy="label-Last Modified Date"]'
    administrativeLevel = 'div[data-cy="label-Administrative Level 2"]'
    areaVillage = 'div[data-cy="label-Area / Village / Pay point"]'
    languagesSpoken = 'div[data-cy="label-Languages Spoken"]'
    documentation = 'div[data-cy="label-Documentation"]'
    ticketDescription = 'div[data-cy="label-Description"]'
    labelCreatedBy = 'div[data-cy="label-Created By"]'
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
    labelLanguagesSpoken = 'div[data-cy="label-Languages Spoken"]'
    labelDocumentation = 'div[data-cy="label-Documentation"]'
    labelDescription = 'div[data-cy="label-Description"]'
    noteRow = '[data-cy="note-row"]'
    noteName = '[data-cy="note-name"]'
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
    labelAdministrativeLevel2 = 'div[data-cy="label-Administrative Level 2"]'
    checkboxHouseholdData = 'span[data-cy="checkbox-household-data"]'
    checkboxApprove = '//*[contains(@data, "checkbox")]'
    checkboxIndividualData = 'span[data-cy="checkbox-requested-data-change"]'
    checkboxRequestedDataChange = 'span[data-cy="checkbox-requested-data-change"]'
    approveBoxNeedsAdjudicationTitle = 'h6[data-cy="approve-box-needs-adjudication-title"]'
    buttonCreateLinkedTicket = 'button[data-cy="button-create-linked-ticket"]'
    buttonMarkDistinct = 'button[data-cy="button-mark-distinct"]'
    buttonMarkDuplicate = 'button[data-cy="button-mark-duplicate"]'
    buttonClear = 'button[data-cy="button-clear"]'
    selectAllCheckbox = 'span[data-cy="select-all-checkbox"]'
    tableCellUniqueness = 'th[data-cy="table-cell-uniqueness"]'
    tableCellIndividualId = 'th[data-cy="table-cell-individual-id"]'
    tableCellHouseholdId = 'th[data-cy="table-cell-household-id"]'
    tableCellFullName = 'th[data-cy="table-cell-full-name"]'
    tableCellGender = 'th[data-cy="table-cell-gender"]'
    tableCellDateOfBirth = 'th[data-cy="table-cell-date-of-birth"]'
    tableCellSimilarityScore = 'th[data-cy="table-cell-similarity-score"]'
    tableCellLastRegistrationDate = 'th[data-cy="table-cell-last-registration-date"]'
    tableCellDocType = 'th[data-cy="table-cell-doc-type"]'
    tableCellDocNumber = 'th[data-cy="table-cell-doc-number"]'
    tableCellAdminLevel2 = 'th[data-cy="table-cell-admin-level2"]'
    tableCellVillage = 'th[data-cy="table-cell-village"]'
    checkboxIndividual = 'span[data-cy="checkbox-individual"]'
    uniquenessCell = 'td[data-cy="uniqueness-cell"]'
    distinctTooltip = 'svg[data-cy="distinct-tooltip"]'
    individualIdCell = 'td[data-cy="individual-id-cell"]'
    individualId = 'span[data-cy="individual-id"]'
    householdIdCell = 'td[data-cy="household-id-cell"]'
    householdId = 'span[data-cy="household-id"]'
    fullNameCell = 'td[data-cy="full-name-cell"]'
    genderCell = 'td[data-cy="gender-cell"]'
    birthDateCell = 'td[data-cy="birth-date-cell"]'
    similarityScoreCell = 'td[data-cy="similarity-score-cell"]'
    lastRegistrationDateCell = 'td[data-cy="last-registration-date-cell"]'
    docTypeCell = 'td[data-cy="doc-type-cell"]'
    docNumberCell = 'td[data-cy="doc-number-cell"]'
    adminLevel2Cell = 'td[data-cy="admin-level2-cell"]'
    villageCell = 'td[data-cy="village-cell"]'
    checkboxCell = 'td[data-cy="checkbox-cell"]'
    selectCheckbox = 'span[data-cy="select-checkbox"]'
    statusCell = 'td[data-cy="status-cell"]'
    sexCell = 'td[data-cy="sex-cell"]'
    similarityCell = 'td[data-cy="similarity-cell"]'
    documentTypeCell = 'td[data-cy="document-type-cell"]'
    documentNumberCell = 'td[data-cy="document-number-cell"]'
    admin2NameCell = 'td[data-cy="admin2-name-cell"]'
    duplicateTooltip = 'svg[data-cy="duplicate-tooltip"]'
    inputNewnote = 'textarea[data-cy="input-newNote"]'
    buttonAddNote = 'button[data-cy="button-add-note"]'
    activityLogContainer = 'div[data-cy="activity-log-container"]'
    activityLogTitle = 'h6[data-cy="activity-log-title"]'
    expandCollapseButton = 'button[data-cy="expand-collapse-button"]'
    activityLogTable = 'div[data-cy="activity-log-table"]'
    headingCellTimestamp = 'div[data-cy="heading-cell-timestamp"]'
    headingCellActor = 'div[data-cy="heading-cell-actor"]'
    headingCellAction = 'div[data-cy="heading-cell-action"]'
    headingCellChange_from = 'div[data-cy="heading-cell-change_from"]'
    headingCellChange_to = 'div[data-cy="heading-cell-change_to"]'
    pagination = 'div[data-cy="pagination"]'
    buttonAdmin = 'div[data-cy="button-admin"]'
    logRow = 'div[data-cy="log-row"]'
    paymentRecord = 'span[data-cy="payment-record"]'
    labelGender = 'div[data-cy="label-GENDER"]'

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
    possibleDuplicateRowTemplate = 'tr[data-cy="possible-duplicate-row-{}"]'
    peopleIcon = 'svg[data-cy="people-icon"]'
    personIcon = 'svg[data-cy="person-icon"]'
    buttonRotateImage = 'button[data-cy="button-rotate-image"]'
    buttonCancel = 'button[data-cy="button-cancel"]'
    linkShowPhoto = 'a[data-cy="link-show-photo"]'

    def getLabelGender(self) -> WebElement:
        return self.wait_for(self.labelGender)

    def getPersonIcon(self) -> WebElement:
        return self.wait_for(self.personIcon)

    def getLabelAdministrativeLevel2(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel2)

    def getPeopleIcon(self) -> WebElement:
        return self.wait_for(self.peopleIcon)

    def disappearPeopleIcon(self) -> WebElement:
        return self.wait_for_disappear(self.peopleIcon)

    def disappearPersonIcon(self) -> WebElement:
        return self.wait_for_disappear(self.peopleIcon)

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getTitle(self) -> WebElement:
        return self.wait_for(self.title)

    def getButtonCloseTicket(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.wait_for(self.buttonCloseTicket)

    def getButtonAssignToMe(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.wait_for(self.buttonAssignToMe)

    def getButtonSendForApproval(self) -> WebElement:
        return self.wait_for(self.buttonSendForApproval)

    def getButtonApproval(self) -> WebElement:
        return self.wait_for(self.buttonApproval)

    def getButtonSetInProgress(self) -> WebElement:
        return self.wait_for(self.buttonSetInProgress)

    def getButtonSendBack(self) -> WebElement:
        return self.wait_for(self.buttonSendBack)

    def getButtonConfirm(self) -> WebElement:
        return self.wait_for(self.buttonConfirm)

    def disappearButtonConfirm(self) -> WebElement:
        return self.wait_for_disappear(self.buttonConfirm)
    
    def disappearButtonCloseTicket(self) -> WebElement:
        return self.wait_for_disappear(self.buttonCloseTicket)

    def getButtonEdit(self) -> WebElement:
        return self.wait_for(self.buttonEdit)

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

    def getLabelPaymentPlan(self) -> WebElement:
        return self.wait_for(self.labelPaymentPlan)

    def getLabelPaymentPlanVerification(self) -> WebElement:
        return self.wait_for(self.labelPaymentPlanVerification)

    def getLabelProgramme(self) -> WebElement:
        return self.wait_for(self.labelProgramme)

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

    def getLabelLastModifiedDate(self) -> WebElement:
        return self.wait_for(self.lastModifiedDate)

    def getAreaVillage(self) -> WebElement:
        return self.wait_for(self.areaVillage)

    def getLanguagesSpoken(self) -> WebElement:
        return self.wait_for(self.languagesSpoken)

    def getDocumentation(self) -> WebElement:
        return self.wait_for(self.documentation)

    def getTicketDescription(self) -> WebElement:
        return self.wait_for(self.ticketDescription)

    def getLabelCreatedBy(self) -> WebElement:
        return self.wait_for(self.labelCreatedBy)

    def getLabelDateCreation(self) -> WebElement:
        return self.wait_for(self.dateCreation)

    def getLabelComments(self) -> WebElement:
        return self.wait_for(self.comments)

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

    def getButtonNewNote(self) -> WebElement:
        return self.wait_for(self.buttonNewNote)

    def getNoteRows(self) -> [WebElement]:
        self.wait_for(self.noteRow)
        return self.get_elements(self.noteRow)

    def getLabelLanguagesSpoken(self) -> WebElement:
        return self.wait_for(self.labelLanguagesSpoken)

    def getLabelDocumentation(self) -> WebElement:
        return self.wait_for(self.labelDocumentation)

    def getLabelDescription(self) -> WebElement:
        return self.wait_for(self.labelDescription)

    def getNoteName(self) -> WebElement:
        return self.wait_for(self.noteName)

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

    def getApproveBoxNeedsAdjudicationTitle(self) -> WebElement:
        return self.wait_for(self.approveBoxNeedsAdjudicationTitle)

    def getCheckboxHouseholdData(self) -> WebElement:
        return self.wait_for(self.checkboxHouseholdData)

    def getCheckboxApprove(self) -> [WebElement]:
        self.wait_for(self.checkboxApprove, By.XPATH)
        return self.get_elements(self.checkboxApprove, By.XPATH)

    def getCheckboxIndividualData(self) -> WebElement:
        return self.wait_for(self.checkboxIndividualData)

    def getCheckboxRequestedDataChange(self) -> [WebElement]:
        self.wait_for(self.checkboxRequestedDataChange)
        return self.get_elements(self.checkboxRequestedDataChange)

    def getButtonCreateLinkedTicket(self) -> WebElement:
        return self.wait_for(self.buttonCreateLinkedTicket)

    def getButtonMarkDistinct(self) -> WebElement:
        return self.wait_for(self.buttonMarkDistinct)

    def getButtonMarkDuplicate(self) -> WebElement:
        return self.wait_for(self.buttonMarkDuplicate)

    def getButtonClear(self) -> WebElement:
        return self.wait_for(self.buttonClear)

    def getSelectAllCheckbox(self) -> WebElement:
        return self.wait_for(self.selectAllCheckbox)

    def getTableCellUniqueness(self) -> WebElement:
        return self.wait_for(self.tableCellUniqueness)

    def getTableCellIndividualId(self) -> WebElement:
        return self.wait_for(self.tableCellIndividualId)

    def getTableCellHouseholdId(self) -> WebElement:
        return self.wait_for(self.tableCellHouseholdId)

    def getTableCellFullName(self) -> WebElement:
        return self.wait_for(self.tableCellFullName)

    def getTableCellGender(self) -> WebElement:
        return self.wait_for(self.tableCellGender)

    def getTableCellDateOfBirth(self) -> WebElement:
        return self.wait_for(self.tableCellDateOfBirth)

    def getTableCellSimilarityScore(self) -> WebElement:
        return self.wait_for(self.tableCellSimilarityScore)

    def getTableCellLastRegistrationDate(self) -> WebElement:
        return self.wait_for(self.tableCellLastRegistrationDate)

    def getTableCellDocType(self) -> WebElement:
        return self.wait_for(self.tableCellDocType)

    def getTableCellDocNumber(self) -> WebElement:
        return self.wait_for(self.tableCellDocNumber)

    def getTableCellAdminLevel2(self) -> WebElement:
        return self.wait_for(self.tableCellAdminLevel2)

    def getTableCellVillage(self) -> WebElement:
        return self.wait_for(self.tableCellVillage)

    def getCheckboxIndividual(self) -> WebElement:
        return self.wait_for(self.checkboxIndividual)

    def getUniquenessCell(self) -> WebElement:
        return self.wait_for(self.uniquenessCell)

    def getDistinctTooltip(self) -> WebElement:
        return self.wait_for(self.distinctTooltip)

    def getIndividualIdCell(self) -> [WebElement]:
        self.wait_for(self.individualIdCell)
        return self.get_elements(self.individualIdCell)

    def getIndividualId(self) -> WebElement:
        return self.wait_for(self.individualId)

    def getHouseholdIdCell(self) -> [WebElement]:
        self.wait_for(self.householdIdCell)
        return self.get_elements(self.householdIdCell)

    def getHouseholdId(self) -> [WebElement]:
        self.wait_for(self.householdId)
        return self.get_elements(self.householdId)

    def getFullNameCell(self) -> [WebElement]:
        return self.wait_for(self.fullNameCell)

    def getGenderCell(self) -> WebElement:
        return self.wait_for(self.genderCell)

    def getBirthDateCell(self) -> [WebElement]:
        return self.wait_for(self.birthDateCell)

    def getSimilarityScoreCell(self) -> WebElement:
        return self.wait_for(self.similarityScoreCell)

    def getLastRegistrationDateCell(self) -> WebElement:
        return self.wait_for(self.lastRegistrationDateCell)

    def getDocTypeCell(self) -> WebElement:
        return self.wait_for(self.docTypeCell)

    def getDocNumberCell(self) -> WebElement:
        return self.wait_for(self.docNumberCell)

    def getAdminLevel2Cell(self) -> WebElement:
        return self.wait_for(self.adminLevel2Cell)

    def getVillageCell(self) -> [WebElement]:
        self.wait_for(self.villageCell)
        return self.get_elements(self.villageCell)

    def getPossibleDuplicateRowByUnicefId(self,unicef_id) -> WebElement:
        return self.wait_for(self.possibleDuplicateRowTemplate.format(unicef_id))

    def getCheckboxCell(self) -> [WebElement]:
        self.wait_for(self.checkboxCell)
        return self.get_elements(self.checkboxCell)

    def getSelectCheckbox(self) -> [WebElement]:
        self.wait_for(self.selectCheckbox)
        return self.get_elements(self.selectCheckbox)

    def getStatusCell(self) -> [WebElement]:
        self.wait_for(self.statusCell)
        return self.get_elements(self.statusCell)

    def getSexCell(self) -> WebElement:
        return self.wait_for(self.sexCell)

    def getSimilarityCell(self) -> WebElement:
        return self.wait_for(self.similarityCell)

    def getDocumentTypeCell(self) -> WebElement:
        return self.wait_for(self.documentTypeCell)

    def getDocumentNumberCell(self) -> WebElement:
        return self.wait_for(self.documentNumberCell)

    def getAdmin2NameCell(self) -> WebElement:
        return self.wait_for(self.admin2NameCell)

    def getDuplicateTooltip(self) -> WebElement:
        return self.wait_for(self.duplicateTooltip)

    def getInputNewnote(self) -> WebElement:
        return self.wait_for(self.inputNewnote)

    def getButtonAddNote(self) -> WebElement:
        return self.wait_for(self.buttonAddNote)

    def getActivityLogContainer(self) -> WebElement:
        return self.wait_for(self.activityLogContainer)

    def getActivityLogTitle(self) -> WebElement:
        return self.wait_for(self.activityLogTitle)

    def getExpandCollapseButton(self) -> WebElement:
        return self.wait_for(self.expandCollapseButton, timeout=120)

    def getActivityLogTable(self) -> WebElement:
        return self.wait_for(self.activityLogTable)

    def getHeadingCellTimestamp(self) -> WebElement:
        return self.wait_for(self.headingCellTimestamp)

    def getHeadingCellActor(self) -> WebElement:
        return self.wait_for(self.headingCellActor)

    def getHeadingCellAction(self) -> WebElement:
        return self.wait_for(self.headingCellAction)

    def getHeadingCellChange_from(self) -> WebElement:
        return self.wait_for(self.headingCellChange_from)

    def getHeadingCellChange_to(self) -> WebElement:
        return self.wait_for(self.headingCellChange_to)

    def getPagination(self) -> WebElement:
        return self.wait_for(self.pagination)

    def getButtonCancel(self) -> WebElement:
        return self.wait_for(self.buttonCancel)

    def getButtonAdmin(self) -> WebElement:
        return self.wait_for(self.buttonAdmin)

    def getLogRow(self) -> [WebElement]:
        self.wait_for(self.logRow)
        return self.get_elements(self.logRow)

    def getPaymentRecord(self) -> WebElement:
        return self.wait_for(self.paymentRecord)

    def getButtonRotateImage(self) -> WebElement:
        return self.wait_for(self.buttonRotateImage)

    def getLinkShowPhoto(self) -> WebElement:
        return self.wait_for(self.linkShowPhoto)
