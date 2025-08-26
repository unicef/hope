from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.grievance.details_feedback_page import FeedbackDetailsPage
from e2e.page_object.grievance.details_grievance_page import GrievanceDetailsPage
from e2e.page_object.grievance.feedback import Feedback
from e2e.page_object.grievance.new_feedback import NewFeedback
from e2e.page_object.grievance.new_ticket import NewTicket
from e2e.page_object.programme_details.programme_details import ProgrammeDetails
from extras.test_utils.factories.accountability import generate_feedback
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    create_afghanistan,
)
from extras.test_utils.factories.household import (
    create_household,
    create_household_and_individuals,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
import pytest

from hope.apps.account.models import User
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.geo.models import Area, Country
from hope.apps.household.models import HOST, Household
from hope.apps.program.models import BeneficiaryGroup, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def add_feedbacks() -> None:
    generate_feedback()
    yield


@pytest.fixture
def add_households() -> None:
    registration_data_import = RegistrationDataImportFactory(
        imported_by=User.objects.first(), business_area=BusinessArea.objects.first()
    )
    household, _ = create_household(
        {
            "registration_data_import": registration_data_import,
            "admin2": Area.objects.order_by("?").first(),
            "program": Program.objects.filter(name="Test Programm").first(),
        },
        {"registration_data_import": registration_data_import},
    )

    household.unicef_id = "HH-00-0000.1380"
    household.save()


@pytest.fixture
def create_programs() -> None:
    business_area = create_afghanistan()
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    ProgramFactory(
        name="Test Programm",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )
    ProgramFactory(
        name="Draft Program",
        status=Program.DRAFT,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def create_households_and_individuals() -> Household:
    hh = create_custom_household(observed_disability=[])
    hh.male_children_count = 1
    hh.male_age_group_0_5_count = 1
    hh.female_children_count = 2
    hh.female_age_group_0_5_count = 2
    hh.children_count = 3
    hh.village = "Wroclaw"
    hh.country_origin = Country.objects.filter(iso_code2="UA").first()
    hh.address = "Karta-e-Mamorin KABUL/5TH DISTRICT, Afghanistan"
    hh.admin1 = Area.objects.first()
    hh.admin2 = Area.objects.get(name="Shakardara")
    hh.save()
    hh.set_admin_areas()
    hh.refresh_from_db()
    yield hh


def create_custom_household(observed_disability: list[str], residence_status: str = HOST) -> Household:
    program = get_program_with_dct_type_and_name("Test Program", "1234")
    household, _ = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.0002",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "residence_status": residence_status,
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.0011",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "observed_disability": observed_disability,
            },
            {
                "unicef_id": "IND-00-0000.0022",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "observed_disability": observed_disability,
            },
            {
                "unicef_id": "IND-00-0000.0033",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "observed_disability": observed_disability,
            },
        ],
    )
    return household


@pytest.mark.usefixtures("login")
class TestSmokeFeedback:
    def test_check_feedback_page(
        self,
        page_feedback: Feedback,
    ) -> None:
        """
        Go to Grievance page
        Go to Feedback page
        Check if all elements on page exist
        """
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Check Feedback page
        page_feedback.get_title_page()
        page_feedback.get_button_submit_new_feedback()
        page_feedback.get_filter_search()
        page_feedback.get_filter_issue_type()
        page_feedback.get_filter_created_by()
        page_feedback.get_filter_creation_date_from()
        page_feedback.get_filter_creation_date_to()
        page_feedback.get_button_clear()
        page_feedback.get_button_apply()
        assert page_feedback.text_table_title in page_feedback.get_table_title().text
        assert page_feedback.text_feedback_id in page_feedback.get_feedback_id().text
        assert page_feedback.text_issue_type in page_feedback.get_issue_type().text
        assert page_feedback.text_household_id in page_feedback.get_household_id().text
        assert page_feedback.text_linked_grievance in page_feedback.get_linked_grievance().text
        assert page_feedback.text_created_by in page_feedback.get_created_by().text
        assert page_feedback.text_creation_date in page_feedback.get_creation_date().text

    def test_check_feedback_details_page(
        self,
        add_feedbacks: None,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
    ) -> None:
        """
        Go to Grievance page
        Go to Feedback page
        Choose Feedback
        Check if all elements on page exist
        """
        # Go to Feedback
        page_feedback.driver.refresh()
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        page_feedback.get_row(0).click()
        # Check Feedback details page
        assert page_feedback_details.text_title in page_feedback_details.get_title_page().text
        page_feedback_details.get_button_edit()
        assert page_feedback_details.text_category in page_feedback_details.get_category().text
        assert page_feedback_details.text_issue_type in page_feedback_details.get_issue_type().text
        page_feedback_details.get_household_id()
        page_feedback_details.get_individual_id()
        page_feedback_details.get_created_by()
        page_feedback_details.get_date_created()
        page_feedback_details.get_last_modified_date()
        page_feedback_details.get_administrative_level2()


