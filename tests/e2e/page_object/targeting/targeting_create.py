from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class TargetingCreate(BaseComponents):
    # Locators
    targeting_criteria = 'h6[data-cy="title-targeting-criteria"]'
    add_criteria_button = 'div[data-cy="button-target-population-add-criteria"]'
    add_household_rule_button = '[data-cy="button-household-rule"]'
    add_individual_rule_button = '[data-cy="button-individual-rule"]'
    add_people_rule_button = '[data-cy="button-household-rule"]'
    title_page = 'h5[data-cy="page-header-title"]'
    field_name = 'input[data-cy="input-name"]'
    targeting_criteria_auto_complete = 'input[data-cy="autocomplete-target-criteria-option-{}"]'
    targeting_criteria_value = 'div[data-cy="autocomplete-target-criteria-values"]'
    targeting_criteria_add_dialog_save_button = 'button[data-cy="button-target-population-add-criteria"]'
    targeting_criteria_add_dialog_save_button_edit = 'button[data-cy="button-target-population-add-criteria"]'
    criteria_container = 'div[data-cy="criteria-container"]'
    target_population_save_button = 'button[data-cy="button-target-population-create"]'
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    button_target_population_create = 'button[data-cy="button-target-population-create"]'
    input_div_name = 'div[data-cy="input-name"]'
    input_included_household_ids = 'div[data-cy="input-included-household-ids"]'
    input_householdids = '[data-cy="input-householdIds"]'
    input_included_individual_ids = 'div[data-cy="input-included-individual-ids"]'
    input_individualids = 'input[data-cy="input-individualIds"]'
    input_flag_exclude_if_on_sanction_list = 'span[data-cy="input-flagExcludeIfOnSanctionList"]'
    input_flag_exclude_if_active_adjudication_ticket = 'span[data-cy="input-flagExcludeIfActiveAdjudicationTicket"]'
    icon_selected = '[data-testid="CheckBoxIcon"]'
    icon_not_selected = '[data-testid="CheckBoxOutlineBlankIcon"]'
    input_name = 'input[data-cy="input-name"]'
    div_target_population_add_criteria = 'div[data-cy="button-target-population-add-criteria"]'
    title_excluded_entries = 'h6[data-cy="title-excluded-entries"]'
    button_show_hide_exclusions = 'button[data-cy="button-show-hide-exclusions"]'
    input_excluded_ids = 'div[data-cy="input-excluded-ids"]'
    input_excludedids = 'input[data-cy="input-excludedIds"]'
    input_exclusion_reason = 'div[data-cy="input-exclusion-reason"]'
    title_add_filter = 'h6[data-cy="title-add-filter"]'
    autocomplete_target_criteria = 'div[data-cy="autocomplete-target-criteria"]'
    field_chooser_filters = 'div[data-cy="field-chooser-filters[0]"]'
    autocomplete_target_criteria_option = 'input[data-cy="autocomplete-target-criteria-option-0"]'
    button_household_rule = 'button[data-cy="button-household-rule"]'
    button_individual_rule = 'button[data-cy="button-individual-rule"]'
    button_target_population_add_criteria = 'button[data-cy="button-target-population-add-criteria"]'
    button_save = 'button[data-cy="button-save"]'
    input_filters_value_from = 'input[data-cy="input-householdsFiltersBlocks[{}].value.from"]'
    input_filters_value_to = 'input[data-cy="input-householdsFiltersBlocks[{}].value.to"]'
    input_filters_value = 'input[data-cy="input-householdsFiltersBlocks[{}].value"]'
    autocomplete_target_criteria_values = 'div[data-cy="autocomplete-target-criteria-values"]'
    select_many = 'div[data-cy="select-many"]'
    button_edit = 'button[data-cy="button-edit"]'
    date_picker_filter = 'div[data-cy="date-picker-filter"]'
    bool_field = 'div[data-cy="bool-field"]'
    text_field = 'div[data-cy="string-textfield"]'
    select_individuals_filters_blocks_round_number = (
        'div[data-cy="select-individualsFiltersBlocks[{}].individualBlockFilters[{}].roundNumber"]'
    )
    select_filters_round_number = 'div[data-cy="select-householdsFiltersBlocks[{}].roundNumber"]'
    select_round_option = 'li[data-cy="select-option-{}"]'
    select_individuals_filters_blocks_is_null = (
        'span[data-cy="input-individualsFiltersBlocks[{}].individualBlockFilters[{}].isNull"]'
    )
    input_individuals_filters_blocks_value_from = (
        'input[data-cy="input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value.from"]'
    )
    input_individuals_filters_blocks_value_to = (
        'input[data-cy="input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value.to"]'
    )
    input_date_individuals_filters_blocks_value_from = (
        'input[data-cy="date-input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value.from"]'
    )
    input_date_individuals_filters_blocks_value_to = (
        'input[data-cy="date-input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value.to"]'
    )
    input_individuals_filters_blocks_value = (
        'input[data-cy="input-individualsFiltersBlocks[{}].individualBlockFilters[{}].value"]'
    )
    select_individuals_filters_blocks_value = (
        'div[data-cy="select-individualsFiltersBlocks[{}].individualBlockFilters[{}].value"]'
    )
    total_number_of_households_count = 'div[data-cy="total-number-of-households-count"]'
    total_number_of_people_count = 'div[data-cy="label-Total Number of People"]'
    select_program_cycle_autocomplete = 'div[data-cy="filters-program-cycle-autocomplete"]'
    programme_cycle_input = 'div[data-cy="Programme Cycle-input"]'
    select_refugee = 'li[data-cy="select-option-REFUGEE"]'
    field_chooser = 'data-cy="field-chooser-householdsFiltersBlocks[{}]"'
    no_validation_fsp_accept = 'button[data-cy="button-confirm"]'

    # Texts
    text_targeting_criteria = "Targeting Criteria"

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_button_target_population_create(self) -> WebElement:
        return self.wait_for(self.button_target_population_create)

    def click_button_target_population_create(self) -> bool:
        for _ in range(10):
            self.wait_for(self.button_target_population_create).click()
            try:
                self.wait_for_disappear(self.button_target_population_create)
                break
            except TimeoutException:
                pass
        else:
            raise Exception(f"Element {self.button_target_population_create} not found")
        return True

    def get_input_name(self) -> WebElement:
        return self.wait_for(self.input_name)

    def get_input_included_household_ids(self) -> WebElement:
        return self.wait_for(self.input_included_household_ids)

    def get_input_household_ids(self) -> WebElement:
        return self.wait_for(self.input_householdids)

    def get_input_included_individual_ids(self) -> WebElement:
        return self.wait_for(self.input_included_individual_ids)

    def get_input_individual_ids(self) -> WebElement:
        return self.wait_for(self.input_individualids)

    def get_input_flag_exclude_if_active_adjudication_ticket(self) -> WebElement:
        return self.wait_for(self.input_flag_exclude_if_active_adjudication_ticket)

    def get_input_flag_exclude_if_on_sanction_list(self) -> WebElement:
        return self.wait_for(self.input_flag_exclude_if_on_sanction_list)

    def get_icon_not_selected(self) -> WebElement:
        return self.wait_for(self.icon_not_selected)

    def get_icon_selected(self) -> WebElement:
        return self.wait_for(self.icon_selected)

    def get_button_target_population_add_criteria(self) -> WebElement:
        return self.wait_for(self.button_target_population_add_criteria)

    def get_div_target_population_add_criteria(self) -> WebElement:
        return self.wait_for(self.div_target_population_add_criteria)

    def get_title_excluded_entries(self) -> WebElement:
        return self.wait_for(self.title_excluded_entries)

    def get_button_show_hide_exclusions(self) -> WebElement:
        return self.wait_for(self.button_show_hide_exclusions)

    def get_input_excluded_ids(self) -> WebElement:
        return self.wait_for(self.input_excluded_ids)

    def get_input_excludedids(self) -> WebElement:
        return self.wait_for(self.input_excludedids)

    def get_input_exclusion_reason(self) -> WebElement:
        return self.wait_for(self.input_exclusion_reason)

    def get_button_household_rule(self) -> WebElement:
        return self.wait_for(self.button_household_rule)

    def get_button_individual_rule(self) -> WebElement:
        return self.wait_for(self.button_individual_rule)

    def get_autocomplete_target_criteria_option(self) -> WebElement:
        return self.wait_for(self.autocomplete_target_criteria_option)

    def get_targeting_criteria(self) -> WebElement:
        return self.wait_for(self.targeting_criteria)

    def get_title_page(self) -> WebElement:
        return self.wait_for(self.title_page)

    def get_add_criteria_button(self) -> WebElement:
        return self.wait_for(self.add_criteria_button)

    def get_add_household_rule_button(self) -> WebElement:
        return self.wait_for(self.add_household_rule_button)

    def get_add_individual_rule_button(self) -> WebElement:
        return self.wait_for(self.add_individual_rule_button)

    def get_add_people_rule_button(self) -> WebElement:
        return self.wait_for(self.add_people_rule_button)

    def get_targeting_criteria_auto_complete(self, index: int = 0) -> WebElement:
        return self.wait_for(self.targeting_criteria_auto_complete.format(index))

    def get_targeting_criteria_auto_complete_individual(self, index: int = 0) -> WebElement:
        for _ in range(5):
            if len(self.get_elements(self.targeting_criteria_auto_complete.format(index))) >= 2:
                break
            sleep(1)
        return self.get_elements(self.targeting_criteria_auto_complete.format(index))[1]

    def get_targeting_criteria_value(self, index: int = 0) -> WebElement:
        return self.wait_for(self.targeting_criteria_value.format(index))

    def get_targeting_criteria_add_dialog_save_button(self) -> WebElement:
        return self.wait_for(self.targeting_criteria_add_dialog_save_button)

    def get_criteria_container(self) -> WebElement:
        return self.wait_for(self.criteria_container)

    def get_field_name(self) -> WebElement:
        return self.wait_for(self.field_name)

    def get_target_population_save_button(self) -> WebElement:
        return self.wait_for(self.target_population_save_button)

    def get_button_save(self) -> WebElement:
        return self.wait_for(self.button_save)

    def get_input_filters_value_from(self, fiter_number: int = 0) -> WebElement:
        return self.wait_for(self.input_filters_value_from.format(fiter_number))

    def get_input_filters_value_to(self, fiter_number: int = 0) -> WebElement:
        return self.wait_for(self.input_filters_value_to.format(fiter_number))

    def get_input_filters_value(self, fiter_number: int = 0) -> WebElement:
        return self.wait_for(self.input_filters_value.format(fiter_number))

    def get_autocomplete_target_criteria_values(self) -> WebElement:
        return self.wait_for(self.autocomplete_target_criteria_values)

    def get_select_many(self) -> WebElement:
        return self.wait_for(self.select_many)

    def get_button_edit(self) -> WebElement:
        return self.wait_for(self.button_edit)

    def get_text_field(self) -> WebElement:
        return self.wait_for(self.text_field)

    def get_bool_field(self) -> WebElement:
        return self.wait_for(self.bool_field)

    def get_date_picker_filter(self) -> WebElement:
        return self.wait_for(self.date_picker_filter)

    def get_select_individuals_filters_blocks_round_number(
        self,
        individuals_filters_blocks_number: int = 0,
        individual_block_filters_number: int = 0,
    ) -> WebElement:
        return self.wait_for(
            self.select_individuals_filters_blocks_round_number.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def get_select_filters_round_number(self, round_number: int = 0) -> WebElement:
        return self.wait_for(self.select_filters_round_number.format(round_number))

    def get_select_round_option(self, round_number: int = 0) -> WebElement:
        return self.wait_for(self.select_round_option.format(round_number))

    def get_select_individuals_filters_blocks_is_null(
        self,
        individuals_filters_blocks_number: int = 0,
        individual_block_filters_number: int = 0,
    ) -> WebElement:
        return self.wait_for(
            self.select_individuals_filters_blocks_is_null.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def get_input_individuals_filters_blocks_value_from(
        self,
        individuals_filters_blocks_number: int = 0,
        individual_block_filters_number: int = 0,
    ) -> WebElement:
        return self.wait_for(
            self.input_individuals_filters_blocks_value_from.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def get_input_individuals_filters_blocks_value_to(
        self,
        individuals_filters_blocks_number: int = 0,
        individual_block_filters_number: int = 0,
    ) -> WebElement:
        return self.wait_for(
            self.input_individuals_filters_blocks_value_to.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def get_input_date_individuals_filters_blocks_value_from(
        self,
        individuals_filters_blocks_number: int = 0,
        individual_block_filters_number: int = 0,
    ) -> WebElement:
        return self.wait_for(
            self.input_date_individuals_filters_blocks_value_from.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def get_input_date_individuals_filters_blocks_value_to(
        self,
        individuals_filters_blocks_number: int = 0,
        individual_block_filters_number: int = 0,
    ) -> WebElement:
        return self.wait_for(
            self.input_date_individuals_filters_blocks_value_to.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def get_input_individuals_filters_blocks_value(
        self,
        individuals_filters_blocks_number: int = 0,
        individual_block_filters_number: int = 0,
    ) -> WebElement:
        return self.wait_for(
            self.input_individuals_filters_blocks_value.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def get_select_individuals_filters_blocks_value(
        self,
        individuals_filters_blocks_number: int = 0,
        individual_block_filters_number: int = 0,
    ) -> WebElement:
        return self.wait_for(
            self.select_individuals_filters_blocks_value.format(
                individuals_filters_blocks_number, individual_block_filters_number
            )
        )

    def get_total_number_of_households_count(self) -> WebElement:
        return self.wait_for(self.total_number_of_households_count)

    def get_total_number_of_people_count(self) -> WebElement:
        return self.wait_for(self.total_number_of_people_count)

    def get_filters_program_cycle_autocomplete(self) -> WebElement:
        return self.wait_for(self.select_program_cycle_autocomplete)

    def get_programme_cycle_input(self) -> WebElement:
        return self.wait_for(self.programme_cycle_input)

    def get_select_refugee(self) -> WebElement:
        return self.wait_for(self.select_refugee)

    def get_field_chooser(self, num: int) -> WebElement:
        return self.wait_for(self.field_chooser.format(str(num)))

    def get_no_validation_fsp_accept(self) -> WebElement:
        return self.wait_for(self.no_validation_fsp_accept)
