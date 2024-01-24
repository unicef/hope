from page_object.base_components import BaseComponents


class NewTicket extends BaseComponent {
  // Locators
  title = 'h5[data-cy="page-header-title"]';
  selectCategory = 'div[data-cy="select-category"]';
  issueType = 'div[data-cy="select-issueType"]';
  buttonNext = 'button[data-cy="button-submit"]';
  statusOptions = 'li[role="option"]';
  lookUpTabs = 'button[role="tab"]';
  householdTableRow = 'tr[data-cy="household-table-row"]';
  individualTableRow = 'tr[data-cy="individual-table-row"]';
  receivedConsent = 'span[data-cy="input-consent"]';
  individualID = 'div[data-cy="label-INDIVIDUAL ID"]';
  householdID = 'div[data-cy="label-HOUSEHOLD ID"]';
  issueTypeLabel = 'div[data-cy="label-Issue Type"]';
  category = 'div[data-cy="label-Category"]';
  description = 'textarea[data-cy="input-description"]';
  comments = 'textarea[data-cy="input-comments"]';
  whoAnswersPhone = 'input[data-cy="input-individualData.whoAnswersPhone"]';
  whoAnswersAltPhone =
    'input[data-cy="input-individualData.whoAnswersAltPhone"]';
  role = 'div[data-cy="select-individualData.role"]';
  relationship = 'div[data-cy="select-individualData.relationship"]';
  phoneNo = 'input[data-cy="input-individualData.phoneNo"]';
  middleName = 'input[data-cy="input-individualData.middleName"]';
  maritalStatus = 'div[data-cy="select-individualData.maritalStatus"]';
  pregnant = 'div[data-cy="select-individualData.pregnant"]';
  disability = 'div[data-cy="select-individualData.disability"]';
  email = 'input[data-cy="input-individualData.email"]';
  physicalDisability =
    'div[data-cy="select-individualData.physicalDisability"]';
  seeingDisability = 'div[data-cy="select-individualData.seeingDisability"]';
  memoryDisability = 'div[data-cy="select-individualData.memoryDisability"]';
  hearingDisability = 'div[data-cy="select-individualData.hearingDisability"]';
  commsDisability = 'div[data-cy="select-individualData.commsDisability"]';
  givenName = 'input[data-cy="input-individualData.givenName"]';
  gender = 'div[data-cy="select-individualData.sex"]';
  fullName = 'input[data-cy="input-individualData.fullName"]';
  familyName = 'input[data-cy="input-individualData.familyName"]';
  estimatedBirthDate =
    'div[data-cy="select-individualData.estimatedBirthDate"]';
  workStatus = 'div[data-cy="select-individualData.workStatus"]';
  observedDisability =
    'div[data-cy="select-individualData.observedDisability"]';
  selfcareDisability =
    'div[data-cy="select-individualData.selfcareDisability"]';
  birthDate = 'input[data-cy="date-input-individualData.birthDate"]';
  phoneNoAlternative =
    'input[data-cy="input-individualData.phoneNoAlternative"]';
  addDocument = 'button[type="button"]';
  lookUpButton = 'div[data-cy="look-up-button"]';
  checkbox = 'tr[role="checkbox"]';
  selectUrgency = 'div[data-cy="select-urgency"]';
  selectPriority = 'div[data-cy="select-priority"]';
  inputLanguage = 'textarea[data-cy="input-language"]';
  inputArea = 'input[data-cy="input-area"]';
  adminAreaAutocomplete = 'div[data-cy="admin-area-autocomplete"]';
  optionUndefined = 'li[data-cy="select-option-undefined"]';
  optionZero = 'li[data-cy="select-option-0"]';
  optionOne = 'li[data-cy="select-option-1"]';
  labelCategoryDescription = 'div[data-cy="label-Category Description"]';
  labelIssueTypeDescription = 'div[data-cy="label-Issue Type Description"]';
  selectFieldName =
    'div[data-cy="select-householdDataUpdateFields[0].fieldName"]';
  individualFieldName =
    'div[data-cy="select-individualDataUpdateFields[0].fieldName"]';
  inputValue = 'input[data-cy="input-householdDataUpdateFields[0].fieldValue"]';
  partner = 'div[data-cy="select-partner"]';

