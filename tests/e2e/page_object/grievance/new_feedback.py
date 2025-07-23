from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class NewFeedback(BaseComponents):
    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    labelCategory = 'div[data-cy="label-Category"]'
    selectIssueType = 'div[data-cy="select-issueType"]'
    issueType = 'div[data-cy="label-Issue Type"]'
    inputIssueType = 'div[data-cy="input-issue-type"]'
    buttonCancel = 'a[data-cy="button-cancel"]'
    buttonBack = 'button[data-cy="button-back"]'
    buttonNext = 'button[data-cy="button-submit"]'
    option = 'li[role="option"]'
    householdTableRow = 'tr[data-cy="household-table-row"]'
    individualTableRow = 'tr[data-cy="individual-table-row"]'
    lookUpTabsHouseHold = 'button[role="tab"]'
    lookUpTabsIndividual = 'button[role="tab"]'
    receivedConsent = 'span[data-cy="input-consent"]'
    error = 'p[data-cy="checkbox-error"]'
    divDescription = 'div[data-cy="input-description"]'
    description = 'textarea[data-cy="input-description"]'
    comments = 'textarea[data-cy="input-comments"]'
    adminAreaAutocomplete = 'div[data-cy="admin-area-autocomplete"]'
    inputLanguage = 'textarea[data-cy="input-language"]'
    inputArea = 'input[data-cy="input-area"]'
    programmeSelect = 'div[data-cy="select-program"]'
    hhRadioButton = 'span[data-cy="input-radio-household"]'
    individualRadioButton = 'span[data-cy="input-radio-individual"]'
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
    labelIndividualFullName = 'div[data-cy="label-Member full name"]'
    inputQuestionnaire_birthdate = 'span[data-cy="input-questionnaire_birthDate"]'
    labelBirthDate = 'div[data-cy="label-Birth Date"]'
    inputQuestionnaire_phoneno = 'span[data-cy="input-questionnaire_phoneNo"]'
    labelPhoneNumber = 'div[data-cy="label-Phone Number"]'
    inputQuestionnaire_relationship = 'span[data-cy="input-questionnaire_relationship"]'
    emptyHouseholdRow = 'tr[data-cy="table-row"]'

    # Texts
    textTitle = "New Feedback"
    textCategory = "Feedback"
    textLookUpHousehold = "LOOK UP {}"
    textLookUpIndividual = "LOOK UP {}"

    # Elements

    def getTitlePage(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getLabelCategory(self) -> WebElement:
        return self.wait_for(self.labelCategory)

    def getSelectIssueType(self) -> WebElement:
        return self.wait_for(self.selectIssueType)

    def getButtonCancel(self) -> WebElement:
        return self.wait_for(self.buttonCancel)

    def getButtonBack(self) -> WebElement:
        return self.wait_for(self.buttonBack)

    def getButtonNext(self) -> WebElement:
        return self.wait_for(self.buttonNext)

    def getOptions(self) -> list[WebElement]:
        return self.get_elements(self.option)

    def getHouseholdTab(self, tab_name: str = "GROUP") -> None:
        try:
            household_tab = self.get_elements(self.lookUpTabsHouseHold)[0]
        except IndexError:
            sleep(1)
            household_tab = self.get_elements(self.lookUpTabsHouseHold)[0]
        assert self.textLookUpHousehold.format(tab_name) in household_tab.text, household_tab.text
        return household_tab

    def getIndividualTab(self, tab_name: str = "MEMBER") -> WebElement:
        try:
            individual_tab = self.get_elements(self.lookUpTabsIndividual, attempts=5)[1]
        except IndexError:
            sleep(1)
            individual_tab = self.get_elements(self.lookUpTabsIndividual, attempts=5)[1]
        assert self.textLookUpIndividual.format(tab_name) in individual_tab.text, individual_tab.text
        return individual_tab

    def getHouseholdTableRows(self, number: int) -> WebElement:
        self.get_elements(self.hhRadioButton)
        try:
            return self.get_elements(self.householdTableRow, attempts=5)[number]
        except IndexError:
            sleep(1)
            return self.get_elements(self.householdTableRow, attempts=5)[number]

    def getIndividualTableRow(self, number: int) -> WebElement:
        self.get_elements(self.individualRadioButton)
        try:
            return self.get_elements(self.individualTableRow, attempts=5)[number]
        except IndexError:
            sleep(1)
            return self.get_elements(self.individualTableRow, attempts=5)[number]

    def getReceivedConsent(self) -> WebElement:
        return self.wait_for(self.receivedConsent)

    def getError(self) -> WebElement:
        return self.wait_for(self.error)

    def getDescription(self) -> WebElement:
        return self.wait_for(self.description)

    def getDivDescription(self) -> WebElement:
        return self.wait_for(self.divDescription)

    def getComments(self) -> WebElement:
        return self.wait_for(self.comments)

    def getInputLanguage(self) -> WebElement:
        return self.wait_for(self.inputLanguage)

    def getInputArea(self) -> WebElement:
        return self.wait_for(self.inputArea)

    def getAdminAreaAutocomplete(self) -> WebElement:
        return self.wait_for(self.adminAreaAutocomplete)

    def selectArea(self, name: str) -> None:
        self.getAdminAreaAutocomplete().click()
        self.select_listbox_element(name)

    def getIssueType(self) -> WebElement:
        return self.wait_for(self.issueType)

    def getInputIssueType(self) -> WebElement:
        return self.wait_for(self.inputIssueType)

    def getProgrammeSelect(self) -> WebElement:
        return self.wait_for(self.programmeSelect)

    def selectProgramme(self, name: str) -> None:
        self.getProgrammeSelect().click()
        self.select_listbox_element(name)

    def checkElementsOnPage(self) -> None:
        assert self.textTitle in self.getTitlePage().text
        assert self.textCategory in self.getLabelCategory().text
        self.getSelectIssueType()
        self.getButtonCancel()
        self.getButtonBack()
        self.getButtonNext()

    def chooseOptionByName(self, name: str) -> None:
        self.getSelectIssueType().click()
        self.select_listbox_element(name)

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

    def getInputQuestionnaire_phoneno(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_phoneno)

    def getLabelPhoneNumber(self) -> WebElement:
        return self.wait_for(self.labelPhoneNumber)

    def getInputQuestionnaire_relationship(self) -> WebElement:
        return self.wait_for(self.inputQuestionnaire_relationship)

    def getLabelRelationshipToHoh(self) -> WebElement:
        return self.wait_for(self.labelRelationshipToHoh)

    def getInputConsent(self) -> WebElement:
        return self.wait_for(self.inputConsent)

    def getTableEmptyRow(self) -> None:
        self.wait_for_text("No results", self.emptyHouseholdRow)
