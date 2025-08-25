from datetime import datetime
from typing import List

import pytest
from dateutil.relativedelta import relativedelta
from django.db import transaction
from e2e.page_object.filters import Filters
from e2e.page_object.grievance.details_grievance_page import GrievanceDetailsPage
from e2e.page_object.grievance.grievance_tickets import GrievanceTickets
from e2e.page_object.grievance.new_ticket import NewTicket
from e2e.page_object.people.people import People
from e2e.page_object.people.people_details import PeopleDetails
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.household import (
    create_household,
    create_individual_document,
)
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from selenium.webdriver.common.by import By

from hope.models.core import BusinessArea, DataCollectingType
from hope.models.household import HOST, SEEING, Individual
from hope.apps.payment.models import Payment
from hope.models.program import BeneficiaryGroup, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def social_worker_program() -> Program:
    return get_social_program_with_dct_type_and_name(
        "Worker Program", "WORK", DataCollectingType.Type.SOCIAL, Program.ACTIVE
    )


@pytest.fixture
def add_people(social_worker_program: Program) -> List:
    ba = social_worker_program.business_area
    with transaction.atomic():
        household, individuals = create_household(
            household_args={
                "business_area": ba,
                "program": social_worker_program,
                "residence_status": HOST,
            },
            individual_args={
                "full_name": "Stacey Freeman",
                "given_name": "Stacey",
                "middle_name": "",
                "family_name": "Freeman",
                "business_area": ba,
                "observed_disability": [SEEING],
            },
        )
        individual = individuals[0]
        create_individual_document(individual)
    yield [individual, household]


@pytest.fixture
def add_people_with_payment_record(add_people: List) -> Payment:
    program = Program.objects.filter(name="Worker Program").first()

    payment_plan = PaymentPlanFactory(
        name="TEST",
        program_cycle=program.cycles.first(),
        business_area=BusinessArea.objects.first(),
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )
    payment = PaymentFactory(
        household=add_people[1],
        parent=payment_plan,
        entitlement_quantity=21.36,
        delivered_quantity=21.36,
        currency="PLN",
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    add_people[1].total_cash_received_usd = 21.36
    add_people[1].save()
    return payment


def get_program_with_dct_type_and_name(
    name: str,
    programme_code: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.DRAFT,
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    return ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )


def get_social_program_with_dct_type_and_name(
    name: str,
    programme_code: str,
    dct_type: str = DataCollectingType.Type.SOCIAL,
    status: str = Program.DRAFT,
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="People").first()
    return ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )


