from page_object.base_components import BaseComponents


class NewTicket(BaseComponents):
    # Locators
    title = 'h5[data-cy="page-header-title"]'
    selectCategory = 'div[data-cy="select-category"]'
    issueType = 'div[data-cy="select-issueType"]'
    buttonNext = 'button[data-cy="button-submit"]'
    statusOptions = 'li[role="option"]'
    lookUpTabs = 'button[role="tab"]'
    householdTableRow = 'tr[data-cy="household-table-row"]'
    individualTableRow = 'tr[data-cy="individual-table-row"]'
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
    individualFieldName = 'div[data-cy="select-individualDataUpdateFields[0].fieldName"]'
    inputValue = 'input[data-cy="input-householdDataUpdateFields[0].fieldValue"]'
    partner = 'div[data-cy="select-partner"]'

    # Texts
    textLookUpHousehold = "LOOK UP HOUSEHOLD"
    textLookUpIndividual = "LOOK UP INDIVIDUAL"
    textTitle = "New Ticket"
    textNext = "Next"
    textCategoryDescription = {
        "Data Change":
            "A grievance that is submitted to change in the households or beneficiary status",
        "Grievance Complaint":
            "A grievance submitted to express dissatisfaction made about an individual, UNICEF/NGO/Partner/Vendor, about a received service or about the process itself",
        "Referral":
            "A grievance submitted to direct the reporting individual to another service provider/actor to provide support/help that is beyond the scope of work of UNICEF",
        "Sensitive Grievance":
            "A grievance that shall be treated with sensitivity or which individual wishes to submit anonymously",
    }

    textIssueTypeDescription = {
        "Add Individual":
            "A grievance submitted to specifically change in the households to add an individual",
        "Household Data Update":
            "A grievance submitted to change in the household data (Address, number of individuals, etc.)",
        "Individual Data Update":
            "A grievance submitted to change in the household’s individuals data (Family name, full name, birth date, etc.)",
        "Withdraw Individual":
            "A grievance submitted to remove an individual from within a household",
        "Withdraw Household": "A grievance submitted to remove a household",
        "Payment Related Complaint":
            "A grievance submitted to complain about payments",
        "FSP Related Complaint":
            "A grievance to report dissatisfaction on service provided by a Financial Service Providers",
        "Registration Related Complaint":
            "A grievance submitted on issues/difficulties encountered during the registration of beneficiaries",
        "Other Complaint":
            "Other complaints that do not fall into specific predefined categories",
        "Partner Related Complaint":
            "A grievance submitted on issues encountered by an implementing partner",
        "Bribery, corruption or kickback":
            "Grievance on illicit payments or favors in exchange for personal gain",
        "Data breach":
            "Grievance on unauthorized access or disclosure of beneficiary data",
        "Conflict of interest":
            "Grievance on deception or falsification for personal gain",
        "Fraud and forgery":
            "Grievance related to identity theft or impersonation to benefit from someone’s entitlements",
        "Fraud involving misuse of programme funds by third party":
            "Grievance on forgery actions undertaken by third parties’ individuals",
        "Gross mismanagement":
            "Grievance on mismanagement leading to significant negative impact",
        "Harassment and abuse of authority":
            "Grievance related to intimidation, mistreatment, or abuse by those in authority",
        "Inappropriate staff conduct":
            "Grievance related to improper behavior or actions (physical or verbal) by program staff",
        "Miscellaneous":
            "Other issues not falling into specific predefined categories",
        "Personal disputes":
            "Grievance on conflicts or disagreements between individuals",
        "Sexual harassment and sexual exploitation":
            "Grievance on unwanted advances, abuse, or exploitation of a sexual nature",
        "Unauthorized use, misuse or waste of UNICEF property or funds":
            "Grievance on improper or unauthorized handling or disposal of assets/funds",
    }

    # Elements
    def getTitle(self):
        return self.wait_for(self.title)

    def getSelectCategory(self):
        return self.wait_for(self.selectCategory)

    def getIssueType(self):
        return self.wait_for(self.issueType)

    def getButtonNext(self):
        return self.wait_for(self.buttonNext)

    def getOption(self):
        return self.wait_for(self.statusOptions)

    def getHouseholdTab(self):
        return self.wait_for(self.lookUpTabs).contains(self.textLookUpHousehold)

    def getIndividualTab(self):
        return self.wait_for(self.lookUpTabs).contains(self.textLookUpIndividual)

    def getHouseholdTableRows(self, number):
        return self.wait_for(self.householdTableRow).eq(number)

    def getIndividualTableRows(self, number):
        return self.wait_for(self.individualTableRow).eq(number)

    def getReceivedConsent(self):
        return self.wait_for(self.receivedConsent)

    def getDescription(self):
        return self.wait_for(self.description)

    def getIndividualID(self):
        return self.wait_for(self.individualID)

    def getHouseholdID(self):
        return self.wait_for(self.householdID)

    def getIssueTypeLabel(self):
        return self.wait_for(self.issueTypeLabel)

    def getCategory(self):
        return self.wait_for(self.category)

    def getComments(self):
        return self.wait_for(self.comments)

    def getWhoAnswersPhone(self):
        return self.wait_for(self.whoAnswersPhone)

    def getWhoAnswersAltPhone(self):
        return self.wait_for(self.whoAnswersAltPhone)

    def getRole(self):
        return self.wait_for(self.role)

    def getRelationship(self):
        return self.wait_for(self.relationship)

    def getPhoneNo(self):
        return self.wait_for(self.phoneNo)

    def getMiddleName(self):
        return self.wait_for(self.middleName)

    def getMaritalStatus(self):
        return self.wait_for(self.maritalStatus)

    def getPregnant(self):
        return self.wait_for(self.pregnant)

    def getDisability(self):
        return self.wait_for(self.disability)

    def getEmail(self):
        return self.wait_for(self.email)

    def getPhysicalDisability(self):
        return self.wait_for(self.physicalDisability)

    def getsSeeingDisability(self):
        return self.wait_for(self.seeingDisability)

    def getMemoryDisability(self):
        return self.wait_for(self.memoryDisability)

    def getHearingDisability(self):
        return self.wait_for(self.hearingDisability)

    def getCommsDisability(self):
        return self.wait_for(self.commsDisability)

    def getGivenName(self):
        return self.wait_for(self.givenName)

    def getGender(self):
        return self.wait_for(self.gender)

    def getFullName(self):
        return self.wait_for(self.fullName)

    def getFamilyName(self):
        return self.wait_for(self.familyName)

    def getEstimatedBirthDate(self):
        return self.wait_for(self.estimatedBirthDate)

    def getWorkStatus(self):
        return self.wait_for(self.workStatus)

    def getObservedDisability(self):
        return self.wait_for(self.observedDisability)

    def getSelfcareDisability(self):
        return self.wait_for(self.selfcareDisability)

    def getBirthDate(self):
        return self.wait_for(self.birthDate)

    def getPhoneNoAlternative(self):
        return self.wait_for(self.phoneNoAlternative)

    def getAddDocument(self):
        return self.wait_for(self.addDocument)

    def getLookUpButton(self):
        return self.wait_for(self.lookUpButton)

    def getCheckbox(self):
        return self.wait_for(self.checkbox)

    def getSelectUrgency(self):
        return self.wait_for(self.selectUrgency)

    def getSelectPriority(self):
        return self.wait_for(self.selectPriority)

    def getInputLanguage(self):
        return self.wait_for(self.inputLanguage)

    def getInputArea(self):
        return self.wait_for(self.inputArea)

    def getAdminAreaAutocomplete(self):
        return self.wait_for(self.adminAreaAutocomplete)

    def getOptionUndefined(self):
        return self.wait_for(self.optionUndefined)

    def getOptionZero(self):
        return self.wait_for(self.optionZero)

    def getOptionOne(self):
        return self.wait_for(self.optionOne)

    def getLabelCategoryDescription(self):
        return self.wait_for(self.labelCategoryDescription)

    def getLabelIssueTypeDescription(self):
        return self.wait_for(self.labelIssueTypeDescription)

    def getSelectFieldName(self):
        return self.wait_for(self.selectFieldName)

    def getInputValue(self):
        return self.wait_for(self.inputValue)

    def getIndividualFieldName(self):
        return self.wait_for(self.individualFieldName)

    def getPartner(self):
        return self.wait_for(self.partner)

    def checkElementsOnPage(self):
        self.getTitle().contains(self.textTitle)
        self.getButtonNext().contains(self.textNext)
        self.getSelectCategory().should("be.visible")

    def chooseCategory(self, category):
        self.getSelectCategory().click()
        self.getOption().contains(category).click()

    def chooseIssueType(self, issue):
        self.getIssueType().should("be.visible").click()
        self.getOption().contains(issue).click()
