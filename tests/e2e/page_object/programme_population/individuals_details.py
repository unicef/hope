from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class IndividualsDetails(BaseComponents):
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
    label_household_id = 'div[data-cy="label-Items Group ID"]'
    label_role = 'div[data-cy="label-Role"]'
    label_relationship_to_hoh = 'div[data-cy="label-Relationship to Head Of Items Group"]'
    label_preferred_language = 'div[data-cy="label-Preferred language"]'
    label_linked_households = 'div[data-cy="label-Linked Items Groups"]'
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
    label_birth_certificate = 'div[data-cy="label-BIRTH_CERTIFICATE"]'
    label_issued = 'div[data-cy="label-issued"]'
    label_drivers_license = 'div[data-cy="label-DRIVERS_LICENSE"]'
    label_electoral_card = 'div[data-cy="label-ELECTORAL_CARD"]'
    label_national_passport = 'div[data-cy="label-NATIONAL_PASSPORT"]'
    label_national_id = 'div[data-cy="label-NATIONAL_ID"]'
    label_unhcr_id = 'div[data-cy="label-UNHCR ID"]'
    label_wfp_id = 'div[data-cy="label-WFP ID"]'
    label_email = 'div[data-cy="label-Email"]'
    label_phone_number = 'div[data-cy="label-Phone Number"]'
    label_alternative_phone_number = 'div[data-cy="label-Alternative Phone Number"]'
    label_date_of_last_screening_against_sanctions_list = (
        'div[data-cy="label-Date of last screening against sanctions list"]'
    )
    label_linked_grievances = 'div[data-cy="label-Linked Grievances"]'
    label_school_enrolled = 'div[data-cy="label-school enrolled"]'
    label_school_enrolled_before = 'div[data-cy="label-school enrolled before"]'

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

    def get_label_household_id(self) -> WebElement:
        return self.wait_for(self.label_household_id)

    def get_label_role(self) -> WebElement:
        return self.wait_for(self.label_role)

    def get_label_relationship_to_hoh(self) -> WebElement:
        return self.wait_for(self.label_relationship_to_hoh)

    def get_label_preferred_language(self) -> WebElement:
        return self.wait_for(self.label_preferred_language)

    def get_label_linked_households(self) -> WebElement:
        return self.wait_for(self.label_linked_households)

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

    def get_label_drivers_license(self) -> WebElement:
        return self.wait_for(self.label_drivers_license)

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

    def get_label_school_enrolled(self) -> WebElement:
        return self.wait_for(self.label_school_enrolled)

    def get_label_school_enrolled_before(self) -> WebElement:
        return self.wait_for(self.label_school_enrolled_before)