  // Texts
  textLookUpHousehold = "LOOK UP HOUSEHOLD";
  textLookUpIndividual = "LOOK UP INDIVIDUAL";
  textTitle = "New Ticket";
  textNext = "Next";
  textCategoryDescription = {
    "Data Change":
      "A grievance that is submitted to change in the households or beneficiary status",
    "Grievance Complaint":
      "A grievance submitted to express dissatisfaction made about an individual, UNICEF/NGO/Partner/Vendor, about a received service or about the process itself",
    Referral:
      "A grievance submitted to direct the reporting individual to another service provider/actor to provide support/help that is beyond the scope of work of UNICEF",
    "Sensitive Grievance":
      "A grievance that shall be treated with sensitivity or which individual wishes to submit anonymously",
  };

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
    Miscellaneous:
      "Other issues not falling into specific predefined categories",
    "Personal disputes":
      "Grievance on conflicts or disagreements between individuals",
    "Sexual harassment and sexual exploitation":
      "Grievance on unwanted advances, abuse, or exploitation of a sexual nature",
    "Unauthorized use, misuse or waste of UNICEF property or funds":
      "Grievance on improper or unauthorized handling or disposal of assets/funds",
  };
  // Elements
  getTitle = () => cy.get(this.title);
  getSelectCategory = () => cy.get(this.selectCategory);
  getIssueType = () => cy.get(this.issueType);
  getButtonNext = () => cy.get(this.buttonNext);
  getOption = () => cy.get(this.statusOptions);
  getHouseholdTab = () =>
    cy.get(this.lookUpTabs).contains(this.textLookUpHousehold);
  getIndividualTab = () =>
    cy.get(this.lookUpTabs).contains(this.textLookUpIndividual);
  getHouseholdTableRows = (number) => cy.get(this.householdTableRow).eq(number);
  getIndividualTableRows = (number) =>
    cy.get(this.individualTableRow).eq(number);
  getReceivedConsent = () => cy.get(this.receivedConsent);
  getDescription = () => cy.get(this.description);
  getIndividualID = () => cy.get(this.individualID);
  getHouseholdID = () => cy.get(this.householdID);
  getIssueTypeLabel = () => cy.get(this.issueTypeLabel);
  getCategory = () => cy.get(this.category);
  getComments = () => cy.get(this.comments);
  getWhoAnswersPhone = () => cy.get(this.whoAnswersPhone);
  getWhoAnswersAltPhone = () => cy.get(this.whoAnswersAltPhone);
  getRole = () => cy.get(this.role);
  getRelationship = () => cy.get(this.relationship);
  getPhoneNo = () => cy.get(this.phoneNo);
  getMiddleName = () => cy.get(this.middleName);
  getMaritalStatus = () => cy.get(this.maritalStatus);
  getPregnant = () => cy.get(this.pregnant);
  getDisability = () => cy.get(this.disability);
  getEmail = () => cy.get(this.email);
  getPhysicalDisability = () => cy.get(this.physicalDisability);
  getsSeeingDisability = () => cy.get(this.seeingDisability);
  getMemoryDisability = () => cy.get(this.memoryDisability);
  getHearingDisability = () => cy.get(this.hearingDisability);
  getCommsDisability = () => cy.get(this.commsDisability);
  getGivenName = () => cy.get(this.givenName);
  getGender = () => cy.get(this.gender);
  getFullName = () => cy.get(this.fullName);
  getFamilyName = () => cy.get(this.familyName);
  getEstimatedBirthDate = () => cy.get(this.estimatedBirthDate);
  getWorkStatus = () => cy.get(this.workStatus);
  getObservedDisability = () => cy.get(this.observedDisability);
  getSelfcareDisability = () => cy.get(this.selfcareDisability);
  getBirthDate = () => cy.get(this.birthDate);
  getPhoneNoAlternative = () => cy.get(this.phoneNoAlternative);
  getAddDocument = () => cy.get(this.addDocument);
  getLookUpButton = () => cy.get(this.lookUpButton);
  getCheckbox = () => cy.get(this.checkbox);
  getSelectUrgency = () => cy.get(this.selectUrgency);
  getSelectPriority = () => cy.get(this.selectPriority);
  getInputLanguage = () => cy.get(this.inputLanguage);
  getInputArea = () => cy.get(this.inputArea);
  getAdminAreaAutocomplete = () => cy.get(this.adminAreaAutocomplete);
  getOptionUndefined = () => cy.get(this.optionUndefined);
  getOptionZero = () => cy.get(this.optionZero);
  getOptionOne = () => cy.get(this.optionOne);
  getLabelCategoryDescription = () => cy.get(this.labelCategoryDescription);
  getLabelIssueTypeDescription = () => cy.get(this.labelIssueTypeDescription);
  getSelectFieldName = () => cy.get(this.selectFieldName);
  getInputValue = () => cy.get(this.inputValue);
  getIndividualFieldName = () => cy.get(this.individualFieldName);
  getPartner = () => cy.get(this.partner);

  checkElementsOnPage() {
    this.getTitle().contains(this.textTitle);
    this.getButtonNext().contains(this.textNext);
    this.getSelectCategory().should("be.visible");
  }

  chooseCategory(category) {
    this.getSelectCategory().click();
    this.getOption().contains(category).click();
  }

  chooseIssueType(issue) {
    this.getIssueType().should("be.visible").click();
    this.getOption().contains(issue).click();
  }

  selectOption(optionName) {
    return cy.get(`li[data-cy="select-option-${optionName}"]`);
  }

  getInputIndividualData(fieldName) {
    return cy.get(`div[data-cy="input-individual-data-${fieldName}"]`);
  }
}
