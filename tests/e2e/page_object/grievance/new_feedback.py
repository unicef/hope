from time import sleep

from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class NewFeedback(BaseComponents):
    # Locators
    title_page = 'h5[data-cy="page-header-title"]'
    label_category = 'div[data-cy="label-Category"]'
    select_issue_type = 'div[data-cy="select-issueType"]'
    issue_type = 'div[data-cy="label-Issue Type"]'
    input_issue_type = 'div[data-cy="input-issue-type"]'
    button_cancel = 'a[data-cy="button-cancel"]'
    button_back = 'button[data-cy="button-back"]'
    button_next = 'button[data-cy="button-submit"]'
    option = 'li[role="option"]'
    household_table_row = 'tr[data-cy="household-table-row"]'
    individual_table_row = 'tr[data-cy="individual-table-row"]'
    look_up_tabs_household = 'button[role="tab"]'
    look_up_tabs_individual = 'button[role="tab"]'
    received_consent = 'span[data-cy="input-consent"]'
    error = 'p[data-cy="checkbox-error"]'
    div_description = 'div[data-cy="input-description"]'
    description = 'textarea[data-cy="input-description"]'
    comments = 'textarea[data-cy="input-comments"]'
    admin_area_autocomplete = 'div[data-cy="admin-area-autocomplete"]'
    input_language = 'textarea[data-cy="input-language"]'
    input_area = 'input[data-cy="input-area"]'
    programme_select = 'div[data-cy="select-programId"]'
    hh_radio_button = 'span[data-cy="input-radio-household"]'
    individual_radio_button = 'span[data-cy="input-radio-individual"]'
    input_questionnaire_size = 'span[data-cy="input-questionnaire_size"]'
    label_household_size = 'div[data-cy="label-Household Size"]'
    input_questionnaire_malechildrencount = 'span[data-cy="input-questionnaire_maleChildrenCount"]'
    label_number_of_male_children = 'div[data-cy="label-Number of Male Children"]'
    input_questionnaire_femalechildrencount = 'span[data-cy="input-questionnaire_femaleChildrenCount"]'
    label_number_of_female_children = 'div[data-cy="label-Number of Female Children"]'
    input_questionnaire_childrendisabledcount = 'span[data-cy="input-questionnaire_childrenDisabledCount"]'
    label_number_of_disabled_children = 'div[data-cy="label-Number of Disabled Children"]'
    input_questionnaire_headofhousehold = 'span[data-cy="input-questionnaire_headOfHousehold"]'
    label_head_of_household = 'div[data-cy="label-Head of Household"]'
    input_questionnaire_countryorigin = 'span[data-cy="input-questionnaire_countryOrigin"]'
    label_country_of_origin = 'div[data-cy="label-Country of Origin"]'
    input_questionnaire_address = 'span[data-cy="input-questionnaire_address"]'
    label_address = 'div[data-cy="label-Address"]'
    input_questionnaire_village = 'span[data-cy="input-questionnaire_village"]'
    label_village = 'div[data-cy="label-Village"]'
    input_questionnaire_admin1 = 'span[data-cy="input-questionnaire_admin1"]'
    label_administrative_level1 = 'div[data-cy="label-Administrative Level 1"]'
    input_questionnaire_admin2 = 'span[data-cy="input-questionnaire_admin2"]'
    label_administrative_level2 = 'div[data-cy="label-Administrative Level 2"]'
    input_questionnaire_admin3 = 'span[data-cy="input-questionnaire_admin3"]'
    label_administrative_level3 = 'div[data-cy="label-Administrative Level 3"]'
    input_questionnaire_admin4 = 'span[data-cy="input-questionnaire_admin4"]'
    label_administrative_level4 = 'div[data-cy="label-Administrative Level 4"]'
    input_questionnaire_months_displaced_h_f = 'span[data-cy="input-questionnaire_months_displaced_h_f"]'
    label_length_of_time_since_arrival = 'div[data-cy="label-LENGTH OF TIME SINCE ARRIVAL"]'
    input_questionnaire_fullname = 'span[data-cy="input-questionnaire_fullName"]'
    label_individual_full_name = 'div[data-cy="label-Member full name"]'
    input_questionnaire_birthdate = 'span[data-cy="input-questionnaire_birthDate"]'
    label_birth_date = 'div[data-cy="label-Birth Date"]'
    input_questionnaire_phoneno = 'span[data-cy="input-questionnaire_phoneNo"]'
    label_phone_number = 'div[data-cy="label-Phone Number"]'
    input_questionnaire_relationship = 'span[data-cy="input-questionnaire_relationship"]'
    empty_household_row = 'tr[data-cy="table-row"]'

    # Texts
    text_title = "New Feedback"
    text_category = "Feedback"
    text_look_up_household = "LOOK UP {}"
    text_look_up_individual = "LOOK UP {}"

    # Elements

    def get_title_page(self) -> WebElement:
        return self.wait_for(self.title_page)

    def get_label_category(self) -> WebElement:
        return self.wait_for(self.label_category)

    def get_select_issue_type(self) -> WebElement:
        return self.wait_for(self.select_issue_type)

    def get_button_cancel(self) -> WebElement:
        return self.wait_for(self.button_cancel)

    def get_button_back(self) -> WebElement:
        return self.wait_for(self.button_back)

    def get_button_next(self) -> WebElement:
        return self.wait_for(self.button_next)

    def get_options(self) -> list[WebElement]:
        return self.get_elements(self.option)

    def get_household_tab(self, tab_name: str = "GROUP") -> None:
        try:
            household_tab = self.get_elements(self.look_up_tabs_household)[0]
        except IndexError:
            sleep(1)
            household_tab = self.get_elements(self.look_up_tabs_household)[0]
        assert self.text_look_up_household.format(tab_name) in household_tab.text, household_tab.text
        return household_tab

    def get_individual_tab(self, tab_name: str = "MEMBER") -> WebElement:
        try:
            individual_tab = self.get_elements(self.look_up_tabs_individual, attempts=5)[1]
        except IndexError:
            sleep(1)
            individual_tab = self.get_elements(self.look_up_tabs_individual, attempts=5)[1]
        assert self.text_look_up_individual.format(tab_name) in individual_tab.text, individual_tab.text
        return individual_tab

    def get_household_table_rows(self, number: int) -> WebElement:
        self.get_elements(self.hh_radio_button)
        try:
            return self.get_elements(self.household_table_row, attempts=5)[number]
        except IndexError:
            sleep(1)
            return self.get_elements(self.household_table_row, attempts=5)[number]

    def get_individual_table_row(self, number: int) -> WebElement:
        self.get_elements(self.individual_radio_button)
        try:
            return self.get_elements(self.individual_table_row, attempts=5)[number]
        except IndexError:
            sleep(1)
            return self.get_elements(self.individual_table_row, attempts=5)[number]

    def get_received_consent(self) -> WebElement:
        return self.wait_for(self.received_consent)

    def get_error(self) -> WebElement:
        return self.wait_for(self.error)

    def get_description(self) -> WebElement:
        return self.wait_for(self.description)

    def get_div_description(self) -> WebElement:
        return self.wait_for(self.div_description)

    def get_comments(self) -> WebElement:
        return self.wait_for(self.comments)

    def get_input_language(self) -> WebElement:
        return self.wait_for(self.input_language)

    def get_input_area(self) -> WebElement:
        return self.wait_for(self.input_area)

    def get_admin_area_autocomplete(self) -> WebElement:
        return self.wait_for(self.admin_area_autocomplete)

    def select_area(self, name: str) -> None:
        self.get_admin_area_autocomplete().click()
        self.select_listbox_element(name)

    def get_issue_type(self) -> WebElement:
        return self.wait_for(self.issue_type)

    def get_input_issue_type(self) -> WebElement:
        return self.wait_for(self.input_issue_type)

    def get_programme_select(self) -> WebElement:
        return self.wait_for(self.programme_select)

    def select_programme(self, name: str) -> None:
        self.get_programme_select().click()
        self.select_listbox_element(name)

    def check_elements_on_page(self) -> None:
        assert self.text_title in self.get_title_page().text
        assert self.text_category in self.get_label_category().text
        self.get_select_issue_type()
        self.get_button_cancel()
        self.get_button_back()
        self.get_button_next()

    def choose_option_by_name(self, name: str) -> None:
        self.get_select_issue_type().click()
        self.select_listbox_element(name)

    def get_input_questionnaire_size(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_size)

    def get_label_household_size(self) -> WebElement:
        return self.wait_for(self.label_household_size)

    def get_input_questionnaire_malechildrencount(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_malechildrencount)

    def get_label_number_of_male_children(self) -> WebElement:
        return self.wait_for(self.label_number_of_male_children)

    def get_input_questionnaire_femalechildrencount(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_femalechildrencount)

    def get_label_number_of_female_children(self) -> WebElement:
        return self.wait_for(self.label_number_of_female_children)

    def get_input_questionnaire_childrendisabledcount(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_childrendisabledcount)

    def get_label_number_of_disabled_children(self) -> WebElement:
        return self.wait_for(self.label_number_of_disabled_children)

    def get_input_questionnaire_headofhousehold(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_headofhousehold)

    def get_label_head_of_household(self) -> WebElement:
        return self.wait_for(self.label_head_of_household)

    def get_input_questionnaire_countryorigin(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_countryorigin)

    def get_label_country_of_origin(self) -> WebElement:
        return self.wait_for(self.label_country_of_origin)

    def get_input_questionnaire_address(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_address)

    def get_label_address(self) -> WebElement:
        return self.wait_for(self.label_address)

    def get_input_questionnaire_village(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_village)

    def get_label_village(self) -> WebElement:
        return self.wait_for(self.label_village)

    def get_input_questionnaire_admin_1(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_admin1)

    def get_label_administrative_level_1(self) -> WebElement:
        return self.wait_for(self.label_administrative_level1)

    def get_input_questionnaire_admin_2(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_admin2)

    def get_label_administrative_level_2(self) -> WebElement:
        return self.wait_for(self.label_administrative_level2)

    def get_input_questionnaire_admin_3(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_admin3)

    def get_label_administrative_level_3(self) -> WebElement:
        return self.wait_for(self.label_administrative_level3)

    def get_input_questionnaire_admin_4(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_admin4)

    def get_label_administrative_level_4(self) -> WebElement:
        return self.wait_for(self.label_administrative_level4)

    def get_input_questionnaire_months_displaced_h_f(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_months_displaced_h_f)

    def get_label_length_of_time_since_arrival(self) -> WebElement:
        return self.wait_for(self.label_length_of_time_since_arrival)

    def get_input_questionnaire_fullname(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_fullname)

    def get_label_individual_full_name(self) -> WebElement:
        return self.wait_for(self.label_individual_full_name)

    def get_input_questionnaire_birthdate(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_birthdate)

    def get_label_birth_date(self) -> WebElement:
        return self.wait_for(self.label_birth_date)

    def get_input_questionnaire_phoneno(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_phoneno)

    def get_label_phone_number(self) -> WebElement:
        return self.wait_for(self.label_phone_number)

    def get_input_questionnaire_relationship(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_relationship)

    def get_label_relationship_to_hoh(self) -> WebElement:
        return self.wait_for(self.label_relationship_to_hoh)

    def get_input_consent(self) -> WebElement:
        return self.wait_for(self.inputConsent)

    def get_table_empty_row(self) -> None:
        self.wait_for_text("No results", self.empty_household_row)
