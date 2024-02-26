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
    lookUpTabs = 'button[role="tab"]'
    receivedConsent = 'span[data-cy="input-consent"]'
    description = 'textarea[data-cy="input-description"]'
    comments = 'textarea[data-cy="input-comments"]'
    adminAreaAutocomplete = 'div[data-cy="input-admin2"]'
    inputLanguage = 'textarea[data-cy="input-language"]'
    inputArea = 'input[data-cy="input-area"]'

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

    def getOption(self) -> WebElement:
        return self.wait_for(self.option)

    def getHouseholdTab(self) -> WebElement:
        return self.wait_for(self.lookUpTabs).contains(self.textLookUpHousehold)

    def getLookUpIndividual(self) -> WebElement:
        return self.wait_for(self.lookUpTabs).contains(self.textLookUpIndividual)

    def getHouseholdTableRows(self, number: int) -> WebElement:
        return self.wait_for(self.householdTableRow).eq(number)

    def getIndividualTableRow(self, number: int) -> WebElement:
        return self.wait_for(self.individualTableRow).eq(number)

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

    def checkElementsOnPage(self) -> None:
        self.getTitlePage().contains(self.textTitle)
        self.getLabelCategory().contains(self.textCategory)
        self.getSelectIssueType().should("be.visible")
        self.getButtonCancel().should("be.visible")
        self.getButtonBack().should("be.visible")
        self.getButtonNext().should("be.visible")

    def chooseOptionByName(self, name: str) -> None:
        self.getSelectIssueType().click()
        self.getOption().contains(name).click()