@pytest.mark.usefixtures("login")
class TestSmokePeople:
    def test_smoke_page_people(self, social_worker_program: Program, page_people: People) -> None:
        page_people.select_global_program_filter("Worker Program")
        page_people.get_nav_people().click()
        assert "People" in page_people.get_table_title().text
        assert "Individual ID" in page_people.get_individual_id().text
        assert "Individual" in page_people.get_individual_name().text
        assert "Type" in page_people.get_individual_age().text
        assert "Gender" in page_people.get_individual_sex().text
        assert "Administrative Level 2" in page_people.get_individual_location().text
        assert "Rows per page: 10 0–0 of 0" in page_people.get_table_pagination().text.replace("\n", " ")

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_smoke_page_details_people(
        self,
        add_people: None,
        page_people: People,
        page_people_details: PeopleDetails,
        filters: Filters,
    ) -> None:
        page_people.select_global_program_filter("Worker Program")
        page_people.get_nav_people().click()
        assert "People" in page_people.get_table_title().text
        unicef_id = page_people.get_individual_table_row(0).text.split(" ")[0]
        page_people.get_individual_table_row(0).click()
        individual = Individual.objects.filter(unicef_id=unicef_id).first()
        assert f"Individual ID: {individual.unicef_id}" in page_people_details.get_page_header_title().text
        assert individual.full_name in page_people_details.get_label_full_name().text
        assert individual.given_name in page_people_details.get_label_given_name().text
        assert (
            individual.middle_name
            if individual.middle_name
            else "-" in page_people_details.get_label_middle_name().text
        )
        assert individual.family_name in page_people_details.get_label_family_name().text
        assert individual.sex.lower().replace("_", " ") in page_people_details.get_label_gender().text.lower()
        assert page_people_details.get_label_age().text
        assert individual.birth_date.strftime("%-d %b %Y") in page_people_details.get_label_date_of_birth().text
        assert page_people_details.get_label_estimated_date_of_birth().text
        assert individual.marital_status.lower() in page_people_details.get_label_marital_status().text.lower()
        assert "Not provided" in page_people_details.get_label_work_status().text
        assert page_people_details.get_label_pregnant().text
        assert page_people_details.get_label_role().text
        assert (
            individual.preferred_language
            if individual.preferred_language
            else "-" in page_people_details.get_label_preferred_language().text
        )
        assert "Non-displaced | Host" in page_people_details.get_label_residence_status().text
        assert (
            individual.household.country
            if individual.household.country
            else "-" in page_people_details.get_label_country().text
        )
        assert (
            individual.household.country_origin
            if individual.household.country_origin
            else "-" in page_people_details.get_label_country_of_origin().text
        )
        assert (
            individual.household.address
            if individual.household.address
            else "-" in page_people_details.get_label_address().text
        )
        assert (
            individual.household.village
            if individual.household.village
            else "-" in page_people_details.get_label_vilage().text
        )
        assert (
            individual.household.zip_code
            if individual.household.zip_code
            else "-" in page_people_details.get_label_zip_code().text
        )
        assert (
            individual.household.admin1
            if individual.household.admin1
            else "-" in page_people_details.get_label_administrative_level_1().text
        )
        assert (
            individual.household.admin2
            if individual.household.admin2
            else "-" in page_people_details.get_label_administrative_level_2().text
        )
        assert (
            individual.household.admin3
            if individual.household.admin3
            else "-" in page_people_details.get_label_administrative_level_3().text
        )
        assert (
            individual.household.admin4
            if individual.household.admin4
            else "-" in page_people_details.get_label_administrative_level_4().text
        )
        assert (
            individual.household.geopoint
            if individual.household.geopoint
            else "-" in page_people_details.get_label_geolocation().text
        )
        assert page_people_details.get_label_data_collecting_type().text
        assert page_people_details.get_label_observed_disabilities().text
        assert page_people_details.get_label_seeing_disability_severity().text
        assert page_people_details.get_label_hearing_disability_severity().text
        assert page_people_details.get_label_physical_disability_severity().text
        assert page_people_details.get_label_remembering_or_concentrating_disability_severity().text
        assert page_people_details.get_label_communicating_disability_severity().text
        assert "Not Disabled" in page_people_details.get_label_disability().text
        assert page_people_details.get_label_issued().text
        assert page_people_details.get_label_email().text
        assert page_people_details.get_label_phone_number().text
        assert page_people_details.get_label_alternative_phone_number().text
        assert page_people_details.get_label_date_of_last_screening_against_sanctions_list().text
        assert page_people_details.get_label_linked_grievances().text
        assert page_people_details.get_label_wallet_name().text
        assert page_people_details.get_label_blockchain_name().text
        assert page_people_details.get_label_wallet_address().text
        assert "Rows per page: 5 0–0 of 0" in page_people_details.get_table_pagination().text.replace("\n", " ")
        assert page_people_details.get_label_source().text
        assert page_people_details.get_label_import_name().text
        assert page_people_details.get_label_registration_date().text
        assert page_people_details.get_label_user_name().text

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_people_happy_path(
        self,
        add_people_with_payment_record: Payment,
        page_people: People,
        page_people_details: PeopleDetails,
    ) -> None:
        page_people.select_global_program_filter("Worker Program")
        page_people.get_nav_people().click()
        page_people.get_individual_table_row(0).click()
        assert "21.36" in page_people_details.get_label_total_cash_received().text
        page_people_details.wait_for_rows()
        assert len(page_people_details.get_rows()) == 1
        assert "21.36" in page_people_details.get_rows()[0].text
        assert "DELIVERED FULLY" in page_people_details.get_rows()[0].text
        assert add_people_with_payment_record.unicef_id in page_people_details.get_rows()[0].text


