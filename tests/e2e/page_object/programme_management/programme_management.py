from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement


class ProgrammeManagement(BaseComponents):
    header_title = 'h5[data-cy="page-header-title"]'
    button_new_program = 'a[data-cy="button-new-program"]'
    input_programme_name = 'input[data-cy="input-name"]'
    label_programme_name = 'div[data-cy="input-programme-name"]'
    input_start_date = 'input[name="startDate"]'
    label_start_date = 'div[data-cy="date-picker-filter"]'
    input_end_date = 'input[name="endDate"]'
    label_end_date = 'input[data-cy="date-input-endDate"]'
    select_selector = 'div[data-cy="select-sector"]'
    label_selector = 'div[data-cy="input-sector"]'
    input_data_collecting_type = 'div[data-cy="input-data-collecting-type"]'
    label_data_collecting_type = 'div[data-cy="input-data-collecting-type"]'
    input_cash_plus = 'span[data-cy="input-cashPlus"]'
    input_description = 'textarea[data-cy="input-description"]'
    input_budget = 'input[data-cy="input-budget"]'
    input_administrative_areas_of_implementation = 'input[data-cy="input-administrativeAreasOfImplementation"]'
    input_population = 'input[data-cy="input-populationGoal"]'
    input_beneficiary_group = 'div[data-cy="input-beneficiary-group"]'
    input_freq_of_payment_one_off = '//*[@data-cy="input-frequency-of-payment"]/div[1]/div/span'
    input_freq_of_payment_regular = '//*[@data-cy="input-frequency-of-payment"]/div[2]/div/span'
    button_next = 'button[data-cy="button-next"]'
    button_back = 'button[data-cy="button-back"]'
    button_cancel = 'a[data-cy="button-cancel"]'
    button_save = 'button[data-cy="button-save"]'
    select_partner_access = 'div[data-cy="select-partnerAccess"]'
    button_add_partner = 'button[data-cy="button-add-partner"]'
    input_partner = 'div[data-cy="select-partners[0].id"]'
    button_delete = 'button[data-cy="button-delete"]'
    label_admin_area = '//*[@id="radioGroup-partners[0].areaAccess"]/div[2]/div/span'
    calendar_icon = 'button[data-cy="calendar-icon"]'
    calendar = "//*[@data-popper-placement]"
    calendar_month_year = 'div[role="presentation"]'
    calendar_change_month = 'button[title="Next month"]'
    calendar_days = "//*[@data-timestamp]"
    filters_search = '//*[@data-cy="filters-search"]/div/input'
    button_apply = 'button[data-cy="button-filters-clear"]'
    button_edit_program = 'button[data-cy="button-edit-program"]'
    select_edit_program_details = 'li[data-cy="menu-item-edit-details"]'
    select_edit_program_partners = 'li[data-cy="menu-item-edit-partners"]'
    select_options_container = 'ul[data-cy="select-options-container"]'
    input_programme_code = 'input[data-cy="input-programmeCode"]'
    table_row = 'tr[data-cy="table-row-{}"]'
    step_button_details = 'button[data-cy="step-button-details"]'
    step_button_time_series_fields = 'button[data-cy="step-button-time-series-fields"]'
    step_button_partners = 'button[data-cy="step-button-partners"]'
    title = 'h6[data-cy="title"]'
    description = 'div[data-cy="description"]'
    input_pdu_fields_object_label = 'input[data-cy="input-pduFields.{}.label"]'
    select_pdu_fields_object_pdu_data_subtype = 'div[data-cy="select-pduFields.{}.pduData.subtype"]'
    select_pdu_fields_object_pdu_data_number_of_rounds = 'div[data-cy="select-pduFields.{}.pduData.numberOfRounds"]'
    input_pdu_fields_rounds_names = 'input[data-cy="input-pduFields.{}.pduData.roundsNames.{}"]'
    button_add_time_series_field = 'button[data-cy="button-add-time-series-field"]'

    def get_step_button_details(self) -> WebElement:
        return self.wait_for(self.step_button_details)

    def get_step_button_time_series_fields(self) -> WebElement:
        return self.wait_for(self.step_button_time_series_fields)

    def get_step_button_partners(self) -> WebElement:
        return self.wait_for(self.step_button_partners)

    def get_title(self) -> WebElement:
        return self.wait_for(self.title)

    def get_description(self) -> WebElement:
        return self.wait_for(self.description)

    def get_input_pdu_fields_object_label(self, index: int) -> WebElement:
        locator = self.input_pdu_fields_object_label.format(index)
        return self.wait_for(locator)

    def get_select_pdu_fields_object_pdu_data_subtype(self, index: int) -> WebElement:
        locator = self.select_pdu_fields_object_pdu_data_subtype.format(index)
        return self.wait_for(locator)

    def get_select_pdu_fields_object_pdu_data_number_of_rounds(self, index: int) -> WebElement:
        locator = self.select_pdu_fields_object_pdu_data_number_of_rounds.format(index)
        return self.wait_for(locator)

    def get_input_pdu_fields_rounds_names(self, pdu_field_index: int, round_name_index: int) -> WebElement:
        locator = self.input_pdu_fields_rounds_names.format(pdu_field_index, round_name_index)
        return self.wait_for(locator)

    def get_button_add_time_series_field(self) -> WebElement:
        return self.wait_for(self.button_add_time_series_field)

    def get_calendar_icon(self) -> WebElement:
        return self.wait_for(self.calendar_icon)

    def get_calendar(self) -> WebElement:
        return self.wait_for(self.calendar, By.XPATH)

    def choose_area_admin1_by_name(self, name: str) -> WebElement:
        return self.wait_for(f"//*[contains(text(), '{name}')]/span", By.XPATH)

    def get_label_admin_area(self) -> WebElement:
        return self.wait_for(self.label_admin_area, By.XPATH)

    def get_row_by_program_name(self, program_name: str) -> WebElement:
        locator = f'tr[data-cy="table-row-{program_name}"]'
        self.wait_for(locator)
        return self.get_elements(locator)[0].text.split("\n")

    def get_access_to_program(self) -> WebElement:
        return self.wait_for(self.select_partner_access)

    def select_who_access_to_program(self, name: str) -> None:
        self.select_option_by_name(name)

    def get_select_options_container(self) -> WebElement:
        return self.wait_for(self.select_options_container)

    def get_button_add_partner(self) -> WebElement:
        return self.wait_for(self.button_add_partner)

    def get_button_delete(self) -> WebElement:
        return self.wait_for(self.button_delete)

    def get_button_delete_popup(self) -> WebElement:
        return self.wait_for("/html/body/div[2]/div[3]/div/div[3]/div/button[2]", By.XPATH)

    def get_input_partner(self) -> WebElement:
        return self.wait_for(self.input_partner)

    def choose_partner_option(self, option_name: str) -> None:
        # Todo: Change undefined to name of Partner
        self.get_input_partner().click()
        self.select_option_by_name(option_name)

    def get_input_programme_name(self) -> WebElement:
        return self.wait_for(self.input_programme_name)

    def get_label_programme_name(self) -> WebElement:
        return self.wait_for(self.label_programme_name)

    def get_input_cash_plus(self) -> WebElement:
        return self.wait_for(self.input_cash_plus)

    def get_input_freq_of_payment_one_off(self) -> WebElement:
        return self.wait_for(self.input_freq_of_payment_one_off, By.XPATH)

    def get_input_freq_of_payment_regular(self) -> WebElement:
        return self.wait_for(self.input_freq_of_payment_regular, By.XPATH)

    def get_input_start_date(self) -> WebElement:
        return self.wait_for(self.input_start_date)

    def choose_input_start_date_via_calendar(self, day: int) -> None:
        self.get(self.label_start_date).find_element(By.TAG_NAME, "button").click()
        self.get_calendar()
        # ToDo: Create additional waiting mechanism
        sleep(1)
        self.get_elements(self.calendar_days, By.XPATH)[day - 1].click()
        self.wait_for_disappear(self.calendar, By.XPATH)

    def choose_input_end_date_via_calendar(self, day: int) -> None:
        self.get_label_end_date().find_element(By.XPATH, "./..").find_element(By.TAG_NAME, "button").click()
        self.get_calendar()
        month = self.wait_for(self.calendar_month_year).text
        self.wait_for(self.calendar_change_month).click()
        for _ in range(50):
            next_month = self.wait_for(self.calendar_month_year).text
            sleep(0.1)
            if month != next_month:
                break
        self.get_elements(self.calendar_days, By.XPATH)[day - 1].click()
        self.wait_for_disappear(self.calendar, By.XPATH, timeout=120)

    def get_label_start_date(self) -> WebElement:
        return self.get_elements(self.label_start_date)[0]

    def get_input_end_date(self) -> WebElement:
        return self.wait_for(self.input_end_date)

    def get_label_end_date(self) -> WebElement:
        return self.wait_for(self.label_end_date)

    def get_button_next(self) -> WebElement:
        return self.wait_for(self.button_next)

    def get_button_back(self) -> WebElement:
        return self.wait_for(self.button_back)

    def get_button_cancel(self) -> WebElement:
        return self.wait_for(self.button_cancel)

    def get_button_save(self) -> WebElement:
        return self.wait_for(self.button_save)

    def choose_option_selector(self, option_name: str) -> None:
        self.wait_for(self.select_selector).click()
        self.select_option_by_name(option_name)

    def get_label_selector(self) -> WebElement:
        return self.wait_for(self.label_selector)

    def choose_option_data_collecting_type(self, option_name: str) -> None:
        self.wait_for(self.input_data_collecting_type).click()
        self.select_option_by_name(option_name)

    def get_label_data_collecting_type(self) -> WebElement:
        return self.wait_for(self.label_data_collecting_type)

    def get_header_title(self) -> WebElement:
        return self.wait_for(self.header_title)

    def get_button_new_program(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector(\"div[data-cy='main-content']\")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.wait_for(self.button_new_program)

    def fill_filters_search(self, filter_text: str) -> None:
        self.wait_for(self.filters_search, By.XPATH).send_keys(filter_text)
        # ToDo: Delete sleep
        sleep(1)
        self.wait_for(self.filters_search, By.XPATH).send_keys(Keys.ENTER)

    def get_button_apply(self) -> WebElement:
        return self.wait_for(self.button_apply)

    def get_button_edit_program(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector(\"div[data-cy='main-content']\")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.wait_for(self.button_edit_program)

    def get_select_edit_program_details(self) -> WebElement:
        return self.wait_for(self.select_edit_program_details)

    def get_select_edit_program_partners(self) -> WebElement:
        return self.wait_for(self.select_edit_program_partners)

    def get_input_programme_code(self) -> WebElement:
        return self.wait_for(self.input_programme_code)

    def get_input_description(self) -> WebElement:
        return self.wait_for(self.input_description)

    def get_input_budget(self) -> WebElement:
        return self.wait_for(self.input_budget)

    def get_input_administrative_areas_of_implementation(self) -> WebElement:
        return self.wait_for(self.input_administrative_areas_of_implementation)

    def get_input_population(self) -> WebElement:
        return self.wait_for(self.input_population)

    def get_input_beneficiary_group(self) -> WebElement:
        return self.wait_for(self.input_beneficiary_group)

    def get_table_row_by_program_name(self, program_name: str) -> WebElement:
        return self.wait_for(self.table_row.format(program_name))

    def click_nav_programme_management(self) -> None:
        for _ in range(150):
            try:
                self.wait_for(self.nav_programme_management).click()
                self.wait_for(self.header_title)
                self.wait_for_text("Programme Management", self.header_title)
                break
            except BaseException:
                sleep(0.1)
        else:
            raise NoSuchElementException(
                "Could not locate page with title 'Programme Management' after multiple attempts."
            )
