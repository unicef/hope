from page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class TargetingCreate(BaseComponents):
    # Locators
    targetingCriteria = 'h6[data-cy="title-targeting-criteria"]'
    addCriteriaButton = 'div[data-cy="button-target-population-add-criteria"]'
    addHouseholdRuleButton = '[data-cy="button-household-rule"]'
    addIndividualRuleButton = '[data-cy="button-individual-rule"]'
    addPeopleRuleButton = '[data-cy="button-household-rule"]'
    titlePage = 'h5[data-cy="page-header-title"]'
    fieldName = 'input[data-cy="input-name"]'
    targetingCriteriaAutoComplete = 'input[data-cy="autocomplete-target-criteria-option-{}"]'
    targetingCriteriaValue = '[data-cy="select-filters[{}].value"]'
    targetingCriteriaAddDialogSaveButton = 'button[data-cy="button-target-population-add-criteria"]'
    criteriaContainer = 'div[data-cy="criteria-container"]'
    targetPopulationSaveButton = 'button[data-cy="button-target-population-create"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonTargetPopulationCreate = 'button[data-cy="button-target-population-create"]'
    inputDivName = 'div[data-cy="input-name"]'
    inputIncludedHouseholdIds = 'div[data-cy="input-included-household-ids"]'
    inputHouseholdids = 'input[data-cy="input-householdIds"]'
    inputIncludedIndividualIds = 'div[data-cy="input-included-individual-ids"]'
    inputIndividualids = 'input[data-cy="input-individualIds"]'
    inputFlagexcludeifactiveadjudicationticket = 'span[data-cy="input-flagExcludeIfActiveAdjudicationTicket"]'
    inputName = 'input[data-cy="input-name"]'
    divTargetPopulationAddCriteria = 'div[data-cy="button-target-population-add-criteria"]'
    titleExcludedEntries = 'h6[data-cy="title-excluded-entries"]'
    buttonShowHideExclusions = 'button[data-cy="button-show-hide-exclusions"]'
    inputExcludedIds = 'div[data-cy="input-excluded-ids"]'
    inputExcludedids = 'input[data-cy="input-excludedIds"]'
    inputExclusionReason = 'div[data-cy="input-exclusion-reason"]'
    titleAddFilter = 'h6[data-cy="title-add-filter"]'
    autocompleteTargetCriteria = 'div[data-cy="autocomplete-target-criteria"]'
    fieldChooserFilters = 'div[data-cy="field-chooser-filters[0]"]'
    autocompleteTargetCriteriaOption = 'input[data-cy="autocomplete-target-criteria-option-0"]'
    buttonHouseholdRule = 'button[data-cy="button-household-rule"]'
    buttonIndividualRule = 'button[data-cy="button-individual-rule"]'
    buttonTargetPopulationAddCriteria = 'button[data-cy="button-target-population-add-criteria"]'
    buttonSave = 'button[data-cy="button-save"]'
    # Texts
    textTargetingCriteria = "Targeting Criteria"

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonTargetPopulationCreate(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationCreate)

    def getInputName(self) -> WebElement:
        return self.wait_for(self.inputName)

    def getInputIncludedHouseholdIds(self) -> WebElement:
        return self.wait_for(self.inputIncludedHouseholdIds)

    def getInputHouseholdids(self) -> WebElement:
        return self.wait_for(self.inputHouseholdids)

    def getInputIncludedIndividualIds(self) -> WebElement:
        return self.wait_for(self.inputIncludedIndividualIds)

    def getInputIndividualids(self) -> WebElement:
        return self.wait_for(self.inputIndividualids)

    def getInputFlagexcludeifactiveadjudicationticket(self) -> WebElement:
        return self.wait_for(self.inputFlagexcludeifactiveadjudicationticket)

    def getButtonTargetPopulationAddCriteria(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationAddCriteria)

    def getDivTargetPopulationAddCriteria(self) -> WebElement:
        return self.wait_for(self.divTargetPopulationAddCriteria)

    def getTitleExcludedEntries(self) -> WebElement:
        return self.wait_for(self.titleExcludedEntries)

    def getButtonShowHideExclusions(self) -> WebElement:
        return self.wait_for(self.buttonShowHideExclusions)

    def getInputExcludedIds(self) -> WebElement:
        return self.wait_for(self.inputExcludedIds)

    def getInputExcludedids(self) -> WebElement:
        return self.wait_for(self.inputExcludedids)

    def getInputExclusionReason(self) -> WebElement:
        return self.wait_for(self.inputExclusionReason)

    def getButtonHouseholdRule(self) -> WebElement:
        return self.wait_for(self.buttonHouseholdRule)

    def getButtonIndividualRule(self) -> WebElement:
        return self.wait_for(self.buttonIndividualRule)

    def getAutocompleteTargetCriteriaOption(self) -> WebElement:
        return self.wait_for(self.autocompleteTargetCriteriaOption)

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

    def getButtonSave(self) -> WebElement:
        return self.wait_for(self.buttonSave)