@pytest.mark.usefixtures("login")
class TestPeople:
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {"category": "Data Change", "type": "Member Data Update"},
                id="Data Change People Data Update",
            )
        ],
    )
    def test_check_people_data_after_grievance_ticket_processed(
        self,
        page_grievance_tickets: GrievanceTickets,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        add_people: List,
        test_data: dict,
        page_people: People,
        page_people_details: PeopleDetails,
    ) -> None:
        page_grievance_tickets.get_nav_grievance().click()
        assert "Grievance Tickets" in page_grievance_tickets.get_grievance_title().text
        page_grievance_tickets.get_button_new_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name(str(test_data["category"]))
        page_grievance_new_ticket.get_issue_type().click()
        page_grievance_new_ticket.element_clickable(f'li[data-cy="select-option-{test_data["type"]}"]')
        page_grievance_new_ticket.select_listbox_element(str(test_data["type"]))
        assert test_data["category"] in page_grievance_new_ticket.get_select_category().text
        assert test_data["type"] in page_grievance_new_ticket.get_issue_type().text
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_individual_tab().click()
        page_grievance_new_ticket.get_individual_table_rows(0).click()
        page_grievance_details_page.screenshot("0")
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()

        page_grievance_new_ticket.get_description().send_keys("Add Member - TEST")
        page_grievance_new_ticket.get_button_add_new_field().click()
        page_grievance_new_ticket.get_individual_field_name(0).click()
        page_grievance_new_ticket.select_listbox_element("Gender")
        page_grievance_new_ticket.get_input_individual_data("Gender").click()
        page_grievance_new_ticket.select_listbox_element("Female")
        page_grievance_new_ticket.get_individual_field_name(1).click()
        page_grievance_new_ticket.select_listbox_element("Preferred language")
        page_grievance_new_ticket.get_input_individual_data("Preferred language").click()
        page_grievance_new_ticket.select_listbox_element("English | English")

        page_grievance_new_ticket.get_button_next().click()
        page_grievance_details_page.get_checkbox_individual_data()
        row0 = page_grievance_details_page.get_rows()[0].text.split(" ")
        assert "Gender" in row0[0]
        assert "Female" in row0[-1]

        row1 = page_grievance_details_page.get_rows()[1].text.split(" ")
        assert "Preferred Language" in f"{row1[0]} {row1[1]}"
        assert "English" in row1[-1]
        page_grievance_details_page.get_button_assign_to_me().click()
        page_grievance_details_page.get_button_set_in_progress().click()
        page_grievance_details_page.get_button_send_for_approval().click()
        page_grievance_details_page.get_button_close_ticket()
        page_grievance_details_page.get_checkbox_requested_data_change()
        page_grievance_details_page.get_checkbox_requested_data_change()[0].find_element(By.TAG_NAME, "input").click()
        page_grievance_details_page.get_checkbox_requested_data_change()[1].find_element(By.TAG_NAME, "input").click()
        page_grievance_details_page.get_button_approval().click()
        page_grievance_details_page.get_button_confirm().click()
        page_grievance_details_page.get_button_close_ticket().click()
        page_grievance_details_page.get_button_confirm().click()
        assert "Ticket ID" in page_grievance_details_page.get_title().text
        page_people.select_global_program_filter("Worker Program")
        page_people.get_nav_people().click()
        page_people.get_individual_table_row(0).click()
