from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class HouseholdsDetails(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    label_household_size = 'div[data-cy="label-Items Group Size"]'
    label_residence_status = 'div[data-cy="label-Residence Status"]'
    label_head_of_household = 'div[data-cy="label-Head of Items Group"]'
    label_female_child_headed_household = 'div[data-cy="label-FEMALE CHILD HEADED ITEMS GROUPS"]'
    label_child_headed_household = 'div[data-cy="label-CHILD HEADED ITEMS GROUP"]'
    label_country = 'div[data-cy="label-Country"]'
    label_country_of_origin = 'div[data-cy="label-Country of Origin"]'
    label_address = 'div[data-cy="label-Address"]'
    label_village = 'div[data-cy="label-Village"]'
    label_zip_code = 'div[data-cy="label-Zip code"]'
    label_administrative_level1 = 'div[data-cy="label-Administrative Level 1"]'
    label_administrative_level2 = 'div[data-cy="label-Administrative Level 2"]'
    label_administrative_level3 = 'div[data-cy="label-Administrative Level 3"]'
    label_administrative_level4 = 'div[data-cy="label-Administrative Level 4"]'
    label_geolocation = 'div[data-cy="label-Geolocation"]'
    label_unhcr_case_id = 'div[data-cy="label-UNHCR CASE ID"]'
    label_length_of_time_since_arrival = 'div[data-cy="label-LENGTH OF TIME SINCE ARRIVAL"]'
    label_number_of_times_displaced = 'div[data-cy="label-NUMBER OF TIMES DISPLACED"]'
    label_is_this_a_returnee_household = 'div[data-cy="label-IS THIS A RETURNEE ITEMS GROUP?"]'
    label_linked_grievances = 'div[data-cy="label-Linked Grievances"]'
    label_data_collecting_type = 'div[data-cy="label-Data Collecting Type"]'
    label_cash_received = 'div[data-cy="label-Cash received"]'
    label_total_cash_received = 'div[data-cy="label-Total Cash Received"]'
    table_title = 'h6[data-cy="table-title"]'
    table_label = 'span[data-cy="table-label"]'
    status_container = 'div[data-cy="status-container"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    table_row = 'tr[data-cy="table-row"]'
    label_source = 'div[data-cy="label-Source"]'
    label_import_name = 'div[data-cy="label-Import name"]'
    label_registration_date = 'div[data-cy="label-Registration Date"]'
    label_user_name = 'div[data-cy="label-User name"]'
    row05 = '[data-cy="row05"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_label_household_size(self) -> WebElement:
        return self.wait_for(self.label_household_size)

    def get_label_residence_status(self) -> WebElement:
        return self.wait_for(self.label_residence_status)

    def get_label_head_of_household(self) -> WebElement:
        return self.wait_for(self.label_head_of_household)

    def get_label_female_child_headed_household(self) -> WebElement:
        return self.wait_for(self.label_female_child_headed_household)

    def get_label_child_headed_household(self) -> WebElement:
        return self.wait_for(self.label_child_headed_household)

    def get_label_country(self) -> WebElement:
        return self.wait_for(self.label_country)

    def get_label_country_of_origin(self) -> WebElement:
        return self.wait_for(self.label_country_of_origin)

    def get_label_address(self) -> WebElement:
        return self.wait_for(self.label_address)

    def get_label_village(self) -> WebElement:
        return self.wait_for(self.label_village)

    def get_label_zip_code(self) -> WebElement:
        return self.wait_for(self.label_zip_code)

    def get_label_administrative_level_1(self) -> WebElement:
        return self.wait_for(self.label_administrative_level1)

    def get_label_administrative_level_2(self) -> WebElement:
        return self.wait_for(self.label_administrative_level2)

    def get_label_administrative_level_3(self) -> WebElement:
        return self.wait_for(self.label_administrative_level3)

    def get_label_administrative_level_4(self) -> WebElement:
        return self.wait_for(self.label_administrative_level4)

    def get_label_geolocation(self) -> WebElement:
        return self.wait_for(self.label_geolocation)

    def get_label_unhcr_case_id(self) -> WebElement:
        return self.wait_for(self.label_unhcr_case_id)

    def get_label_length_of_time_since_arrival(self) -> WebElement:
        return self.wait_for(self.label_length_of_time_since_arrival)

    def get_label_number_of_times_displaced(self) -> WebElement:
        return self.wait_for(self.label_number_of_times_displaced)

    def get_label_is_this_a_returnee_household(self) -> WebElement:
        return self.wait_for(self.label_is_this_a_returnee_household)

    def get_label_linked_grievances(self) -> WebElement:
        return self.wait_for(self.label_linked_grievances)

    def get_label_data_collecting_type(self) -> WebElement:
        return self.wait_for(self.label_data_collecting_type)

    def get_label_cash_received(self) -> WebElement:
        return self.wait_for(self.label_cash_received)

    def get_label_total_cash_received(self) -> WebElement:
        return self.wait_for(self.label_total_cash_received)

    def get_table_title(self) -> WebElement:
        return self.wait_for(self.table_title)

    def get_table_label(self) -> WebElement:
        return self.wait_for(self.table_label)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_table_row(self) -> WebElement:
        return self.wait_for(self.table_row)

    def get_label_source(self) -> WebElement:
        return self.wait_for(self.label_source)

    def get_label_import_name(self) -> WebElement:
        return self.wait_for(self.label_import_name)

    def get_label_registration_date(self) -> WebElement:
        return self.wait_for(self.label_registration_date)

    def get_label_user_name(self) -> WebElement:
        return self.wait_for(self.label_user_name)

    def get_row05(self) -> WebElement:
        return self.wait_for(self.row05)
