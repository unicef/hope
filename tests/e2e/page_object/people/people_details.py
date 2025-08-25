from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class PeopleDetails(BaseComponents):
    page_header_container = 'div[data-cy="page-header-container"]'
    page_header_title = 'h5[data-cy="page-header-title"]'
    label_full_name = 'div[data-cy="label-Full Name"]'
    label_given_name = 'div[data-cy="label-Given Name"]'
    label_middle_name = 'div[data-cy="label-Middle Name"]'
    label_family_name = 'div[data-cy="label-Family Name"]'
    label_gender = 'div[data-cy="label-Gender"]'
    label_age = 'div[data-cy="label-Age"]'
    label_date_of_birth = 'div[data-cy="label-Date of Birth"]'
    label_estimated_date_of_birth = 'div[data-cy="label-Estimated Date of Birth"]'
    label_marital_status = 'div[data-cy="label-Marital Status"]'
    label_work_status = 'div[data-cy="label-Work Status"]'
    label_pregnant = 'div[data-cy="label-Pregnant"]'
    label_role = 'div[data-cy="label-Role"]'
    label_preferred_language = 'div[data-cy="label-Preferred language"]'
    label_residence_status = 'div[data-cy="label-Residence Status"]'
    label_country = 'div[data-cy="label-Country"]'
    label_country_of_origin = 'div[data-cy="label-Country of Origin"]'
    label_address = 'div[data-cy="label-Address"]'
    label_vilage = 'div[data-cy="label-Vilage"]'
    label_zip_code = 'div[data-cy="label-Zip Code"]'
    label_administrative_level_1 = 'div[data-cy="label-Administrative Level 1"]'
    label_administrative_level_2 = 'div[data-cy="label-Administrative Level 2"]'
    label_administrative_level_3 = 'div[data-cy="label-Administrative Level 3"]'
    label_administrative_level_4 = 'div[data-cy="label-Administrative Level 4"]'
    label_geolocation = 'div[data-cy="label-Geolocation"]'
    label_data_collecting_type = 'div[data-cy="label-Data Collecting Type"]'
    label_observed_disabilities = 'div[data-cy="label-Observed disabilities"]'
    label_seeing_disability_severity = 'div[data-cy="label-Seeing disability severity"]'
    label_hearing_disability_severity = 'div[data-cy="label-Hearing disability severity"]'
    label_physical_disability_severity = 'div[data-cy="label-Physical disability severity"]'
    label_remembering_or_concentrating_disability_severity = (
        'div[data-cy="label-Remembering or concentrating disability severity"]'
    )
    label_self_care_disability_severity = 'div[data-cy="label-Self-care disability severity"]'
    label_communicating_disability_severity = 'div[data-cy="label-Communicating disability severity"]'
    label_disability = 'div[data-cy="label-Disability"]'
    label_birth_certificate = 'div[data-cy="label-Birth Certificate"]'
    label_issued = 'div[data-cy="label-issued"]'
    label_driver_license = 'div[data-cy = "label-DriverLicense"]'
    label_electoral_card = 'div[data-cy="label-Electoral Card"]'
    label_national_passport = 'div[data-cy="label-National Passport"]'
    label_national_id = 'div[data-cy="label-National ID"]'
    label_unhcr_id = 'div[data-cy="label-UNHCR ID"]'
    label_wfp_id = 'div[data-cy="label-WFP ID"]'
    label_email = 'div[data-cy="label-Email"]'
    label_phone_number = 'div[data-cy="label-Phone Number"]'
    label_alternative_phone_number = 'div[data-cy="label-Alternative Phone Number"]'
    label_date_of_last_screening_against_sanctions_list = (
        'div[data-cy="label-Date of last screening against sanctions list"]'
    )
    label_linked_grievances = 'div[data-cy="label-Linked Grievances"]'
    label_wallet_name = 'div[data-cy="label-Wallet Name"]'
    label_blockchain_name = 'div[data-cy="label-Blockchain Name"]'
    label_wallet_address = 'div[data-cy="label-Wallet Address"]'
    label_cash_received = 'div[data-cy="label-Cash received"]'
    label_total_cash_received = 'div[data-cy="label-Total Cash Received"]'
    table_title = 'h6[data-cy="table-title"]'
    table_label = 'span[data-cy="table-label"]'
    status_container = 'div[data-cy="status-container"]'
    table_pagination = 'div[data-cy="table-pagination"]'
    label_source = 'div[data-cy="label-Source"]'
    label_import_name = 'div[data-cy="label-Import name"]'
    label_registration_date = 'div[data-cy="label-Registration Date"]'
    label_user_name = 'div[data-cy="label-User name"]'

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_page_header_title(self) -> WebElement:
        return self.wait_for(self.page_header_title)

    def get_label_full_name(self) -> WebElement:
        return self.wait_for(self.label_full_name)

    def get_label_given_name(self) -> WebElement:
        return self.wait_for(self.label_given_name)

    def get_label_middle_name(self) -> WebElement:
        return self.wait_for(self.label_middle_name)

    def get_label_family_name(self) -> WebElement:
        return self.wait_for(self.label_family_name)

    def get_label_gender(self) -> WebElement:
        return self.wait_for(self.label_gender)

    def get_label_age(self) -> WebElement:
        return self.wait_for(self.label_age)

    def get_label_date_of_birth(self) -> WebElement:
        return self.wait_for(self.label_date_of_birth)

    def get_label_estimated_date_of_birth(self) -> WebElement:
        return self.wait_for(self.label_estimated_date_of_birth)

    def get_label_marital_status(self) -> WebElement:
        return self.wait_for(self.label_marital_status)

    def get_label_work_status(self) -> WebElement:
        return self.wait_for(self.label_work_status)

    def get_label_pregnant(self) -> WebElement:
        return self.wait_for(self.label_pregnant)

    def get_label_role(self) -> WebElement:
        return self.wait_for(self.label_role)

    def get_label_preferred_language(self) -> WebElement:
        return self.wait_for(self.label_preferred_language)

    def get_label_residence_status(self) -> WebElement:
        return self.wait_for(self.label_residence_status)

    def get_label_country(self) -> WebElement:
        return self.wait_for(self.label_country)

    def get_label_country_of_origin(self) -> WebElement:
        return self.wait_for(self.label_country_of_origin)

    def get_label_address(self) -> WebElement:
        return self.wait_for(self.label_address)

    def get_label_vilage(self) -> WebElement:
        return self.wait_for(self.label_vilage)

    def get_label_zip_code(self) -> WebElement:
        return self.wait_for(self.label_zip_code)

    def get_label_administrative_level_1(self) -> WebElement:
        return self.wait_for(self.label_administrative_level_1)

    def get_label_administrative_level_2(self) -> WebElement:
        return self.wait_for(self.label_administrative_level_2)

    def get_label_administrative_level_3(self) -> WebElement:
        return self.wait_for(self.label_administrative_level_3)

    def get_label_administrative_level_4(self) -> WebElement:
        return self.wait_for(self.label_administrative_level_4)

    def get_label_geolocation(self) -> WebElement:
        return self.wait_for(self.label_geolocation)

    def get_label_data_collecting_type(self) -> WebElement:
        return self.wait_for(self.label_data_collecting_type)

    def get_label_observed_disabilities(self) -> WebElement:
        return self.wait_for(self.label_observed_disabilities)

    def get_label_seeing_disability_severity(self) -> WebElement:
        return self.wait_for(self.label_seeing_disability_severity)

    def get_label_hearing_disability_severity(self) -> WebElement:
        return self.wait_for(self.label_hearing_disability_severity)

    def get_label_physical_disability_severity(self) -> WebElement:
        return self.wait_for(self.label_physical_disability_severity)

    def get_label_remembering_or_concentrating_disability_severity(self) -> WebElement:
        return self.wait_for(self.label_remembering_or_concentrating_disability_severity)

    def get_label_self_care_disability_severity(self) -> WebElement:
        return self.wait_for(self.label_self_care_disability_severity)

    def get_label_communicating_disability_severity(self) -> WebElement:
        return self.wait_for(self.label_communicating_disability_severity)

    def get_label_disability(self) -> WebElement:
        return self.wait_for(self.label_disability)

    def get_label_birth_certificate(self) -> WebElement:
        return self.wait_for(self.label_birth_certificate)

    def get_label_issued(self) -> WebElement:
        return self.wait_for(self.label_issued)

    def get_label_driver_license(self) -> WebElement:
        return self.wait_for(self.label_driver_license)

    def get_label_electoral_card(self) -> WebElement:
        return self.wait_for(self.label_electoral_card)

    def get_label_national_passport(self) -> WebElement:
        return self.wait_for(self.label_national_passport)

    def get_label_national_id(self) -> WebElement:
        return self.wait_for(self.label_national_id)

    def get_label_unhcr_id(self) -> WebElement:
        return self.wait_for(self.label_unhcr_id)

    def get_label_wfp_id(self) -> WebElement:
        return self.wait_for(self.label_wfp_id)

    def get_label_email(self) -> WebElement:
        return self.wait_for(self.label_email)

    def get_label_phone_number(self) -> WebElement:
        return self.wait_for(self.label_phone_number)

    def get_label_alternative_phone_number(self) -> WebElement:
        return self.wait_for(self.label_alternative_phone_number)

    def get_label_date_of_last_screening_against_sanctions_list(self) -> WebElement:
        return self.wait_for(self.label_date_of_last_screening_against_sanctions_list)

    def get_label_linked_grievances(self) -> WebElement:
        return self.wait_for(self.label_linked_grievances)

    def get_label_wallet_name(self) -> WebElement:
        return self.wait_for(self.label_wallet_name)

    def get_label_blockchain_name(self) -> WebElement:
        return self.wait_for(self.label_blockchain_name)

    def get_label_wallet_address(self) -> WebElement:
        return self.wait_for(self.label_wallet_address)

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

    def get_label_source(self) -> WebElement:
        return self.wait_for(self.label_source)

    def get_label_import_name(self) -> WebElement:
        return self.wait_for(self.label_import_name)

    def get_label_registration_date(self) -> WebElement:
        return self.wait_for(self.label_registration_date)

    def get_label_user_name(self) -> WebElement:
        return self.wait_for(self.label_user_name)
