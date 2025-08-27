from time import sleep

from e2e.page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class NewTicket(BaseComponents):
    # Locators
    title = 'h5[data-cy="page-header-title"]'
    select_category = 'div[data-cy="select-category"]'
    issue_type = 'div[data-cy="select-issueType"]'
    button_next = 'button[data-cy="button-submit"]'
    status_options = 'li[role="option"]'
    look_up_individual_tab = 'button[data-cy="look-up-individual"]'
    look_up_household_tab = 'button[data-cy="look-up-household"]'
    household_table_row = 'tr[data-cy="household-table-row"]'
    individual_table_row = 'tr[data-cy="individual-table-row"]'
    table_row = '[data-cy="table-row"]'
    received_consent = 'span[data-cy="input-consent"]'
    individual_id = 'div[data-cy="label-INDIVIDUAL ID"]'
    household_id = 'div[data-cy="label-HOUSEHOLD ID"]'
    issue_type_label = 'div[data-cy="label-Issue Type"]'
    category = 'div[data-cy="label-Category"]'
    description = 'textarea[data-cy="input-description"]'
    comments = 'textarea[data-cy="input-comments"]'
    who_answers_phone = 'input[data-cy="input-individualData.whoAnswersPhone"]'
    who_answers_alt_phone = 'input[data-cy="input-individualData.whoAnswersAltPhone"]'
    role = 'div[data-cy="select-individualData.role"]'
    relationship = 'div[data-cy="select-individualData.relationship"]'
    phone_no = 'input[data-cy="input-individualData.phoneNo"]'
    middle_name = 'input[data-cy="input-individualData.middleName"]'
    marital_status = 'div[data-cy="select-individualData.maritalStatus"]'
    pregnant = 'div[data-cy="select-individualData.pregnant"]'
    disability = 'div[data-cy="select-individualData.disability"]'
    email = 'input[data-cy="input-individualData.email"]'
    physical_disability = 'div[data-cy="select-individualData.physicalDisability"]'
    seeing_disability = 'div[data-cy="select-individualData.seeingDisability"]'
    memory_disability = 'div[data-cy="select-individualData.memoryDisability"]'
    hearing_disability = 'div[data-cy="select-individualData.hearingDisability"]'
    comms_disability = 'div[data-cy="select-individualData.commsDisability"]'
    given_name = 'input[data-cy="input-individualData.givenName"]'
    gender = 'div[data-cy="select-individualData.sex"]'
    full_name = 'input[data-cy="input-individualData.fullName"]'
    family_name = 'input[data-cy="input-individualData.familyName"]'
    estimated_birth_date = 'div[data-cy="select-individualData.estimatedBirthDate"]'
    work_status = 'div[data-cy="select-individualData.workStatus"]'
    observed_disability = 'div[data-cy="select-individualData.observedDisability"]'
    selfcare_disability = 'div[data-cy="select-individualData.selfcareDisability"]'
    birth_date = 'input[data-cy="date-input-individualData.birthDate"]'
    phone_no_alternative = 'input[data-cy="input-individualData.phoneNoAlternative"]'
    add_document = 'button[type="button"]'
    look_up_button = 'div[data-cy="look-up-button"]'
    checkbox = 'tr[role="checkbox"]'
    select_urgency = 'div[data-cy="select-urgency"]'
    select_priority = 'div[data-cy="select-priority"]'
    input_language = 'textarea[data-cy="input-language"]'
    input_area = 'input[data-cy="input-area"]'
    admin_area_autocomplete = 'div[data-cy="admin-area-autocomplete"]'
    option_undefined = 'li[data-cy="select-option-undefined"]'
    option_zero = 'li[data-cy="select-option-0"]'
    option_one = 'li[data-cy="select-option-1"]'
    label_category_description = 'div[data-cy="label-Category Description"]'
    label_issue_type_description = 'div[data-cy="label-Issue Type Description"]'
    select_field_name = 'div[data-cy="select-householdDataUpdateFields[0].fieldName"]'
    individual_field_name = 'div[data-cy="select-individualDataUpdateFields[{}].fieldName"]'
    input_value = 'input[data-cy="input-householdDataUpdateFields[0].fieldValue"]'
    partner = 'div[data-cy="select-partner"]'
    table_pagination = '[data-cy="table-pagination"]'
    input_description = 'textarea[data-cy="input-description"]'
    input_comments = 'textarea[data-cy="input-comments"]'
    select_program = 'div[data-cy="select-program"]'
    input_individual_data_phone_no_alternative = 'input[data-cy="input-individualDataPhoneNoAlternative"]'
    date_picker_filter = 'div[data-cy="date-picker-filter"]'
    input_individualdata_blockchainname = 'input[data-cy="input-individualData.blockchainName"]'
    select_individualdata_selfcaredisability = 'div[data-cy="select-individualData.selfcareDisability"]'
    select_individualdata_observeddisability = 'div[data-cy="select-individualData.observedDisability"]'
    select_individualdata_workstatus = 'div[data-cy="select-individualData.workStatus"]'
    select_individualdata_estimatedbirthdate = 'div[data-cy="select-individualData.estimatedBirthDate"]'
    input_individualdata_familyname = 'input[data-cy="input-individualData.familyName"]'
    input_individualdata_fullname = 'input[data-cy="input-individualData.fullName"]'
    select_individualdata_sex = 'div[data-cy="select-individualData.sex"]'
    input_individualdata_givenname = 'input[data-cy="input-individualData.givenName"]'
    select_individualdata_commsdisability = 'div[data-cy="select-individualData.commsDisability"]'
    select_individualdata_hearingdisability = 'div[data-cy="select-individualData.hearingDisability"]'
    select_individualdata_memorydisability = 'div[data-cy="select-individualData.memoryDisability"]'
    select_individualdata_seeingdisability = 'div[data-cy="select-individualData.seeingDisability"]'
    select_individualdata_physicaldisability = 'div[data-cy="select-individualData.physicalDisability"]'
    input_individualdata_email = 'input[data-cy="input-individualData.email"]'
    select_individualdata_disability = 'div[data-cy="select-individualData.disability"]'
    select_individualdata_pregnant = 'div[data-cy="select-individualData.pregnant"]'
    select_individualdata_maritalstatus = 'div[data-cy="select-individualData.maritalStatus"]'
    input_individualdata_middlename = 'input[data-cy="input-individualData.middleName"]'
    input_individualdata_phoneno = 'input[data-cy="input-individualData.phoneNo"]'
    select_individualdata_preferredlanguage = 'div[data-cy="select-individualData.preferredLanguage"]'
    select_individualdata_relationship = 'div[data-cy="select-individualData.relationship"]'
    select_individualdata_role = 'div[data-cy="select-individualData.role"]'
    input_individualdata_walletaddress = 'input[data-cy="input-individualData.walletAddress"]'
    input_individualdata_walletname = 'input[data-cy="input-individualData.walletName"]'
    input_individualdata_whoanswersaltphone = 'input[data-cy="input-individualData.whoAnswersAltPhone"]'
    input_individualdata_whoanswersphone = 'input[data-cy="input-individualData.whoAnswersPhone"]'
    select_householddataupdatefields_fieldname = 'div[data-cy="select-householdDataUpdateFields[{}].fieldName"]'
    button_add_new_field = 'button[data-cy="button-add-new-field"]'
    input_individual_data = 'div[data-cy="input-individual-data-{}"]'  # Gender
    checkbox_select_all = 'span[data-cy="checkbox-select-all"]'
    button_submit = 'button[data-cy="button-submit"]'
    linked_ticket_id = 'span[data-cy="linked-ticket-id"]'
    linked_ticket = '[data-cy="linked-ticket"]'
    button_edit = 'svg[data-cy="button-edit"]'
    button_delete = 'svg[data-cy="button-delete"]'
    add_documentation = 'button[data-cy="add-documentation"]'
    input_documentation_name = 'input[data-cy="input-documentation[{}].name"]'
    input_file = 'input[type="file"]'
    input_questionnaire_size = 'span[data-cy="input-questionnaire_size"]'
    label_household_size = 'div[data-cy="label-Group Size"]'
    input_questionnaire_malechildrencount = 'span[data-cy="input-questionnaire_maleChildrenCount"]'
    label_number_of_male_children = 'div[data-cy="label-Number of Male Children"]'
    input_questionnaire_femalechildrencount = 'span[data-cy="input-questionnaire_femaleChildrenCount"]'
    label_number_of_female_children = 'div[data-cy="label-Number of Female Children"]'
    input_questionnaire_childrendisabledcount = 'span[data-cy="input-questionnaire_childrenDisabledCount"]'
    label_number_of_disabled_children = 'div[data-cy="label-Number of Disabled Children"]'
    input_questionnaire_headofhousehold = 'span[data-cy="input-questionnaire_headOfHousehold"]'
    label_head_of_household = 'div[data-cy="label-Head of Group"]'
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
    input_questionnaire_sex = 'span[data-cy="input-questionnaire_sex"]'
    label_gender = 'div[data-cy="label-Gender"]'
    input_questionnaire_phoneno = 'span[data-cy="input-questionnaire_phoneNo"]'
    label_phone_number = 'div[data-cy="label-Phone Number"]'
    input_questionnaire_relationship = 'span[data-cy="input-questionnaire_relationship"]'
    label_relationship_to_hoh = 'div[data-cy="label-Relationship to Head of Group"]'

    # Texts
    text_look_up_household = "LOOK UP HOUSEHOLD"
    text_look_up_individual = "LOOK UP INDIVIDUAL"
    text_title = "New Ticket"
    text_next = "Next"
    text_category_description = {
        "Data Change": "A grievance that is submitted to change in the households or beneficiary status",
        "Grievance Complaint": "A grievance submitted to express dissatisfaction made about an individual, "
        "UNICEF/NGO/Partner/Vendor, about a received service or about the process itself",
        "Referral": "A grievance submitted to direct the reporting individual to another service provider/actor to "
        "provide support/help that is beyond the scope of work of UNICEF",
        "Sensitive Grievance": "A grievance that shall be treated with sensitivity or which individual wishes to "
        "submit anonymously",
    }

    text_issue_type_description = {
        "Add Individual": "A grievance submitted to specifically change in the households to add an individual",
        "Household Data Update": "A grievance submitted to change in the household data "
        "(Address, number of individuals, etc.)",
        "Individual Data Update": "A grievance submitted to change in the household’s individuals data "
        "(Family name, full name, birth date, etc.)",
        "Withdraw Individual": "A grievance submitted to remove an individual from within a household",
        "Withdraw Household": "A grievance submitted to remove a household",
        "Payment Related Complaint": "A grievance submitted to complain about payments",
        "FSP Related Complaint": "A grievance to report dissatisfaction on service provided "
        "by a Financial Service Providers",
        "Registration Related Complaint": "A grievance submitted on issues/difficulties encountered during "
        "the registration of beneficiaries",
        "Other Complaint": "Other complaints that do not fall into specific predefined categories",
        "Partner Related Complaint": "A grievance submitted on issues encountered by an implementing partner",
        "Bribery, corruption or kickback": "Grievance on illicit payments or favors in exchange for personal gain",
        "Data breach": "Grievance on unauthorized access or disclosure of beneficiary data",
        "Conflict of interest": "Grievance on deception or falsification for personal gain",
        "Fraud and forgery": "Grievance related to identity theft or impersonation to benefit "
        "from someone’s entitlements",
        "Fraud involving misuse of programme funds by third party": "Grievance on forgery actions undertaken "
        "by third parties’ individuals",
        "Gross mismanagement": "Grievance on mismanagement leading to significant negative impact",
        "Harassment and abuse of authority": "Grievance related to intimidation, mistreatment, or abuse "
        "by those in authority",
        "Inappropriate staff conduct": "Grievance related to improper behavior or actions (physical or verbal) "
        "by program staff",
        "Miscellaneous": "Other issues not falling into specific predefined categories",
        "Personal disputes": "Grievance on conflicts or disagreements between individuals",
        "Sexual harassment and sexual exploitation": "Grievance on unwanted advances, abuse, or exploitation "
        "of a sexual nature",
        "Unauthorized use, misuse or waste of UNICEF property or funds": "Grievance on improper or unauthorized "
        "handling or disposal of assets/funds",
    }

    # Elements
    def get_title(self) -> WebElement:
        return self.wait_for(self.title)

    def get_select_category(self) -> WebElement:
        return self.wait_for(self.select_category)

    def get_issue_type(self) -> WebElement:
        return self.wait_for(self.issue_type)

    def get_button_next(self) -> WebElement:
        return self.wait_for(self.button_next)

    def get_option(self) -> WebElement:
        return self.wait_for(self.status_options)

    def get_household_tab(self) -> WebElement:
        return self.wait_for(self.look_up_household_tab)

    def get_individual_tab(self) -> WebElement:
        return self.wait_for(self.look_up_individual_tab)

    def get_household_table_rows(self, number: int) -> WebElement:
        self.wait_for(self.household_table_row)
        return self.get_elements(self.household_table_row)[number]

    def get_individual_table_rows(self, number: int) -> WebElement:
        self.wait_for(self.individual_table_row)
        return self.get_elements(self.individual_table_row)[number]

    def get_received_consent(self) -> WebElement:
        return self.wait_for(self.received_consent, timeout=100)

    def get_description(self) -> WebElement:
        return self.wait_for(self.description)

    def get_individual_id(self) -> WebElement:
        return self.wait_for(self.individual_id)

    def get_household_id(self) -> WebElement:
        return self.wait_for(self.household_id)

    def get_issue_type_label(self) -> WebElement:
        return self.wait_for(self.issue_type_label)

    def get_category(self) -> WebElement:
        return self.wait_for(self.category)

    def get_comments(self) -> WebElement:
        return self.wait_for(self.comments)

    def get_who_answers_phone(self) -> WebElement:
        return self.wait_for(self.who_answers_phone)

    def get_who_answers_alt_phone(self) -> WebElement:
        return self.wait_for(self.who_answers_alt_phone)

    def get_role(self) -> WebElement:
        return self.wait_for(self.role)

    def get_relationship(self) -> WebElement:
        return self.wait_for(self.relationship)

    def get_phone_no(self) -> WebElement:
        return self.wait_for(self.phone_no)

    def get_middle_name(self) -> WebElement:
        return self.wait_for(self.middle_name)

    def get_marital_status(self) -> WebElement:
        return self.wait_for(self.marital_status)

    def get_pregnant(self) -> WebElement:
        return self.wait_for(self.pregnant)

    def get_disability(self) -> WebElement:
        return self.wait_for(self.disability)

    def get_email(self) -> WebElement:
        return self.wait_for(self.email)

    def get_physical_disability(self) -> WebElement:
        return self.wait_for(self.physical_disability)

    def get_seeing_disability(self) -> WebElement:
        return self.wait_for(self.seeing_disability)

    def get_memory_disability(self) -> WebElement:
        return self.wait_for(self.memory_disability)

    def get_hearing_disability(self) -> WebElement:
        return self.wait_for(self.hearing_disability)

    def get_comms_disability(self) -> WebElement:
        return self.wait_for(self.comms_disability)

    def get_given_name(self) -> WebElement:
        return self.wait_for(self.given_name)

    def get_gender(self) -> WebElement:
        return self.wait_for(self.gender)

    def get_full_name(self) -> WebElement:
        return self.wait_for(self.full_name)

    def get_family_name(self) -> WebElement:
        return self.wait_for(self.family_name)

    def get_estimated_birth_date(self) -> WebElement:
        return self.wait_for(self.estimated_birth_date)

    def get_work_status(self) -> WebElement:
        return self.wait_for(self.work_status)

    def get_observed_disability(self) -> WebElement:
        return self.wait_for(self.observed_disability)

    def get_selfcare_disability(self) -> WebElement:
        return self.wait_for(self.selfcare_disability)

    def get_birth_date(self) -> WebElement:
        return self.wait_for(self.birth_date)

    def get_phone_no_alternative(self) -> WebElement:
        return self.wait_for(self.phone_no_alternative)

    def get_add_document(self) -> WebElement:
        return self.wait_for(self.add_document)

    def get_look_up_button(self) -> WebElement:
        return self.wait_for(self.look_up_button)

    def get_look_up_payment_record(self) -> [WebElement]:
        return self.get_elements(self.look_up_button)[1]

    def get_checkbox(self) -> WebElement:
        return self.wait_for(self.checkbox)

    def get_select_urgency(self) -> WebElement:
        return self.wait_for(self.select_urgency)

    def get_select_priority(self) -> WebElement:
        return self.wait_for(self.select_priority)

    def get_input_language(self) -> WebElement:
        return self.wait_for(self.input_language)

    def get_input_area(self) -> WebElement:
        return self.wait_for(self.input_area)

    def get_admin_area_autocomplete(self) -> WebElement:
        return self.wait_for(self.admin_area_autocomplete)

    def get_option_undefined(self) -> WebElement:
        return self.wait_for(self.option_undefined)

    def get_option_zero(self) -> WebElement:
        return self.wait_for(self.option_zero)

    def get_option_one(self) -> WebElement:
        return self.wait_for(self.option_one)

    def get_label_category_description(self) -> WebElement:
        return self.wait_for(self.label_category_description)

    def get_label_issue_type_description(self) -> WebElement:
        return self.wait_for(self.label_issue_type_description)

    def get_select_field_name(self) -> WebElement:
        return self.wait_for(self.select_field_name)

    def get_input_value(self) -> WebElement:
        return self.wait_for(self.input_value)

    def get_individual_field_name(self, index: int) -> WebElement:
        return self.wait_for(self.individual_field_name.format(str(index)))

    def get_partner(self) -> WebElement:
        return self.wait_for(self.partner)

    def get_table_pagination(self) -> WebElement:
        return self.wait_for(self.table_pagination)

    def get_table_row(self) -> WebElement:
        return self.wait_for(self.table_row)

    def wait_for_no_results(self) -> bool:
        for _ in range(15):
            if "No results" in self.get_table_row().text:
                return True
            sleep(1)
        return False

    def get_select_program(self) -> WebElement:
        return self.wait_for(self.select_program)

    def get_input_individual_data_phone_no_alternative(self) -> WebElement:
        return self.wait_for(self.input_individual_data_phone_no_alternative)

    def get_date_picker_filter(self) -> WebElement:
        return self.wait_for(self.date_picker_filter).find_element("tag name", "input")

    def get_input_individualdata_blockchainname(self) -> WebElement:
        return self.wait_for(self.input_individualdata_blockchainname)

    def get_select_individualdata_selfcaredisability(self) -> WebElement:
        return self.wait_for(self.select_individualdata_selfcaredisability)

    def get_select_individualdata_observeddisability(self) -> WebElement:
        return self.wait_for(self.select_individualdata_observeddisability)

    def get_select_individualdata_workstatus(self) -> WebElement:
        return self.wait_for(self.select_individualdata_workstatus)

    def get_select_individualdata_estimatedbirthdate(self) -> WebElement:
        return self.wait_for(self.select_individualdata_estimatedbirthdate)

    def get_input_individualdata_familyname(self) -> WebElement:
        return self.wait_for(self.input_individualdata_familyname)

    def get_input_individualdata_fullname(self) -> WebElement:
        return self.wait_for(self.input_individualdata_fullname)

    def get_select_individualdata_sex(self) -> WebElement:
        return self.wait_for(self.select_individualdata_sex)

    def get_input_individualdata_givenname(self) -> WebElement:
        return self.wait_for(self.input_individualdata_givenname)

    def get_select_individualdata_commsdisability(self) -> WebElement:
        return self.wait_for(self.select_individualdata_commsdisability)

    def get_select_individualdata_hearingdisability(self) -> WebElement:
        return self.wait_for(self.select_individualdata_hearingdisability)

    def get_select_individualdata_memorydisability(self) -> WebElement:
        return self.wait_for(self.select_individualdata_memorydisability)

    def get_select_individualdata_seeingdisability(self) -> WebElement:
        return self.wait_for(self.select_individualdata_seeingdisability)

    def get_select_individualdata_physicaldisability(self) -> WebElement:
        return self.wait_for(self.select_individualdata_physicaldisability)

    def get_input_individualdata_email(self) -> WebElement:
        return self.wait_for(self.input_individualdata_email)

    def get_select_individualdata_disability(self) -> WebElement:
        return self.wait_for(self.select_individualdata_disability)

    def get_select_individualdata_pregnant(self) -> WebElement:
        return self.wait_for(self.select_individualdata_pregnant)

    def get_select_individualdata_maritalstatus(self) -> WebElement:
        return self.wait_for(self.select_individualdata_maritalstatus)

    def get_input_individualdata_middlename(self) -> WebElement:
        return self.wait_for(self.input_individualdata_middlename)

    def get_input_individualdata_phoneno(self) -> WebElement:
        return self.wait_for(self.input_individualdata_phoneno)

    def get_select_individualdata_preferredlanguage(self) -> WebElement:
        return self.wait_for(self.select_individualdata_preferredlanguage)

    def get_select_individualdata_relationship(self) -> WebElement:
        return self.wait_for(self.select_individualdata_relationship)

    def get_select_individualdata_role(self) -> WebElement:
        return self.wait_for(self.select_individualdata_role)

    def get_input_individualdata_walletaddress(self) -> WebElement:
        return self.wait_for(self.input_individualdata_walletaddress)

    def get_input_individualdata_walletname(self) -> WebElement:
        return self.wait_for(self.input_individualdata_walletname)

    def get_input_individualdata_whoanswersaltphone(self) -> WebElement:
        return self.wait_for(self.input_individualdata_whoanswersaltphone)

    def get_input_individualdata_whoanswersphone(self) -> WebElement:
        return self.wait_for(self.input_individualdata_whoanswersphone)

    def get_button_add_new_field(self) -> WebElement:
        return self.wait_for(self.button_add_new_field)

    def get_select_householddataupdatefields_fieldname(self, index: int) -> WebElement:
        field = self.wait_for(self.select_householddataupdatefields_fieldname.format(index))
        return field.find_element(By.XPATH, "./..")

    def get_input_individual_data(self, typology: str) -> WebElement:
        return self.wait_for(self.input_individual_data.format(typology))

    def get_checkbox_select_all(self) -> WebElement:
        return self.wait_for(self.checkbox_select_all)

    def get_button_submit(self) -> WebElement:
        return self.get_elements(self.button_submit)[1]

    def get_linked_ticket_id(self) -> WebElement:
        return self.wait_for(self.linked_ticket_id)

    def get_linked_ticket(self) -> WebElement:
        return self.wait_for(self.linked_ticket)

    def get_button_edit(self) -> WebElement:
        return self.wait_for(self.button_edit)

    def get_button_delete(self) -> WebElement:
        return self.wait_for(self.button_delete)

    def get_add_documentation(self) -> WebElement:
        return self.wait_for(self.add_documentation)

    def get_input_documentation_name(self, index: int) -> WebElement:
        return self.wait_for(self.input_documentation_name.format(index))

    def get_input_file(self) -> WebElement:
        return self.wait_for(self.input_file)

    def get_input_questionnaire_size(self) -> WebElement:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
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

    def get_input_questionnaire_sex(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_sex)

    def get_label_gender(self) -> WebElement:
        return self.wait_for(self.label_gender)

    def get_input_questionnaire_phoneno(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_phoneno)

    def get_label_phone_number(self) -> WebElement:
        return self.wait_for(self.label_phone_number)

    def get_input_questionnaire_relationship(self) -> WebElement:
        return self.wait_for(self.input_questionnaire_relationship)

    def get_label_relationship_to_hoh(self) -> WebElement:
        return self.wait_for(self.label_relationship_to_hoh)
