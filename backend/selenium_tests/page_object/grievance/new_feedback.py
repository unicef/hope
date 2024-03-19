from page_object.base_components import BaseComponents
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
    individualTableRow = 'tr[data-cy="individual-table-row"'
    lookUpTabsHouseHold = 'button[role="tab"]'
    lookUpTabsIndividual = 'button[role="tab"]'
    receivedConsent = 'span[data-cy="input-consent"]'
    description = 'textarea[data-cy="input-description"]'
    comments = 'textarea[data-cy="input-comments"]'
    adminAreaAutocomplete = 'div[data-cy="input-admin2"]'
    inputLanguage = 'textarea[data-cy="input-language"]'
    inputArea = 'input[data-cy="input-area"]'
    programmeSelect = 'div[data-cy="select-program"]'
    hhRadioButton = 'span[data-cy="input-radio-household"]'

    # Texts
    textTitle = "New Feedback"
    textCategory = "Feedback"
    textLookUpHousehold = "LOOK UP HOUSEHOLD"
    textLookUpIndividual = "LOOK UP INDIVIDUAL"

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

    def getHouseholdTab(self) -> None:
        household_tab = self.get_elements(self.lookUpTabsHouseHold)[0]
        assert self.textLookUpHousehold in household_tab.text
        return household_tab

    def getIndividualTab(self) -> WebElement:
        individual_tab = self.get_elements(self.lookUpTabsIndividual)[1]
        assert self.textLookUpIndividual in individual_tab.text
        return individual_tab

    def getHouseholdTableRows(self, number: int) -> WebElement:
        self.get_elements(self.hhRadioButton)
        return self.get_elements(self.householdTableRow)[number]

    def getIndividualTableRow(self, number: int) -> WebElement:
        return self.get_elements(self.individualTableRow)[number]

    def getReceivedConsent(self) -> WebElement:
        return self.wait_for(self.receivedConsent)

    def getDescription(self) -> WebElement:
        return self.wait_for(self.description)

    def getComments(self) -> WebElement:
        return self.wait_for(self.comments)

    def getInputLanguage(self) -> WebElement:
        return self.wait_for(self.inputLanguage)

    def getInputArea(self) -> WebElement:
        return self.wait_for(self.inputArea)

    def getAdminAreaAutocomplete(self) -> WebElement:
        return self.wait_for(self.adminAreaAutocomplete)

    def getIssueType(self) -> WebElement:
        return self.wait_for(self.issueType)

    def getInputIssueType(self) -> WebElement:
        return self.wait_for(self.inputIssueType)

    def getProgrammeSelect(self) -> WebElement:
        return self.wait_for(self.programmeSelect)

    def selectProgramme(self, name: str) -> WebElement:
        self.getProgrammeSelect().click()
        return self.select_listbox_element(name)

    def checkElementsOnPage(self) -> None:
        assert self.textTitle in self.getTitlePage().text
        assert self.textCategory in self.getLabelCategory().text
        self.getSelectIssueType()
        self.getButtonCancel()
        self.getButtonBack()
        self.getButtonNext()

    def chooseOptionByName(self, name: str) -> None:
        self.getSelectIssueType().click()
        self.select_listbox_element(name).click()
