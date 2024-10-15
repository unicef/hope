from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from tests.selenium.page_object.base_components import BaseComponents


class NewTicket(BaseComponents):
    # Locators
    title = 'h5[data-cy="page-header-title"]'
    selectCategory = 'div[data-cy="select-category"]'
    issueType = 'div[data-cy="select-issueType"]'
    buttonNext = 'button[data-cy="button-submit"]'
    statusOptions = 'li[role="option"]'
    lookUpIndividualTab = 'button[data-cy="look-up-individual"]'
    lookUpHouseholdTab = 'button[data-cy="look-up-household"]'
    householdTableRow = 'tr[data-cy="household-table-row"]'
    individualTableRow = 'tr[data-cy="individual-table-row"]'
    tableRow = '[data-cy="table-row"]'
    receivedConsent = 'span[data-cy="input-consent"]'
    individualID = 'div[data-cy="label-INDIVIDUAL ID"]'
    householdID = 'div[data-cy="label-HOUSEHOLD ID"]'
    issueTypeLabel = 'div[data-cy="label-Issue Type"]'
    category = 'div[data-cy="label-Category"]'
    description = 'textarea[data-cy="input-description"]'
    comments = 'textarea[data-cy="input-comments"]'
    whoAnswersPhone = 'input[data-cy="input-individualData.whoAnswersPhone"]'
    whoAnswersAltPhone = 'input[data-cy="input-individualData.whoAnswersAltPhone"]'
    role = 'div[data-cy="select-individualData.role"]'
    relationship = 'div[data-cy="select-individualData.relationship"]'
    phoneNo = 'input[data-cy="input-individualData.phoneNo"]'
    middleName = 'input[data-cy="input-individualData.middleName"]'
    maritalStatus = 'div[data-cy="select-individualData.maritalStatus"]'
    pregnant = 'div[data-cy="select-individualData.pregnant"]'
    disability = 'div[data-cy="select-individualData.disability"]'
    email = 'input[data-cy="input-individualData.email"]'
    physicalDisability = 'div[data-cy="select-individualData.physicalDisability"]'
    seeingDisability = 'div[data-cy="select-individualData.seeingDisability"]'
    memoryDisability = 'div[data-cy="select-individualData.memoryDisability"]'
    hearingDisability = 'div[data-cy="select-individualData.hearingDisability"]'
    commsDisability = 'div[data-cy="select-individualData.commsDisability"]'
    givenName = 'input[data-cy="input-individualData.givenName"]'
    gender = 'div[data-cy="select-individualData.sex"]'
    fullName = 'input[data-cy="input-individualData.fullName"]'
    familyName = 'input[data-cy="input-individualData.familyName"]'
    estimatedBirthDate = 'div[data-cy="select-individualData.estimatedBirthDate"]'
    workStatus = 'div[data-cy="select-individualData.workStatus"]'
    observedDisability = 'div[data-cy="select-individualData.observedDisability"]'
    selfcareDisability = 'div[data-cy="select-individualData.selfcareDisability"]'
    birthDate = 'input[data-cy="date-input-individualData.birthDate"]'
    phoneNoAlternative = 'input[data-cy="input-individualData.phoneNoAlternative"]'
    addDocument = 'button[type="button"]'
    lookUpButton = 'div[data-cy="look-up-button"]'
    checkbox = 'tr[role="checkbox"]'
    selectUrgency = 'div[data-cy="select-urgency"]'
    selectPriority = 'div[data-cy="select-priority"]'
    inputLanguage = 'textarea[data-cy="input-language"]'
    inputArea = 'input[data-cy="input-area"]'
    adminAreaAutocomplete = 'div[data-cy="admin-area-autocomplete"]'
    optionUndefined = 'li[data-cy="select-option-undefined"]'
    optionZero = 'li[data-cy="select-option-0"]'
    optionOne = 'li[data-cy="select-option-1"]'
    labelCategoryDescription = 'div[data-cy="label-Category Description"]'
    labelIssueTypeDescription = 'div[data-cy="label-Issue Type Description"]'
    selectFieldName = 'div[data-cy="select-householdDataUpdateFields[0].fieldName"]'
    individualFieldName = 'div[data-cy="select-individualDataUpdateFields[{}].fieldName"]'
    inputValue = 'input[data-cy="input-householdDataUpdateFields[0].fieldValue"]'
    partner = 'div[data-cy="select-partner"]'
    tablePagination = '[data-cy="table-pagination"]'
    inputDescription = 'textarea[data-cy="input-description"]'
    inputComments = 'textarea[data-cy="input-comments"]'
    selectProgram = 'div[data-cy="select-program"]'
    inputIndividualdataPhonenoalternative = 'input[data-cy="input-individualDataPhoneNoAlternative"]'
    datePickerFilter = 'div[data-cy="date-picker-filter"]'
    inputIndividualdataBlockchainname = 'input[data-cy="input-individualData.blockchainName"]'
    selectIndividualdataSelfcaredisability = 'div[data-cy="select-individualData.selfcareDisability"]'
    selectIndividualdataObserveddisability = 'div[data-cy="select-individualData.observedDisability"]'
    selectIndividualdataWorkstatus = 'div[data-cy="select-individualData.workStatus"]'
    selectIndividualdataEstimatedbirthdate = 'div[data-cy="select-individualData.estimatedBirthDate"]'
    inputIndividualdataFamilyname = 'input[data-cy="input-individualData.familyName"]'
    inputIndividualdataFullname = 'input[data-cy="input-individualData.fullName"]'
    selectIndividualdataSex = 'div[data-cy="select-individualData.sex"]'
    inputIndividualdataGivenname = 'input[data-cy="input-individualData.givenName"]'
    selectIndividualdataCommsdisability = 'div[data-cy="select-individualData.commsDisability"]'
    selectIndividualdataHearingdisability = 'div[data-cy="select-individualData.hearingDisability"]'
    selectIndividualdataMemorydisability = 'div[data-cy="select-individualData.memoryDisability"]'
    selectIndividualdataSeeingdisability = 'div[data-cy="select-individualData.seeingDisability"]'
    selectIndividualdataPhysicaldisability = 'div[data-cy="select-individualData.physicalDisability"]'
    inputIndividualdataEmail = 'input[data-cy="input-individualData.email"]'
    selectIndividualdataDisability = 'div[data-cy="select-individualData.disability"]'
    selectIndividualdataPregnant = 'div[data-cy="select-individualData.pregnant"]'
    selectIndividualdataMaritalstatus = 'div[data-cy="select-individualData.maritalStatus"]'
    inputIndividualdataMiddlename = 'input[data-cy="input-individualData.middleName"]'
    inputIndividualdataPaymentdeliveryphoneno = 'input[data-cy="input-individualData.paymentDeliveryPhoneNo"]'
    inputIndividualdataPhoneno = 'input[data-cy="input-individualData.phoneNo"]'
    selectIndividualdataPreferredlanguage = 'div[data-cy="select-individualData.preferredLanguage"]'
    selectIndividualdataRelationship = 'div[data-cy="select-individualData.relationship"]'
    selectIndividualdataRole = 'div[data-cy="select-individualData.role"]'
    inputIndividualdataWalletaddress = 'input[data-cy="input-individualData.walletAddress"]'
    inputIndividualdataWalletname = 'input[data-cy="input-individualData.walletName"]'
    inputIndividualdataWhoanswersaltphone = 'input[data-cy="input-individualData.whoAnswersAltPhone"]'
    inputIndividualdataWhoanswersphone = 'input[data-cy="input-individualData.whoAnswersPhone"]'
    selectHouseholddataupdatefieldsFieldname = 'div[data-cy="select-householdDataUpdateFields[{}].fieldName"]'
    buttonAddNewField = 'button[data-cy="button-add-new-field"]'
    inputIndividualData = 'div[data-cy="input-individual-data-{}"]'  # Gender
    checkboxSelectAll = 'span[data-cy="checkbox-select-all"]'
    buttonSubmit = 'button[data-cy="button-submit"]'
    linkedTicketId = 'span[data-cy="linked-ticket-id"]'
    linkedTicket = '[data-cy="linked-ticket"]'
    buttonEdit = 'svg[data-cy="button-edit"]'
    buttonDelete = 'svg[data-cy="button-delete"]'
    addDocumentation = 'button[data-cy="add-documentation"]'
    inputDocumentationName = 'input[data-cy="input-documentation[{}].name"]'
    inputFile = 'input[type="file"]'
    inputQuestionnaire_size = 'span[data-cy="input-questionnaire_size"]'
    labelHouseholdSize = 'div[data-cy="label-Household Size"]'
    inputQuestionnaire_malechildrencount = 'span[data-cy="input-questionnaire_maleChildrenCount"]'
    labelNumberOfMaleChildren = 'div[data-cy="label-Number of Male Children"]'
    inputQuestionnaire_femalechildrencount = 'span[data-cy="input-questionnaire_femaleChildrenCount"]'
    labelNumberOfFemaleChildren = 'div[data-cy="label-Number of Female Children"]'
    inputQuestionnaire_childrendisabledcount = 'span[data-cy="input-questionnaire_childrenDisabledCount"]'
    labelNumberOfDisabledChildren = 'div[data-cy="label-Number of Disabled Children"]'
    inputQuestionnaire_headofhousehold = 'span[data-cy="input-questionnaire_headOfHousehold"]'
    labelHeadOfHousehold = 'div[data-cy="label-Head of Household"]'
    inputQuestionnaire_countryorigin = 'span[data-cy="input-questionnaire_countryOrigin"]'
    labelCountryOfOrigin = 'div[data-cy="label-Country of Origin"]'
    inputQuestionnaire_address = 'span[data-cy="input-questionnaire_address"]'
    labelAddress = 'div[data-cy="label-Address"]'
    inputQuestionnaire_village = 'span[data-cy="input-questionnaire_village"]'
    labelVillage = 'div[data-cy="label-Village"]'
    inputQuestionnaire_admin1 = 'span[data-cy="input-questionnaire_admin1"]'
    labelAdministrativeLevel1 = 'div[data-cy="label-Administrative Level 1"]'
    inputQuestionnaire_admin2 = 'span[data-cy="input-questionnaire_admin2"]'
    labelAdministrativeLevel2 = 'div[data-cy="label-Administrative Level 2"]'
    inputQuestionnaire_admin3 = 'span[data-cy="input-questionnaire_admin3"]'
    labelAdministrativeLevel3 = 'div[data-cy="label-Administrative Level 3"]'
    inputQuestionnaire_admin4 = 'span[data-cy="input-questionnaire_admin4"]'
    labelAdministrativeLevel4 = 'div[data-cy="label-Administrative Level 4"]'
    inputQuestionnaire_months_displaced_h_f = 'span[data-cy="input-questionnaire_months_displaced_h_f"]'
    labelLengthOfTimeSinceArrival = 'div[data-cy="label-LENGTH OF TIME SINCE ARRIVAL"]'
    inputQuestionnaire_fullname = 'span[data-cy="input-questionnaire_fullName"]'
    labelIndividualFullName = 'div[data-cy="label-Individual Full Name"]'
    inputQuestionnaire_birthdate = 'span[data-cy="input-questionnaire_birthDate"]'
    labelBirthDate = 'div[data-cy="label-Birth Date"]'
    inputQuestionnaire_sex = 'span[data-cy="input-questionnaire_sex"]'
    labelGender = 'div[data-cy="label-Gender"]'
    inputQuestionnaire_phoneno = 'span[data-cy="input-questionnaire_phoneNo"]'
    labelPhoneNumber = 'div[data-cy="label-Phone Number"]'
    inputQuestionnaire_relationship = 'span[data-cy="input-questionnaire_relationship"]'
    labelRelationshipToHoh = 'div[data-cy="label-Relationship to HOH"]'

    # Texts
    textLookUpHousehold = "LOOK UP HOUSEHOLD"
    textLookUpIndividual = "LOOK UP INDIVIDUAL"
    textTitle = "New Ticket"
    textNext = "Next"
    textCategoryDescription = {
        "Data Change": "A grievance that is submitted to change in the households or beneficiary status",
        "Grievance Complaint": "A grievance submitted to express dissatisfaction made about an individual, UNICEF/NGO/Partner/Vendor, about a received service or about the process itself",
        "Referral": "A grievance submitted to direct the reporting individual to another service provider/actor to provide support/help that is beyond the scope of work of UNICEF",
        "Sensitive Grievance": "A grievance that shall be treated with sensitivity or which individual wishes to submit anonymously",
    }

    textIssueTypeDescription = {
        "Add Individual": "A grievance submitted to specifically change in the households to add an individual",
        "Household Data Update": "A grievance submitted to change in the household data (Address, number of individuals, etc.)",
        "Individual Data Update": "A grievance submitted to change in the household’s individuals data (Family name, full name, birth date, etc.)",
        "Withdraw Individual": "A grievance submitted to remove an individual from within a household",
        "Withdraw Household": "A grievance submitted to remove a household",
        "Payment Related Complaint": "A grievance submitted to complain about payments",
        "FSP Related Complaint": "A grievance to report dissatisfaction on service provided by a Financial Service Providers",
        "Registration Related Complaint": "A grievance submitted on issues/difficulties encountered during the registration of beneficiaries",
        "Other Complaint": "Other complaints that do not fall into specific predefined categories",
        "Partner Related Complaint": "A grievance submitted on issues encountered by an implementing partner",
        "Bribery, corruption or kickback": "Grievance on illicit payments or favors in exchange for personal gain",
        "Data breach": "Grievance on unauthorized access or disclosure of beneficiary data",
        "Conflict of interest": "Grievance on deception or falsification for personal gain",
        "Fraud and forgery": "Grievance related to identity theft or impersonation to benefit from someone’s entitlements",
        "Fraud involving misuse of programme funds by third party": "Grievance on forgery actions undertaken by third parties’ individuals",
        "Gross mismanagement": "Grievance on mismanagement leading to significant negative impact",
        "Harassment and abuse of authority": "Grievance related to intimidation, mistreatment, or abuse by those in authority",
        "Inappropriate staff conduct": "Grievance related to improper behavior or actions (physical or verbal) by program staff",
        "Miscellaneous": "Other issues not falling into specific predefined categories",
        "Personal disputes": "Grievance on conflicts or disagreements between individuals",
        "Sexual harassment and sexual exploitation": "Grievance on unwanted advances, abuse, or exploitation of a sexual nature",
        "Unauthorized use, misuse or waste of UNICEF property or funds": "Grievance on improper or unauthorized handling or disposal of assets/funds",
    }

    # Elements
    def getTitle(self) -> WebElement:
        return self.wait_for(self.title)

    def getSelectCategory(self) -> WebElement:
        return self.wait_for(self.selectCategory)

    def getIssueType(self) -> WebElement:
        return self.wait_for(self.issueType)

    def getButtonNext(self) -> WebElement:
        return self.wait_for(self.buttonNext)

    def getOption(self) -> WebElement:
        return self.wait_for(self.statusOptions)

    def getHouseholdTab(self) -> WebElement:
        return self.wait_for(self.lookUpHouseholdTab)

    def getIndividualTab(self) -> WebElement:
        return self.wait_for(self.lookUpIndividualTab)

    def getHouseholdTableRows(self, number: int) -> WebElement:
        self.wait_for(self.householdTableRow)
        return self.get_elements(self.householdTableRow)[number]

    def getIndividualTableRows(self, number: int) -> WebElement:
        self.wait_for(self.individualTableRow)
        return self.get_elements(self.individualTableRow)[number]

    def getReceivedConsent(self) -> WebElement:
        return self.wait_for(self.receivedConsent, timeout=100)

    def getDescription(self) -> WebElement:
        return self.wait_for(self.description)

    def getIndividualID(self) -> WebElement:
        return self.wait_for(self.individualID)

    def getHouseholdID(self) -> WebElement:
        return self.wait_for(self.householdID)

    def getIssueTypeLabel(self) -> WebElement:
        return self.wait_for(self.issueTypeLabel)

    def getCategory(self) -> WebElement:
        return self.wait_for(self.category)

    def getComments(self) -> WebElement:
        return self.wait_for(self.comments)

    def getWhoAnswersPhone(self) -> WebElement:
        return self.wait_for(self.whoAnswersPhone)

    def getWhoAnswersAltPhone(self) -> WebElement:
        return self.wait_for(self.whoAnswersAltPhone)

    def getRole(self) -> WebElement:
        return self.wait_for(self.role)

    def getRelationship(self) -> WebElement:
        return self.wait_for(self.relationship)

    def getPhoneNo(self) -> WebElement:
        return self.wait_for(self.phoneNo)

    def getMiddleName(self) -> WebElement:
        return self.wait_for(self.middleName)

    def getMaritalStatus(self) -> WebElement:
        return self.wait_for(self.maritalStatus)

    def getPregnant(self) -> WebElement:
        return self.wait_for(self.pregnant)

    def getDisability(self) -> WebElement:
        return self.wait_for(self.disability)

    def getEmail(self) -> WebElement:
        return self.wait_for(self.email)

    def getPhysicalDisability(self) -> WebElement:
        return self.wait_for(self.physicalDisability)

    def getsSeeingDisability(self) -> WebElement:
        return self.wait_for(self.seeingDisability)

    def getMemoryDisability(self) -> WebElement:
        return self.wait_for(self.memoryDisability)

    def getHearingDisability(self) -> WebElement:
        return self.wait_for(self.hearingDisability)

    def getCommsDisability(self) -> WebElement:
        return self.wait_for(self.commsDisability)

    def getGivenName(self) -> WebElement:
        return self.wait_for(self.givenName)

    def getGender(self) -> WebElement:
        return self.wait_for(self.gender)

    def getFullName(self) -> WebElement:
        return self.wait_for(self.fullName)

    def getFamilyName(self) -> WebElement:
        return self.wait_for(self.familyName)

    def getEstimatedBirthDate(self) -> WebElement:
        return self.wait_for(self.estimatedBirthDate)

    def getWorkStatus(self) -> WebElement:
        return self.wait_for(self.workStatus)

    def getObservedDisability(self) -> WebElement:
        return self.wait_for(self.observedDisability)

    def getSelfcareDisability(self) -> WebElement:
        return self.wait_for(self.selfcareDisability)

    def getBirthDate(self) -> WebElement:
        return self.wait_for(self.birthDate)

    def getPhoneNoAlternative(self) -> WebElement:
        return self.wait_for(self.phoneNoAlternative)

    def getAddDocument(self) -> WebElement:
        return self.wait_for(self.addDocument)

    def getLookUpButton(self) -> WebElement:
        return self.wait_for(self.lookUpButton)

    def getLookUpPaymentRecord(self) -> [WebElement]:
        return self.get_elements(self.lookUpButton)[1]

    def getCheckbox(self) -> WebElement:
        return self.wait_for(self.checkbox)

    def getSelectUrgency(self) -> WebElement:
        return self.wait_for(self.selectUrgency)

    def getSelectPriority(self) -> WebElement:
        return self.wait_for(self.selectPriority)

    def getInputLanguage(self) -> WebElement:
        return self.wait_for(self.inputLanguage)

    def getInputArea(self) -> WebElement:
        return self.wait_for(self.inputArea)

    def getAdminAreaAutocomplete(self) -> WebElement:
        return self.wait_for(self.adminAreaAutocomplete)

    def getOptionUndefined(self) -> WebElement:
        return self.wait_for(self.optionUndefined)

    def getOptionZero(self) -> WebElement:
        return self.wait_for(self.optionZero)

    def getOptionOne(self) -> WebElement:
        return self.wait_for(self.optionOne)

    def getLabelCategoryDescription(self) -> WebElement:
        return self.wait_for(self.labelCategoryDescription)

    def getLabelIssueTypeDescription(self) -> WebElement:
        return self.wait_for(self.labelIssueTypeDescription)

    def getSelectFieldName(self) -> WebElement:
        return self.wait_for(self.selectFieldName)

    def getInputValue(self) -> WebElement:
        return self.wait_for(self.inputValue)

    def getIndividualFieldName(self, index: int) -> WebElement:
        return self.wait_for(self.individualFieldName.format(str(index)))

    def getPartner(self) -> WebElement:
        return self.wait_for(self.partner)

    def getTablePagination(self) -> WebElement:
        return self.wait_for(self.tablePagination)

    def getTableRow(self) -> WebElement:
        return self.wait_for(self.tableRow)

    def waitForNoResults(self) -> bool:
        for _ in range(15):
            if "No results" in self.getTableRow().text:
                return True
            sleep(1)
        return False

    def getSelectProgram(self) -> WebElement:
        return self.wait_for(self.selectProgram)

    def getInputIndividualdataPhonenoalternative(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataPhonenoalternative)

    def getDatePickerFilter(self) -> WebElement:
        return self.wait_for(self.datePickerFilter).find_element("tag name", "input")

    def getInputIndividualdataBlockchainname(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataBlockchainname)

    def getSelectIndividualdataSelfcaredisability(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataSelfcaredisability)

    def getSelectIndividualdataObserveddisability(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataObserveddisability)

    def getSelectIndividualdataWorkstatus(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataWorkstatus)

    def getSelectIndividualdataEstimatedbirthdate(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataEstimatedbirthdate)

    def getInputIndividualdataFamilyname(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataFamilyname)

    def getInputIndividualdataFullname(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataFullname)

    def getSelectIndividualdataSex(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataSex)

    def getInputIndividualdataGivenname(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataGivenname)

    def getSelectIndividualdataCommsdisability(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataCommsdisability)

    def getSelectIndividualdataHearingdisability(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataHearingdisability)

    def getSelectIndividualdataMemorydisability(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataMemorydisability)

    def getSelectIndividualdataSeeingdisability(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataSeeingdisability)

    def getSelectIndividualdataPhysicaldisability(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataPhysicaldisability)

    def getInputIndividualdataEmail(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataEmail)

    def getSelectIndividualdataDisability(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataDisability)

    def getSelectIndividualdataPregnant(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataPregnant)

    def getSelectIndividualdataMaritalstatus(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataMaritalstatus)

    def getInputIndividualdataMiddlename(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataMiddlename)

    def getInputIndividualdataPaymentdeliveryphoneno(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataPaymentdeliveryphoneno)

    def getInputIndividualdataPhoneno(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataPhoneno)

    def getSelectIndividualdataPreferredlanguage(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataPreferredlanguage)

    def getSelectIndividualdataRelationship(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataRelationship)

    def getSelectIndividualdataRole(self) -> WebElement:
        return self.wait_for(self.selectIndividualdataRole)

    def getInputIndividualdataWalletaddress(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataWalletaddress)

    def getInputIndividualdataWalletname(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataWalletname)

    def getInputIndividualdataWhoanswersaltphone(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataWhoanswersaltphone)

    def getInputIndividualdataWhoanswersphone(self) -> WebElement:
        return self.wait_for(self.inputIndividualdataWhoanswersphone)

    def getButtonAddNewField(self) -> WebElement:
        return self.wait_for(self.buttonAddNewField)

    def getSelectHouseholddataupdatefieldsFieldname(self, index: int) -> WebElement:
        field = self.wait_for(self.selectHouseholddataupdatefieldsFieldname.format(index))
        return field.find_element(By.XPATH, "./..")

    def getInputIndividualData(self, type: str) -> WebElement:
        return self.wait_for(self.inputIndividualData.format(type))

    def getCheckboxSelectAll(self) -> WebElement:
        return self.wait_for(self.checkboxSelectAll)

    def getButtonSubmit(self) -> WebElement:
        return self.get_elements(self.buttonSubmit)[1]

    def getLinkedTicketId(self) -> WebElement:
        return self.wait_for(self.linkedTicketId)

    def getLinkedTicket(self) -> WebElement:
        return self.wait_for(self.linkedTicket)

    def getButtonEdit(self) -> WebElement:
        return self.wait_for(self.buttonEdit)

    def getButtonDelete(self) -> WebElement:
        return self.wait_for(self.buttonDelete)

    def getAddDocumentation(self) -> WebElement:
        return self.wait_for(self.addDocumentation)

    def getInputDocumentationName(self, index: int) -> WebElement:
        return self.wait_for(self.inputDocumentationName.format(index))

    def getInputFile(self) -> WebElement:
        return self.wait_for(self.inputFile)

    def getInputQuestionnaire_size(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_size)

    def getLabelHouseholdSize(self) -> WebElement:
        return self.wait_for(self.labelHouseholdSize)

    def getInputQuestionnaire_malechildrencount(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_malechildrencount)

    def getLabelNumberOfMaleChildren(self) -> WebElement:
        return self.wait_for(self.labelNumberOfMaleChildren)

    def getInputQuestionnaire_femalechildrencount(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_femalechildrencount)

    def getLabelNumberOfFemaleChildren(self) -> WebElement:
        return self.wait_for(self.labelNumberOfFemaleChildren)

    def getInputQuestionnaire_childrendisabledcount(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_childrendisabledcount)

    def getLabelNumberOfDisabledChildren(self) -> WebElement:
        return self.wait_for(self.labelNumberOfDisabledChildren)

    def getInputQuestionnaire_headofhousehold(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_headofhousehold)

    def getLabelHeadOfHousehold(self) -> WebElement:
        return self.wait_for(self.labelHeadOfHousehold)

    def getInputQuestionnaire_countryorigin(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_countryorigin)

    def getLabelCountryOfOrigin(self) -> WebElement:
        return self.wait_for(self.labelCountryOfOrigin)

    def getInputQuestionnaire_address(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_address)

    def getLabelAddress(self) -> WebElement:
        return self.wait_for(self.labelAddress)

    def getInputQuestionnaire_village(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_village)

    def getLabelVillage(self) -> WebElement:
        return self.wait_for(self.labelVillage)

    def getInputQuestionnaire_admin1(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_admin1)

    def getLabelAdministrativeLevel1(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel1)

    def getInputQuestionnaire_admin2(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_admin2)

    def getLabelAdministrativeLevel2(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel2)

    def getInputQuestionnaire_admin3(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_admin3)

    def getLabelAdministrativeLevel3(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel3)

    def getInputQuestionnaire_admin4(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_admin4)

    def getLabelAdministrativeLevel4(self) -> WebElement:
        return self.wait_for(self.labelAdministrativeLevel4)

    def getInputQuestionnaire_months_displaced_h_f(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_months_displaced_h_f)

    def getLabelLengthOfTimeSinceArrival(self) -> WebElement:
        return self.wait_for(self.labelLengthOfTimeSinceArrival)

    def getInputQuestionnaire_fullname(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_fullname)

    def getLabelIndividualFullName(self) -> WebElement:
        return self.wait_for(self.labelIndividualFullName)

    def getInputQuestionnaire_birthdate(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_birthdate)

    def getLabelBirthDate(self) -> WebElement:
        return self.wait_for(self.labelBirthDate)

    def getInputQuestionnaire_sex(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_sex)

    def getLabelGender(self) -> WebElement:
        return self.wait_for(self.labelGender)

    def getInputQuestionnaire_phoneno(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_phoneno)

    def getLabelPhoneNumber(self) -> WebElement:
        return self.wait_for(self.labelPhoneNumber)

    def getInputQuestionnaire_relationship(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_relationship)

    def getLabelRelationshipToHoh(self) -> WebElement:
        return self.wait_for(self.labelRelationshipToHoh)