@pytest.mark.skip(reason="ToDo: Filters")
@pytest.mark.usefixtures("login")
class TestFeedbackFilters:
    def feedback_search_filter(self) -> None:
        pass

    def feedback_programme_filter(self) -> None:
        pass

    def feedback_issue_type_filter(self) -> None:
        pass

    def feedback_created_by_filter(self) -> None:
        pass

    def feedback_creation_date_filter(self) -> None:
        pass

    def feedback_programme_state_filter(self) -> None:
        pass

    def feedback_clear_button(self) -> None:
        pass


@pytest.mark.usefixtures("login")
class TestFeedback:
    @pytest.mark.parametrize("issue_type", ["Positive", "Negative"])
    def test_create_feedback_mandatory_fields(
        self,
        issue_type: None,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        page_new_feedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Create Feedback
        page_feedback.get_button_submit_new_feedback().click()
        page_new_feedback.choose_option_by_name(issue_type)
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_household_tab()
        page_new_feedback.get_table_empty_row()
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_received_consent().click()
        page_new_feedback.get_button_next().click()
        assert "Feedback" in page_new_feedback.get_label_category().text
        page_new_feedback.get_description().send_keys("Test")
        page_new_feedback.get_button_next().click()
        page_feedback_details.get_button_create_linked_ticket()
        # Check Details page
        assert page_feedback_details.text_category in page_feedback_details.get_category().text
        assert issue_type in page_feedback_details.get_issue_type().text
        assert "-" in page_feedback_details.get_household_id().text
        assert "-" in page_feedback_details.get_individual_id().text
        assert "-" in page_feedback_details.get_programme().text
        assert "Test" in page_feedback_details.get_description().text
        page_feedback_details.get_last_modified_date()
        page_feedback_details.get_administrative_level2()

    @pytest.mark.xfail(reason="UNSTABLE AFTER REST REFACTOR")
    @pytest.mark.parametrize("issue_type", ["Positive", "Negative"])
    def test_create_feedback_optional_fields(
        self,
        issue_type: None,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        page_new_feedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Create Feedback
        page_feedback.get_button_submit_new_feedback().click()
        page_new_feedback.choose_option_by_name(issue_type)
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_household_tab()
        page_new_feedback.get_individual_tab()
        page_feedback.get_table_row_loading()
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_received_consent().click()
        page_new_feedback.get_button_next().click()
        assert "Feedback" in page_new_feedback.get_label_category().text
        page_new_feedback.get_description().send_keys("Test")
        page_new_feedback.get_button_next().click()
        # Check Details page
        assert page_feedback_details.text_category in page_feedback_details.get_category().text
        assert issue_type in page_feedback_details.get_issue_type().text
        assert "-" in page_feedback_details.get_household_id().text
        assert "-" in page_feedback_details.get_individual_id().text
        assert "-" in page_feedback_details.get_programme().text
        assert "Test" in page_feedback_details.get_description().text
        page_feedback_details.get_last_modified_date()
        page_feedback_details.get_administrative_level2()

    def test_check_feedback_filtering_by_chosen_programme(
        self,
        create_programs: None,
        add_feedbacks: None,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        page_new_feedback: NewFeedback,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Edit field Programme in Feedback
        page_feedback.get_row(0).click()
        assert "-" in page_feedback_details.get_programme().text
        page_feedback_details.get_button_edit().click()
        page_new_feedback.select_programme("Test Programm")
        page_new_feedback.get_button_next().click()
        # Check Feedback filtering by chosen Programme
        assert "Test Programm" in page_feedback_details.get_programme().text
        assert page_feedback.global_program_filter_text in page_feedback.get_global_program_filter().text
        page_feedback.select_global_program_filter("Test Programm")
        assert "Test Programm" in page_programme_details.get_header_title().text
        page_feedback.wait_for_disappear(page_feedback.nav_grievance_dashboard)
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        page_feedback.disappear_table_row_loading()
        assert len(page_feedback.get_rows()) == 1
        assert "Negative Feedback" in page_feedback.get_row(0).find_elements("tag name", "td")[1].text

        page_feedback.select_global_program_filter("Draft Program")
        assert "Draft Program" in page_programme_details.get_header_title().text
        page_feedback.wait_for_disappear(page_feedback.nav_grievance_dashboard)
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        assert len(page_feedback.get_rows()) == 0

        page_feedback.select_global_program_filter("All Programmes")
        assert "Programme Management" in page_programme_details.get_header_title().text
        page_feedback.wait_for_disappear(page_feedback.nav_grievance_dashboard)
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        page_feedback.disappear_table_row_loading()
        assert len(page_feedback.get_rows()) == 2

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_create_feedback_with_household(
        self,
        create_programs: None,
        add_households: None,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        page_new_feedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Create Feedback
        page_feedback.get_button_submit_new_feedback().click()
        page_new_feedback.choose_option_by_name("Negative feedback")
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_household_tab()
        page_new_feedback.get_household_table_rows(1).click()
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_received_consent().click()
        page_new_feedback.get_button_next().click()
        assert "Feedback" in page_new_feedback.get_label_category().text
        page_new_feedback.get_description().send_keys("Test")
        page_new_feedback.get_button_next().click()
        # Check Details page
        assert "Test Programm" in page_feedback_details.get_programme().text
        page_feedback.get_nav_feedback().click()
        page_feedback.get_rows()

    @pytest.mark.xfail(reason="UNSTABLE AFTER REST REFACTOR")
    def test_create_feedback_with_household_and_individual(
        self,
        create_programs: None,
        add_households: None,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        page_new_feedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Create Feedback
        page_feedback.get_button_submit_new_feedback().click()
        page_new_feedback.choose_option_by_name("Negative feedback")
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_household_tab()
        page_new_feedback.get_household_table_rows(0).click()
        page_new_feedback.get_individual_tab().click()
        page_new_feedback.get_individual_table_row(2).click()
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_received_consent().click()
        page_new_feedback.get_button_next().click()
        assert "Feedback" in page_new_feedback.get_label_category().text
        page_new_feedback.get_description().send_keys("Test")
        page_new_feedback.get_button_next().click()
        # Check Details page
        assert "Test Programm" in page_feedback_details.get_programme().text
        page_feedback.get_nav_feedback().click()
        page_feedback.get_rows()

    @pytest.mark.xfail(reason="Problem with deadlock during test - 202318")
    def test_create_feedback_with_individual(
        self,
        create_programs: None,
        add_households: None,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        page_new_feedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Create Feedback
        page_feedback.get_button_submit_new_feedback().click()
        page_new_feedback.choose_option_by_name("Negative feedback")
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_household_tab()
        page_new_feedback.get_household_table_rows(1).click()
        page_new_feedback.get_individual_tab().click()
        page_new_feedback.get_individual_table_row(2).click()
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_received_consent().click()
        page_new_feedback.get_button_next().click()
        assert "Feedback" in page_new_feedback.get_label_category().text
        page_new_feedback.get_description().send_keys("Test")
        page_new_feedback.get_button_next().click()
        # Check Details page
        assert "Test Programm" in page_feedback_details.get_programme().text
        page_feedback.get_nav_feedback().click()
        page_feedback.get_rows()

    def test_edit_feedback(
        self,
        create_programs: None,
        add_feedbacks: None,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        page_new_feedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Edit field Programme in Feedback
        page_feedback.get_row(0).click()
        assert "-" in page_feedback_details.get_programme().text
        page_feedback_details.get_button_edit().click()

        page_new_feedback.select_programme("Draft Program")
        page_new_feedback.get_description().click()
        page_new_feedback.clear_input(page_new_feedback.get_description())
        page_new_feedback.get_description().send_keys("New description")
        page_new_feedback.get_comments().send_keys("New comment, new comment. New comment?")
        page_new_feedback.get_input_area().send_keys("Abkamari")
        page_new_feedback.clear_input(page_new_feedback.get_input_language())
        page_new_feedback.get_input_language().send_keys("English")
        page_new_feedback.select_area("Shakardara")
        page_new_feedback.get_button_next().click()
        # Check edited Feedback
        assert "Draft Program" in page_feedback_details.get_programme().text
        assert "New description" in page_feedback_details.get_description().text
        assert "New comment, new comment. New comment?" in page_feedback_details.get_comments().text
        assert "Abkamari" in page_feedback_details.get_area_village_pay_point().text
        assert "English" in page_feedback_details.get_languages_spoken().text
        assert "Shakardara" in page_feedback_details.get_administrative_level2().text

    @pytest.mark.xfail(reason="UNSTABLE AFTER REST REFACTOR")
    def test_create_linked_ticket(
        self,
        page_grievance_new_ticket: NewTicket,
        page_grievance_details_page: GrievanceDetailsPage,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        create_programs: None,
        add_feedbacks: None,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        page_feedback.wait_for_rows()[0].click()
        page_feedback_details.get_button_create_linked_ticket().click()
        page_grievance_new_ticket.get_select_category().click()
        page_grievance_new_ticket.select_option_by_name("Referral")
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_household_tab()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_received_consent().click()
        page_grievance_new_ticket.get_button_next().click()
        page_grievance_new_ticket.get_description().send_keys("Linked Ticket Referral")
        page_grievance_new_ticket.get_button_next().click()
        assert "Linked Ticket Referral" in page_grievance_details_page.get_ticket_description().text
        grievance_ticket = page_grievance_details_page.get_title().text.split(" ")[-1]
        page_feedback.get_nav_feedback().click()
        assert grievance_ticket in page_feedback.wait_for_rows()[0].text
        page_feedback.wait_for_rows()[0].click()
        assert grievance_ticket in page_grievance_details_page.get_grievance_lined_ticket().text
        page_feedback.get_nav_feedback().click()
        page_feedback.wait_for_rows()[0].find_elements("tag name", "a")[0].click()

    def test_feedback_errors(
        self,
        page_feedback: Feedback,
        page_new_feedback: NewFeedback,
        page_feedback_details: FeedbackDetailsPage,
        create_households_and_individuals: Household,
    ) -> None:
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Create Feedback
        page_feedback.get_button_submit_new_feedback().click()
        # ToDo: Uncomment after fix 209087
        # page_new_feedback.get_button_next().click()
        # assert for page_new_feedback.get_error().text
        # with pytest.raises(Exception):
        #     page_new_feedback.get_household_tab()
        page_new_feedback.choose_option_by_name("Negative feedback")
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_household_tab()
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_received_consent()
        page_new_feedback.get_button_next().click()
        assert "Consent is required" in page_new_feedback.get_error().text
        page_new_feedback.get_received_consent().click()
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_description()
        page_new_feedback.get_button_next().click()
        assert "Description is required" in page_new_feedback.get_div_description().text
        page_new_feedback.get_description().send_keys("New description")
        page_new_feedback.get_button_next().click()
        assert "New description" in page_feedback_details.get_description().text

    def test_feedback_identity_verification(
        self,
        create_households_and_individuals: Household,
        page_feedback: Feedback,
        page_feedback_details: FeedbackDetailsPage,
        page_new_feedback: NewFeedback,
    ) -> None:
        page_feedback.get_menu_user_profile().click()
        page_feedback.get_menu_item_clear_cache().click()
        # Go to Feedback
        page_feedback.get_nav_grievance().click()
        page_feedback.get_nav_feedback().click()
        # Create Feedback
        page_feedback.get_button_submit_new_feedback().click()
        page_new_feedback.choose_option_by_name("Negative feedback")
        page_new_feedback.get_button_next().click()
        page_new_feedback.get_household_tab()
        page_new_feedback.get_household_table_rows(0).click()
        page_new_feedback.get_individual_tab().click()
        individual_name = page_new_feedback.get_individual_table_row(0).text.split(" HH")[0][17:]
        individual_unicef_id = page_new_feedback.get_individual_table_row(0).text.split(" ")[0]
        page_new_feedback.get_individual_table_row(0).click()
        page_new_feedback.get_button_next().click()

        page_new_feedback.get_input_questionnaire_size().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in page_new_feedback.get_label_household_size().text
        page_new_feedback.get_input_questionnaire_malechildrencount().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in page_new_feedback.get_label_number_of_male_children().text
        page_new_feedback.get_input_questionnaire_femalechildrencount().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in page_new_feedback.get_label_number_of_female_children().text
        page_new_feedback.get_input_questionnaire_childrendisabledcount().click()
        assert "-" in page_new_feedback.get_label_number_of_disabled_children().text
        page_new_feedback.get_input_questionnaire_headofhousehold().click()
        # TODO: Uncomment after fix: 211708
        # assert "" in page_new_feedback.get_label_head_of_household().text
        page_new_feedback.get_input_questionnaire_countryorigin().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in page_new_feedback.get_label_country_of_origin().text
        page_new_feedback.get_input_questionnaire_address().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in page_new_feedback.get_label_address().text
        page_new_feedback.get_input_questionnaire_village().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in page_new_feedback.get_label_village().text
        page_new_feedback.get_input_questionnaire_admin_1().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in page_new_feedback.get_label_administrative_level_1().text
        page_new_feedback.get_input_questionnaire_admin_2().click()
        assert "Shakardara" in page_new_feedback.get_label_administrative_level_2().text
        page_new_feedback.get_input_questionnaire_admin_3().click()
        assert "-" in page_new_feedback.get_label_administrative_level_3().text
        page_new_feedback.get_input_questionnaire_admin_4().click()
        assert "-" in page_new_feedback.get_label_administrative_level_4().text
        page_new_feedback.get_input_questionnaire_months_displaced_h_f().click()
        assert "-" in page_new_feedback.get_label_length_of_time_since_arrival().text
        page_new_feedback.get_input_questionnaire_fullname().click()
        assert (
            create_households_and_individuals.active_individuals.get(unicef_id=individual_unicef_id).full_name
            in page_new_feedback.get_label_individual_full_name().text
        )
        assert individual_name in page_new_feedback.get_label_individual_full_name().text
        page_new_feedback.get_input_questionnaire_birthdate().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in page_new_feedback.get_label_birth_date().text
        page_new_feedback.get_input_questionnaire_phoneno().click()
        assert "-" in page_new_feedback.get_label_phone_number().text
        page_new_feedback.get_input_questionnaire_relationship().click()
        # ToDo: Uncomment after fix: 211708
        # assert "Head of Household" in page_new_feedback.get_label_relationship_to_hoh().text
        page_new_feedback.get_received_consent().click()
        page_new_feedback.get_button_next().click()
        assert "Feedback" in page_new_feedback.get_label_category().text
