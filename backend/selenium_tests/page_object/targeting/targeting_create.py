from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class TargetingCreate(BaseComponents):
    # Locators
    targetingCriteria = 'h6[data-cy="title-targeting-criteria"]'
    addCriteriaButton = 'div[data-cy="button-target-population-add-criteria"]'
    addHouseholdRuleButton = '[data-cy="button-household-rule"]'
    addIndividualRuleButton = '[data-cy="button-individual-rule"]'
    addPeopleRuleButton = '[data-cy="button-household-rule"]'
    addHouseholdeRuleButton = '[data-cy="button-household-rule"]'
    titlePage = 'h5[data-cy="page-header-title"]'
    fieldName = 'input[data-cy="input-name"]'
    targetingCriteriaAutoComplete = 'input[data-cy="autocomplete-target-criteria-option-{}"]'
    targetingCriteriaValue = '[data-cy="select-filters[{}].value"]'
    targetingCriteriaAddDialogSaveButton = 'button[data-cy="button-target-population-add-criteria"]'
    criteriaContainer = 'div[data-cy="criteria-container"]'
    targetPopulationSaveButton = 'button[data-cy="button-target-population-create"]'
    # Texts
    textTargetingCriteria = "Targeting Criteria"

    # Elements

    def getTargetingCriteria(self) -> WebElement:
        return self.wait_for(self.targetingCriteria)

    def getTitlePage(self) -> WebElement:
        return self.wait_for(self.titlePage)

    def getAddCriteriaButton(self) -> WebElement:
        return self.wait_for(self.addCriteriaButton)

    def getAddHouseholdRuleButton(self) -> WebElement:
        return self.wait_for(self.addHouseholdRuleButton)

    def getAddIndividualRuleButton(self) -> WebElement:
        return self.wait_for(self.addIndividualRuleButton)

    def getAddPeopleRuleButton(self) -> WebElement:
        return self.wait_for(self.addPeopleRuleButton)

    def getAddHouseholdRuleButton(self) -> WebElement:
        return self.wait_for(self.addHouseholdeRuleButton)

    def getTargetingCriteriaAutoComplete(self, index: int = 0) -> WebElement:
        return self.wait_for(self.targetingCriteriaAutoComplete.format(index))

    def getTargetingCriteriaValue(self, index: int = 0) -> WebElement:
        return self.wait_for(self.targetingCriteriaValue.format(index))

    def getTargetingCriteriaAddDialogSaveButton(self) -> WebElement:
        return self.wait_for(self.targetingCriteriaAddDialogSaveButton)

    def getCriteriaContainer(self) -> WebElement:
        return self.wait_for(self.criteriaContainer)

    def getFieldName(self) -> WebElement:
        return self.wait_for(self.fieldName)

    def getTargetPopulationSaveButton(self) -> WebElement:
        return self.wait_for(self.targetPopulationSaveButton)
