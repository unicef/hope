from time import sleep

from e2e.page_object.base_components import BaseComponents
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
    targetingCriteriaValue = 'div[data-cy="autocomplete-target-criteria-values"]'
    targetingCriteriaAddDialogSaveButton = 'button[data-cy="button-target-population-add-criteria"]'
    targetingCriteriaAddDialogSaveButtonEdit = 'button[data-cy="button-target-population-add-criteria"]'
    criteriaContainer = 'div[data-cy="criteria-container"]'
    targetPopulationSaveButton = 'button[data-cy="button-target-population-create"]'
    pageHeaderContainer = 'div[data-cy="page-header-container"]'
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    buttonTargetPopulationCreate = 'button[data-cy="button-target-population-create"]'
    inputDivName = 'div[data-cy="input-name"]'
    inputIncludedHouseholdIds = 'div[data-cy="input-included-household-ids"]'
    inputHouseholdids = '[data-cy="input-householdIds"]'
    inputIncludedIndividualIds = 'div[data-cy="input-included-individual-ids"]'
    inputIndividualids = 'input[data-cy="input-individualIds"]'
    inputFlagexcludeifonsanctionlist = 'span[data-cy="input-flagExcludeIfOnSanctionList"]'
    inputFlagexcludeifactiveadjudicationticket = 'span[data-cy="input-flagExcludeIfActiveAdjudicationTicket"]'
    iconSelected = '[data-testid="CheckBoxIcon"]'
    iconNotSelected = '[data-testid="CheckBoxOutlineBlankIcon"]'
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
    inputFiltersValueFrom = 'input[data-cy="input-householdsFiltersBlocks[{}].value.from"]'
    inputFiltersValueTo = 'input[data-cy="input-householdsFiltersBlocks[{}].value.to"]'
    inputFiltersValue = 'input[data-cy="input-householdsFiltersBlocks[{}].value"]'
    autocompleteTargetCriteriaValues = 'div[data-cy="autocomplete-target-criteria-values"]'
    selectMany = 'div[data-cy="select-many"]'
    buttonEdit = 'button[data-cy="button-edit"]'
    datePickerFilter = 'div[data-cy="date-picker-filter"]'
    boolField = 'div[data-cy="bool-field"]'
    textField = 'div[data-cy="string-textfield"]'
    selectIndividualsFiltersBlocksRoundNumber = (
        'div[data-cy="select-individualsFiltersBlocks[{}].individualBlockFilters[{}].roundNumber"]'
    )
    selectFiltersRoundNumber = 'div[data-cy="select-householdsFiltersBlocks[{}].roundNumber"]'
    selectRoundOption = 'li[data-cy="select-option-{}"]'
    selectIndividualsFiltersBlocksIsNull = (
        'span[data-cy="input-individualsFiltersBlocks[{}].individualBlockFilters[{}].isNull"]'
    )
    inputIndividualsFiltersBlocksValueFrom = (
        'input[data-cy="input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value.from"]'
    )
    inputIndividualsFiltersBlocksValueTo = (
        'input[data-cy="input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value.to"]'
    )
    inputDateIndividualsFiltersBlocksValueFrom = (
        'input[data-cy="date-input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value.from"]'
    )
    inputDateIndividualsFiltersBlocksValueTo = (
        'input[data-cy="date-input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value.to"]'
    )
    inputIndividualsFiltersBlocksValue = (
        'input[data-cy="input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value"]'
    )
    selectIndividualsFiltersBlocksValue = (
        'div[data-cy="select-individualsFiltersBlocks[{}].individualBlockFilters[{}].value"]'
    )
    totalNumberOfHouseholdsCount = 'div[data-cy="total-number-of-households-count"]'
    totalNumberOfPeopleCount = 'div[data-cy="label-Total Number of People"]'
    selectProgramCycleAutocomplete = 'div[data-cy="filters-program-cycle-autocomplete"]'
    programmeCycleInput = 'div[data-cy="Programme Cycle-input"]'
    selectRefugee = 'li[data-cy="select-option-REFUGEE"]'
    fieldChooser = 'data-cy="field-chooser-householdsFiltersBlocks[{}]"'
    noValidationFspAccept = 'button[data-cy="button-confirm"]'

    # Texts
    textTargetingCriteria = "Targeting Criteria"

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getButtonTargetPopulationCreate(self) -> WebElement:
        return self.wait_for(self.buttonTargetPopulationCreate)

    def clickButtonTargetPopulationCreate(self) -> bool:
        for _ in range(10):
            self.wait_for(self.buttonTargetPopulationCreate).click()
            try:
                self.wait_for_disappear(self.buttonTargetPopulationCreate)
                break
            except BaseException:
                pass
        else:
            raise Exception(f"Element {self.buttonTargetPopulationCreate} not found")
        return True

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

    def getInputFlagexcludeifonsanctionlist(self) -> WebElement:
        return self.wait_for(self.inputFlagexcludeifonsanctionlist)

    def getIconNotSelected(self) -> WebElement:
        return self.wait_for(self.iconNotSelected)

    def getIconSelected(self) -> WebElement:
        return self.wait_for(self.iconSelected)

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

    def getTargetingCriteriaAutoCompleteIndividual(self, index: int = 0) -> WebElement:
        for _ in range(5):
            if len(self.get_elements(self.targetingCriteriaAutoComplete.format(index))) >= 2:
                break
            sleep(1)
        return self.get_elements(self.targetingCriteriaAutoComplete.format(index))[1]

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

    def getInputFiltersValueFrom(self, fiter_number: int = 0) -> WebElement:
        return self.wait_for(self.inputFiltersValueFrom.format(fiter_number))

    def getInputFiltersValueTo(self, fiter_number: int = 0) -> WebElement:
        return self.wait_for(self.inputFiltersValueTo.format(fiter_number))

    def getInputFiltersValue(self, fiter_number: int = 0) -> WebElement:
        return self.wait_for(self.inputFiltersValue.format(fiter_number))

    def getAutocompleteTargetCriteriaValues(self) -> WebElement:
        return self.wait_for(self.autocompleteTargetCriteriaValues)

    def getSelectMany(self) -> WebElement:
        return self.wait_for(self.selectMany)

    def getButtonEdit(self) -> WebElement:
        return self.wait_for(self.buttonEdit)

    def getTextField(self) -> WebElement:
        return self.wait_for(self.textField)

    def getBoolField(self) -> WebElement:
        return self.wait_for(self.boolField)

    def getDatePickerFilter(self) -> WebElement:
        return self.wait_for(self.datePickerFilter)

    def getSelectIndividualsiFltersBlocksRoundNumber(
        self, individuals_filters_blocks_number: int = 0, individual_block_filters_number: int = 0
    ) -> WebElement:
        return self.wait_for(
            self.selectIndividualsFiltersBlocksRoundNumber.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def getSelectFiltersRoundNumber(self, round_number: int = 0) -> WebElement:
        return self.wait_for(self.selectFiltersRoundNumber.format(round_number))

    def getSelectRoundOption(self, round_number: int = 0) -> WebElement:
        return self.wait_for(self.selectRoundOption.format(round_number))

    def getSelectIndividualsiFltersBlocksIsNull(
        self, individuals_filters_blocks_number: int = 0, individual_block_filters_number: int = 0
    ) -> WebElement:
        return self.wait_for(
            self.selectIndividualsFiltersBlocksIsNull.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def getInputIndividualsFiltersBlocksValueFrom(
        self, individuals_filters_blocks_number: int = 0, individual_block_filters_number: int = 0
    ) -> WebElement:
        return self.wait_for(
            self.inputIndividualsFiltersBlocksValueFrom.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def getInputIndividualsFiltersBlocksValueTo(
        self, individuals_filters_blocks_number: int = 0, individual_block_filters_number: int = 0
    ) -> WebElement:
        return self.wait_for(
            self.inputIndividualsFiltersBlocksValueTo.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def getInputDateIndividualsFiltersBlocksValueFrom(
        self, individuals_filters_blocks_number: int = 0, individual_block_filters_number: int = 0
    ) -> WebElement:
        return self.wait_for(
            self.inputDateIndividualsFiltersBlocksValueFrom.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def getInputDateIndividualsFiltersBlocksValueTo(
        self, individuals_filters_blocks_number: int = 0, individual_block_filters_number: int = 0
    ) -> WebElement:
        return self.wait_for(
            self.inputDateIndividualsFiltersBlocksValueTo.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def getInputIndividualsFiltersBlocksValue(
        self, individuals_filters_blocks_number: int = 0, individual_block_filters_number: int = 0
    ) -> WebElement:
        return self.wait_for(
            self.inputIndividualsFiltersBlocksValue.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def getSelectIndividualsFiltersBlocksValue(
        self, individuals_filters_blocks_number: int = 0, individual_block_filters_number: int = 0
    ) -> WebElement:
        return self.wait_for(
            self.selectIndividualsFiltersBlocksValue.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def getTotalNumberOfHouseholdsCount(self) -> WebElement:
        return self.wait_for(self.totalNumberOfHouseholdsCount)

    def getTotalNumberOfPeopleCount(self) -> WebElement:
        return self.wait_for(self.totalNumberOfPeopleCount)

    def getFiltersProgramCycleAutocomplete(self) -> WebElement:
        return self.wait_for(self.selectProgramCycleAutocomplete)

    def getProgrammeCycleInput(self) -> WebElement:
        return self.wait_for(self.programmeCycleInput)

    def getSelectRefugee(self) -> WebElement:
        return self.wait_for(self.selectRefugee)

    def getFieldChooser(self, num: int) -> WebElement:
        return self.wait_for(self.fieldChooser.format(str(num)))

    def getNoValidationFspAccept(self) -> WebElement:
        return self.wait_for(self.noValidationFspAccept)
