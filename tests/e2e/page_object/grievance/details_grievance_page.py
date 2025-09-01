from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class GrievanceDetailsPage(BaseComponents):
    # Locators
    page_header_container = 'div[data-cy="page-header-container"]'
    title = 'h5[data-cy="page-header-title"]'
    button_edit = 'a[data-cy="button-edit"]'
    button_set_in_progress = 'button[data-cy="button-set-to-in-progress"]'
    button_send_back = 'button[data-cy="button-send-back"]'
    button_close_ticket = 'button[data-cy="button-close-ticket"]'
    button_confirm = 'button[data-cy="button-confirm"]'
    button_assign_to_me = 'button[data-cy="button-assign-to-me"]'
    button_send_for_approval = 'button[data-cy="button-send-for-approval"]'
    button_approval = 'button[data-cy="button-approve"]'
    ticket_status = 'div[data-cy="label-Status"]'
    ticket_priority = 'div[data-cy="label-Priority"]'
    ticket_urgency = 'div[data-cy="label-Urgency"]'
    ticket_assigment = 'div[data-cy="label-Assigned to"]'
    ticket_category = 'div[data-cy="label-Category"]'
    label_issue_type = 'div[data-cy="label-Issue Type"]'
    ticket_household_id = 'div[data-cy="label-Household ID"]'
    ticket_target_id = 'div[data-cy="label-Target ID"]'
    ticket_individual_id = 'div[data-cy="label-Individual ID"]'
    ticket_payment_label = 'div[data-cy="label-Payment ID"]'
    label_payment_plan = 'div[data-cy="label-Payment Plan"]'
    label_payment_plan_verification = 'div[data-cy="label-Payment Plan Verification"]'
    label_programme = 'div[data-cy="label-Programme"]'
    ticket_category_by = 'div[data-cy="label-Created By"]'
    date_creation = 'div[data-cy="label-Date Created"]'
    last_modified_date = 'div[data-cy="label-Last Modified Date"]'
    administrative_level = 'div[data-cy="label-Administrative Level 2"]'
    area_village = 'div[data-cy="label-Area / Village / Pay point"]'
    languages_spoken = 'div[data-cy="label-Languages Spoken"]'
    documentation = 'div[data-cy="label-Grievance Supporting Documents"]'
    ticket_description = 'div[data-cy="label-Description"]'
    label_created_by = 'div[data-cy="label-Created By"]'
    comments = 'div[data-cy="label-Comments"]'
    create_linked_ticket = 'button[data-cy="button-create-linked-ticket"]'
    mark_duplicate = 'button[data-cy="button-mark-duplicate"]'
    cell_individual_id = 'th[data-cy="table-cell-individual-id"]'
    cell_household_id = 'th[data-cy="table-cell-household-id"]'
    cell_full_name = 'th[data-cy="table-cell-full-name"]'
    cell_gender = 'th[data-cy="table-cell-gender"]'
    cell_date_of_birth = 'th[data-cy="table-cell-date-of-birth"]'
    cell_similarity_score = 'th[data-cy="table-cell-similarity-score"]'
    cell_last_registration_date = 'th[data-cy="table-cell-last-registration-date"]'
    cell_doc_type = 'th[data-cy="table-cell-doc-type"]'
    cell_doc = 'th[data-cy="table-cell-doc-number"]'
    cell_admin_level2 = 'th[data-cy="table-cell-admin-level2"]'
    cell_village = 'th[data-cy="table-cell-village"]'
    new_note_field = 'textarea[data-cy="input-newNote"]'
    button_new_note = 'button[data-cy="button-add-note"]'
    label_languages_spoken = 'div[data-cy="label-Languages Spoken"]'
    label_documentation = 'div[data-cy="label-Grievance Supporting Documents"]'
    label_description = 'div[data-cy="label-Description"]'
    note_row = '[data-cy="note-row"]'
    note_name = '[data-cy="note-name"]'
    label_gender_up = 'div[data-cy="label-GENDER"]'
    label_role = 'div[data-cy="label-role"]'
    label_phone_no = 'div[data-cy="label-phone no"]'
    label_pregnant = 'div[data-cy="label-pregnant"]'
    label_full_name = 'div[data-cy="label-full name"]'
    label_birth_date = 'div[data-cy="label-birth date"]'
    label_disability = 'div[data-cy="label-disability"]'
    label_given_name = 'div[data-cy="label-given name"]'
    label_family_name = 'div[data-cy="label-family name"]'
    label_middle_name = 'div[data-cy="label-middle name"]'
    label_work_status = 'div[data-cy="label-work status"]'
    label_relationship = 'div[data-cy="label-relationship"]'
    label_marital_status = 'div[data-cy="label-marital status"]'
    label_comms_disability = 'div[data-cy="label-comms disability"]'
    label_comms_disability1 = 'div[data-cy="label-comms disability"]'
    label_seeing_disability = 'div[data-cy="label-seeing disability"]'
    label_who_answers_phone = 'div[data-cy="label-who answers phone"]'
    label_hearing_disability = 'div[data-cy="label-hearing disability"]'
    label_observed_disability = 'div[data-cy="label-observed disability"]'
    label_physical_disability = 'div[data-cy="label-physical disability"]'
    label_selfcare_disability = 'div[data-cy="label-selfcare disability"]'
    label_estimated_birth_date = 'div[data-cy="label-estimated birth date"]'
    label_phone_no_alternative = 'div[data-cy="label-phone no alternative"]'
    label_who_answers_alt_phone = 'div[data-cy="label-who answers alt phone"]'
    label_tickets = 'div[data-cy="label-Tickets"]'
    checkbox = 'tr[role="checkbox"]'
    label_partner = 'div[data-cy="label-Partner"]'
    label_administrative_level2 = 'div[data-cy="label-Administrative Level 2"]'
    checkbox_household_data = 'span[data-cy="checkbox-household-data"]'
    checkbox_approve = '//*[contains(@data, "checkbox")]'
    checkbox_individual_data = 'span[data-cy="checkbox-requested-data-change"]'
    checkbox_requested_data_change = 'span[data-cy="checkbox-requested-data-change"]'
    approve_box_needs_adjudication_title = 'h6[data-cy="approve-box-needs-adjudication-title"]'
    button_create_linked_ticket = 'button[data-cy="button-create-linked-ticket"]'
    button_mark_distinct = 'button[data-cy="button-mark-distinct"]'
    button_mark_duplicate = 'button[data-cy="button-mark-duplicate"]'
    button_clear = 'button[data-cy="button-clear"]'
    select_all_checkbox = 'span[data-cy="select-all-checkbox"]'
    table_cell_uniqueness = 'th[data-cy="table-cell-uniqueness"]'
    table_cell_individual_id = 'th[data-cy="table-cell-individual-id"]'
    table_cell_household_id = 'th[data-cy="table-cell-household-id"]'
    table_cell_full_name = 'th[data-cy="table-cell-full-name"]'
    table_cell_gender = 'th[data-cy="table-cell-gender"]'
    table_cell_date_of_birth = 'th[data-cy="table-cell-date-of-birth"]'
    table_cell_similarity_score = 'th[data-cy="table-cell-similarity-score"]'
    table_cell_last_registration_date = 'th[data-cy="table-cell-last-registration-date"]'
    table_cell_doc_type = 'th[data-cy="table-cell-doc-type"]'
    table_cell_doc_number = 'th[data-cy="table-cell-doc-number"]'
    table_cell_admin_level2 = 'th[data-cy="table-cell-admin-level2"]'
    table_cell_village = 'th[data-cy="table-cell-village"]'
    checkbox_individual = 'span[data-cy="checkbox-individual"]'
    uniqueness_cell = 'td[data-cy="uniqueness-cell"]'
    distinct_tooltip = 'svg[data-cy="distinct-tooltip"]'
    individual_id_cell = 'td[data-cy="individual-id-cell"]'
    individual_id = 'span[data-cy="individual-id"]'
    household_id_cell = 'td[data-cy="household-id-cell"]'
    household_id = 'span[data-cy="household-id"]'
    full_name_cell = 'td[data-cy="full-name-cell"]'
    gender_cell = 'td[data-cy="gender-cell"]'
    birth_date_cell = 'td[data-cy="birth-date-cell"]'
    similarity_score_cell = 'td[data-cy="similarity-score-cell"]'
    last_registration_date_cell = 'td[data-cy="last-registration-date-cell"]'
    doc_type_cell = 'td[data-cy="doc-type-cell"]'
    doc_number_cell = 'td[data-cy="doc-number-cell"]'
    admin_level2_cell = 'td[data-cy="admin-level2-cell"]'
    village_cell = 'td[data-cy="village-cell"]'
    checkbox_cell = 'td[data-cy="checkbox-cell"]'
    select_checkbox = 'span[data-cy="select-checkbox"]'
    status_cell = 'td[data-cy="status-cell"]'
    sex_cell = 'td[data-cy="sex-cell"]'
    similarity_cell = 'td[data-cy="similarity-cell"]'
    document_type_cell = 'td[data-cy="document-type-cell"]'
    document_number_cell = 'td[data-cy="document-number-cell"]'
    admin2_name_cell = 'td[data-cy="admin2-name-cell"]'
    duplicate_tooltip = 'svg[data-cy="duplicate-tooltip"]'
    input_new_note = 'textarea[data-cy="input-newNote"]'
    button_add_note = 'button[data-cy="button-add-note"]'
    activity_log_container = 'div[data-cy="activity-log-container"]'
    activity_log_title = 'h6[data-cy="activity-log-title"]'
    expand_collapse_button = 'button[data-cy="expand-collapse-button"]'
    activity_log_table = 'div[data-cy="activity-log-table"]'
    heading_cell_timestamp = 'div[data-cy="heading-cell-timestamp"]'
    heading_cell_actor = 'div[data-cy="heading-cell-actor"]'
    heading_cell_action = 'div[data-cy="heading-cell-action"]'
    heading_cell_change_from = 'div[data-cy="heading-cell-change_from"]'
    heading_cell_change_to = 'div[data-cy="heading-cell-change_to"]'
    pagination = 'div[data-cy="pagination"]'
    button_admin = 'div[data-cy="button-admin"]'
    log_row = 'div[data-cy="log-row"]'
    payment_record = 'span[data-cy="payment-record"]'
    label_gender = 'div[data-cy="label-GENDER"]'
    grievance_verify = '[data-cy="grievance-verify"]'
    input_new_received_amount = '[data-cy="input-newReceivedAmount"]'
    button_submit = 'button[data-cy="button-submit"]'
    grievance_approve = '[data-cy="grievance-approve"]'

    # Texts
    text_title = "Ticket ID: "
    text_status_new = "New"
    text_status_assigned = "Assigned"
    text_priority_not_set = "Not set"
    text_priority_medium = "Medium"
    text_priority_low = "Low"
    text_priority_high = "High"
    text_urgency_not_urgent = "Not urgent"
    text_urgency_urgent = "Urgent"
    text_urgency_very_urgent = "Very urgent"
    text_urgency_not_set = "Not set"
    text_not_assigment = "-"
    text_assigment_root_rootkowski = "Root Rootkowski"
    text_no_category = "Needs Adjudication"
    possible_duplicate_row_template = 'tr[data-cy="possible-duplicate-row-{}"]'
    people_icon = 'svg[data-cy="people-icon"]'
    person_icon = 'svg[data-cy="person-icon"]'
    button_rotate_image = 'button[data-cy="button-rotate-image"]'
    button_cancel = 'button[data-cy="button-cancel"]'
    link_show_photo = 'a[data-cy="link-show-photo"]'
    label_status = 'div[data-cy="label-Status"]'
    status_container = 'div[data-cy="status-container"]'
    label_priority = 'div[data-cy="label-Priority"]'
    label_urgency = 'div[data-cy="label-Urgency"]'
    label_ticket_id = '[data-cy="label-Ticket Id"]'

    def get_label_gender(self) -> WebElement:
        return self.wait_for(self.label_gender)

    def get_person_icon(self) -> WebElement:
        return self.wait_for(self.person_icon)

    def get_label_administrative_level_2(self) -> WebElement:
        return self.wait_for(self.label_administrative_level2)

    def get_people_icon(self) -> WebElement:
        return self.wait_for(self.people_icon)

    def disappear_people_icon(self) -> WebElement:
        return self.wait_for_disappear(self.people_icon)

    def disappear_person_icon(self) -> WebElement:
        return self.wait_for_disappear(self.people_icon)

    def get_page_header_container(self) -> WebElement:
        return self.wait_for(self.page_header_container)

    def get_title(self) -> WebElement:
        return self.wait_for(self.title)

    def get_grievance_lined_ticket(self) -> WebElement:
        return self.wait_for(self.label_ticket_id)

    def get_button_close_ticket(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.wait_for(self.button_close_ticket)

    def get_button_assign_to_me(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.wait_for(self.button_assign_to_me)

    def get_button_send_for_approval(self) -> WebElement:
        return self.wait_for(self.button_send_for_approval)

    def get_button_approval(self) -> WebElement:
        button = self.wait_for(self.button_approval)
        # Force click using JavaScript if regular click might not work
        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
        sleep(1)
        return button

    def get_button_set_in_progress(self) -> WebElement:
        return self.wait_for(self.button_set_in_progress)

    def get_button_send_back(self) -> WebElement:
        return self.wait_for(self.button_send_back)

    def get_button_confirm(self) -> WebElement:
        return self.wait_for(self.button_confirm)

    def disappear_button_confirm(self) -> WebElement:
        return self.wait_for_disappear(self.button_confirm)

    def disappear_button_close_ticket(self) -> WebElement:
        return self.wait_for_disappear(self.button_close_ticket)

    def get_button_edit(self) -> WebElement:
        return self.wait_for(self.button_edit)

    def get_ticket_status(self) -> WebElement:
        return self.wait_for(self.ticket_status)

    def get_ticket_priority(self) -> WebElement:
        return self.wait_for(self.ticket_priority)

    def get_ticket_urgency(self) -> WebElement:
        return self.wait_for(self.ticket_urgency)

    def get_ticket_assigment(self) -> WebElement:
        return self.wait_for(self.ticket_assigment)

    def get_ticket_category(self) -> WebElement:
        return self.wait_for(self.ticket_category)

    def get_ticket_household_id(self) -> WebElement:
        return self.wait_for(self.ticket_household_id)

    def get_ticket_target_id(self) -> WebElement:
        return self.wait_for(self.ticket_target_id)

    def get_ticket_individual_id(self) -> WebElement:
        return self.wait_for(self.ticket_individual_id)

    def get_ticket_payment_label(self) -> WebElement:
        return self.wait_for(self.ticket_payment_label)

    def get_label_payment_plan(self) -> WebElement:
        return self.wait_for(self.label_payment_plan)

    def get_label_payment_plan_verification(self) -> WebElement:
        return self.wait_for(self.label_payment_plan_verification)

    def get_label_programme(self) -> WebElement:
        return self.wait_for(self.label_programme)

    def get_label_partner(self) -> WebElement:
        return self.wait_for(self.label_partner)

    def get_ticket_category_by(self) -> WebElement:
        return self.wait_for(self.ticket_category_by)

    def get_date_creation(self) -> WebElement:
        return self.wait_for(self.date_creation)

    def get_last_modified_date(self) -> WebElement:
        return self.wait_for(self.last_modified_date)

    def get_administrative_level(self) -> WebElement:
        return self.wait_for(self.administrative_level)

    def get_label_last_modified_date(self) -> WebElement:
        return self.wait_for(self.last_modified_date)

    def get_area_village(self) -> WebElement:
        return self.wait_for(self.area_village)

    def get_languages_spoken(self) -> WebElement:
        return self.wait_for(self.languages_spoken)

    def get_documentation(self) -> WebElement:
        return self.wait_for(self.documentation)

    def get_ticket_description(self) -> WebElement:
        return self.wait_for(self.ticket_description)

    def get_label_created_by(self) -> WebElement:
        return self.wait_for(self.label_created_by)

    def get_label_date_creation(self) -> WebElement:
        return self.wait_for(self.date_creation)

    def get_label_comments(self) -> WebElement:
        return self.wait_for(self.comments)

    def get_create_linked_ticket(self) -> WebElement:
        return self.wait_for(self.create_linked_ticket)

    def get_mark_duplicate(self) -> WebElement:
        return self.wait_for(self.mark_duplicate)

    def get_cell_individual_id(self) -> WebElement:
        return self.wait_for(self.cell_individual_id)

    def get_cell_household_id(self) -> WebElement:
        return self.wait_for(self.cell_household_id)

    def get_label_issue_type(self) -> WebElement:
        return self.wait_for(self.label_issue_type)

    def get_cell_full_name(self) -> WebElement:
        return self.wait_for(self.cell_full_name)

    def get_cell_gender(self) -> WebElement:
        return self.wait_for(self.cell_gender)

    def get_cell_date_of_birth(self) -> WebElement:
        return self.wait_for(self.cell_date_of_birth)

    def get_cell_similarity_score(self) -> WebElement:
        return self.wait_for(self.cell_similarity_score)

    def get_cell_last_registration_date(self) -> WebElement:
        return self.wait_for(self.cell_last_registration_date)

    def get_cell_doc_type(self) -> WebElement:
        return self.wait_for(self.cell_doc_type)

    def get_cell_doc(self) -> WebElement:
        return self.wait_for(self.cell_doc)

    def get_cell_admin_level2(self) -> WebElement:
        return self.wait_for(self.cell_admin_level2)

    def get_cell_village(self) -> WebElement:
        return self.wait_for(self.cell_village)

    def get_new_note_field(self) -> WebElement:
        return self.wait_for(self.new_note_field)

    def get_button_new_note(self) -> WebElement:
        return self.wait_for(self.button_new_note)

    def get_note_rows(self) -> [WebElement]:
        self.wait_for(self.note_row)
        return self.get_elements(self.note_row)

    def get_label_languages_spoken(self) -> WebElement:
        return self.wait_for(self.label_languages_spoken)

    def get_label_documentation(self) -> WebElement:
        return self.wait_for(self.label_documentation)

    def get_label_description(self) -> WebElement:
        return self.wait_for(self.label_description)

    def get_note_name(self) -> WebElement:
        return self.wait_for(self.note_name)

    def get_label_gender_up(self) -> WebElement:
        return self.wait_for(self.label_gender_up)

    def get_label_role(self) -> WebElement:
        return self.wait_for(self.label_role)

    def get_label_phone_no(self) -> WebElement:
        return self.wait_for(self.label_phone_no)

    def get_label_pregnant(self) -> WebElement:
        return self.wait_for(self.label_pregnant)

    def get_label_full_name(self) -> WebElement:
        return self.wait_for(self.label_full_name)

    def get_label_birth_date(self) -> WebElement:
        return self.wait_for(self.label_birth_date)

    def get_label_disability(self) -> WebElement:
        return self.wait_for(self.label_disability)

    def get_label_given_name(self) -> WebElement:
        return self.wait_for(self.label_given_name)

    def get_label_family_name(self) -> WebElement:
        return self.wait_for(self.label_family_name)

    def get_label_middle_name(self) -> WebElement:
        return self.wait_for(self.label_middle_name)

    def get_label_work_status(self) -> WebElement:
        return self.wait_for(self.label_work_status)

    def get_label_relationship(self) -> WebElement:
        return self.wait_for(self.label_relationship)

    def get_label_marital_status(self) -> WebElement:
        return self.wait_for(self.label_marital_status)

    def get_label_comms_disability(self) -> WebElement:
        return self.wait_for(self.label_comms_disability)

    def get_label_comms_disability1(self) -> WebElement:
        return self.wait_for(self.label_comms_disability1)

    def get_label_seeing_disability(self) -> WebElement:
        return self.wait_for(self.label_seeing_disability)

    def get_label_who_answers_phone(self) -> WebElement:
        return self.wait_for(self.label_who_answers_phone)

    def get_label_hearing_disability(self) -> WebElement:
        return self.wait_for(self.label_hearing_disability)

    def get_label_observed_disability(self) -> WebElement:
        return self.wait_for(self.label_observed_disability)

    def get_label_physical_disability(self) -> WebElement:
        return self.wait_for(self.label_physical_disability)

    def get_label_selfcare_disability(self) -> WebElement:
        return self.wait_for(self.label_selfcare_disability)

    def get_label_estimated_birth_date(self) -> WebElement:
        return self.wait_for(self.label_estimated_birth_date)

    def get_label_phone_no_alternative(self) -> WebElement:
        return self.wait_for(self.label_phone_no_alternative)

    def get_label_who_answers_alt_phone(self) -> WebElement:
        return self.wait_for(self.label_who_answers_alt_phone)

    def get_label_tickets(self) -> WebElement:
        return self.wait_for(self.label_tickets)

    def get_checkbox(self) -> WebElement:
        return self.wait_for(self.checkbox)

    def get_approve_box_needs_adjudication_title(self) -> WebElement:
        return self.wait_for(self.approve_box_needs_adjudication_title)

    def get_checkbox_household_data(self) -> WebElement:
        return self.wait_for(self.checkbox_household_data)

    def get_checkbox_approve(self) -> [WebElement]:
        self.wait_for(self.checkbox_approve, By.XPATH)
        return self.get_elements(self.checkbox_approve, By.XPATH)

    def get_checkbox_individual_data(self) -> WebElement:
        return self.wait_for(self.checkbox_individual_data)

    def get_checkbox_requested_data_change(self) -> [WebElement]:
        self.wait_for(self.checkbox_requested_data_change)
        return self.get_elements(self.checkbox_requested_data_change)

    def get_button_create_linked_ticket(self) -> WebElement:
        return self.wait_for(self.button_create_linked_ticket)

    def get_button_mark_distinct(self) -> WebElement:
        return self.wait_for(self.button_mark_distinct)

    def get_button_mark_duplicate(self) -> WebElement:
        return self.wait_for(self.button_mark_duplicate)

    def get_button_clear(self) -> WebElement:
        return self.wait_for(self.button_clear)

    def get_select_all_checkbox(self) -> WebElement:
        return self.wait_for(self.select_all_checkbox)

    def get_table_cell_uniqueness(self) -> WebElement:
        return self.wait_for(self.table_cell_uniqueness)

    def get_table_cell_individual_id(self) -> WebElement:
        return self.wait_for(self.table_cell_individual_id)

    def get_table_cell_household_id(self) -> WebElement:
        return self.wait_for(self.table_cell_household_id)

    def get_table_cell_full_name(self) -> WebElement:
        return self.wait_for(self.table_cell_full_name)

    def get_table_cell_gender(self) -> WebElement:
        return self.wait_for(self.table_cell_gender)

    def get_table_cell_date_of_birth(self) -> WebElement:
        return self.wait_for(self.table_cell_date_of_birth)

    def get_table_cell_similarity_score(self) -> WebElement:
        return self.wait_for(self.table_cell_similarity_score)

    def get_table_cell_last_registration_date(self) -> WebElement:
        return self.wait_for(self.table_cell_last_registration_date)

    def get_table_cell_doc_type(self) -> WebElement:
        return self.wait_for(self.table_cell_doc_type)

    def get_table_cell_doc_number(self) -> WebElement:
        return self.wait_for(self.table_cell_doc_number)

    def get_table_cell_admin_level2(self) -> WebElement:
        return self.wait_for(self.table_cell_admin_level2)

    def get_table_cell_village(self) -> WebElement:
        return self.wait_for(self.table_cell_village)

    def get_checkbox_individual(self) -> WebElement:
        return self.wait_for(self.checkbox_individual)

    def get_uniqueness_cell(self) -> WebElement:
        return self.wait_for(self.uniqueness_cell)

    def get_distinct_tooltip(self) -> WebElement:
        return self.wait_for(self.distinct_tooltip)

    def get_individual_id_cell(self) -> [WebElement]:
        self.wait_for(self.individual_id_cell)
        return self.get_elements(self.individual_id_cell)

    def get_individual_id(self) -> WebElement:
        return self.wait_for(self.individual_id)

    def get_household_id_cell(self) -> [WebElement]:
        self.wait_for(self.household_id_cell)
        return self.get_elements(self.household_id_cell)

    def get_household_id(self) -> [WebElement]:
        self.wait_for(self.household_id)
        return self.get_elements(self.household_id)

    def get_full_name_cell(self) -> [WebElement]:
        return self.wait_for(self.full_name_cell)

    def get_gender_cell(self) -> WebElement:
        return self.wait_for(self.gender_cell)

    def get_birth_date_cell(self) -> [WebElement]:
        return self.wait_for(self.birth_date_cell)

    def get_similarity_score_cell(self) -> WebElement:
        return self.wait_for(self.similarity_score_cell)

    def get_last_registration_date_cell(self) -> WebElement:
        return self.wait_for(self.last_registration_date_cell)

    def get_doc_type_cell(self) -> WebElement:
        return self.wait_for(self.doc_type_cell)

    def get_doc_number_cell(self) -> WebElement:
        return self.wait_for(self.doc_number_cell)

    def get_admin_level2_cell(self) -> WebElement:
        return self.wait_for(self.admin_level2_cell)

    def get_village_cell(self) -> [WebElement]:
        self.wait_for(self.village_cell)
        return self.get_elements(self.village_cell)

    def get_possible_duplicate_row_by_unicef_id(self, unicef_id: str) -> WebElement:
        return self.wait_for(self.possible_duplicate_row_template.format(unicef_id))

    def get_checkbox_cell(self) -> [WebElement]:
        self.wait_for(self.checkbox_cell)
        return self.get_elements(self.checkbox_cell)

    def get_select_checkbox(self) -> [WebElement]:
        self.wait_for(self.select_checkbox)
        return self.get_elements(self.select_checkbox)

    def get_status_cell(self) -> [WebElement]:
        self.wait_for(self.status_cell)
        return self.get_elements(self.status_cell)

    def get_sex_cell(self) -> WebElement:
        return self.wait_for(self.sex_cell)

    def get_similarity_cell(self) -> WebElement:
        return self.wait_for(self.similarity_cell)

    def get_document_type_cell(self) -> WebElement:
        return self.wait_for(self.document_type_cell)

    def get_document_number_cell(self) -> WebElement:
        return self.wait_for(self.document_number_cell)

    def get_admin2_name_cell(self) -> WebElement:
        return self.wait_for(self.admin2_name_cell)

    def get_duplicate_tooltip(self) -> WebElement:
        return self.wait_for(self.duplicate_tooltip)

    def get_input_new_note(self) -> WebElement:
        return self.wait_for(self.input_new_note)

    def get_button_add_note(self) -> WebElement:
        return self.wait_for(self.button_add_note)

    def get_activity_log_container(self) -> WebElement:
        return self.wait_for(self.activity_log_container)

    def get_activity_log_title(self) -> WebElement:
        return self.wait_for(self.activity_log_title)

    def get_expand_collapse_button(self) -> WebElement:
        return self.wait_for(self.expand_collapse_button, timeout=120)

    def get_activity_log_table(self) -> WebElement:
        return self.wait_for(self.activity_log_table)

    def get_heading_cell_timestamp(self) -> WebElement:
        return self.wait_for(self.heading_cell_timestamp)

    def get_heading_cell_actor(self) -> WebElement:
        return self.wait_for(self.heading_cell_actor)

    def get_heading_cell_action(self) -> WebElement:
        return self.wait_for(self.heading_cell_action)

    def get_heading_cell_change_from(self) -> WebElement:
        return self.wait_for(self.heading_cell_change_from)

    def get_heading_cell_change_to(self) -> WebElement:
        return self.wait_for(self.heading_cell_change_to)

    def get_pagination(self) -> WebElement:
        return self.wait_for(self.pagination)

    def get_button_cancel(self) -> WebElement:
        return self.wait_for(self.button_cancel)

    def get_button_admin(self) -> WebElement:
        return self.wait_for(self.button_admin)

    def get_log_row(self) -> [WebElement]:
        self.wait_for(self.log_row)
        return self.get_elements(self.log_row)

    def get_payment_record(self) -> WebElement:
        return self.wait_for(self.payment_record)

    def get_button_rotate_image(self) -> WebElement:
        return self.wait_for(self.button_rotate_image)

    def get_link_show_photo(self) -> WebElement:
        return self.wait_for(self.link_show_photo)

    def get_grievance_verify(self) -> WebElement:
        return self.wait_for(self.grievance_verify)

    def get_input_new_received_amount(self) -> WebElement:
        return self.wait_for(self.input_new_received_amount)

    def get_button_submit(self) -> WebElement:
        return self.wait_for(self.button_submit)

    def get_grievance_approve(self) -> WebElement:
        return self.wait_for(self.grievance_approve)

    def get_label_status(self) -> WebElement:
        return self.wait_for(self.label_status)

    def get_status_container(self) -> WebElement:
        return self.wait_for(self.status_container)

    def get_label_priority(self) -> WebElement:
        return self.wait_for(self.label_priority)

    def get_label_urgency(self) -> WebElement:
        return self.wait_for(self.label_urgency)
