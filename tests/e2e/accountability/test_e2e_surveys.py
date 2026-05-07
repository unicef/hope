from django.db import transaction
import pytest
from openpyxl.packaging import relationship

from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.accountability.surveys import AccountabilitySurveys
from e2e.page_object.accountability.surveys_details import AccountabilitySurveysDetails
from extras.test_utils.factories import HouseholdFactory, IndividualFactory, PaymentPlanFactory, SurveyFactory
from hope.models import REFUGEE, BusinessArea, DataCollectingType, Household, PaymentPlan, Program, Survey, User

pytestmark = pytest.mark.django_db()


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.fixture
def add_household(test_program: Program) -> Household:
    hoh = IndividualFactory(
        household=None,
        business_area=test_program.business_area,
        program=test_program,
        observed_disability=[],
        phone_no_alternative="+48123456789",
        phone_no="+48123456777",
        relationship="HEAD",
    )
    household = HouseholdFactory(
        program=test_program,
        business_area=test_program.business_area,
        residence_status=REFUGEE,
        head_of_household=hoh,
    )
    hoh.household = household
    hoh.save()
    return household


@pytest.fixture
def add_accountability_surveys_message(test_program: Program, add_household: Household) -> Survey:
    ba = test_program.business_area
    user = User.objects.first()
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=ba,
        program_cycle=test_program.cycles.first(),
    )
    survey = SurveyFactory(
        title="Test survey",
        category="MANUAL",
        payment_plan=payment_plan,
        created_by=user,
        business_area=ba,
        program=test_program,
        number_of_recipients=1
    )
    survey.recipients.add(add_household)
    return survey


@pytest.mark.usefixtures("login")
class TestSmokeAccountabilitySurveys:
    def test_smoke_accountability_surveys(
        self,
        test_program: Program,
        add_accountability_surveys_message: Survey,
        page_accountability_surveys: AccountabilitySurveys,
    ) -> None:
        page_accountability_surveys.select_global_program_filter("Test Program")
        page_accountability_surveys.get_nav_accountability().click()
        page_accountability_surveys.get_nav_surveys().click()

        assert "Surveys" in page_accountability_surveys.get_page_header_title().text
        assert "NEW SURVEY" in page_accountability_surveys.get_button_new_survey().text
        assert "Search" in page_accountability_surveys.get_filters_search().text
        assert "Target Population" in page_accountability_surveys.get_target_population_input().text
        assert "Created by" in page_accountability_surveys.get_filters_created_by_autocomplete().text
        assert "Created by" in page_accountability_surveys.get_created_by_input().text
        assert "From" in page_accountability_surveys.get_filters_creation_date_from().text
        assert "To" in page_accountability_surveys.get_filters_creation_date_to().text
        assert "CLEAR" in page_accountability_surveys.get_button_filters_clear().text
        assert "APPLY" in page_accountability_surveys.get_button_filters_apply().text
        assert "Surveys List" in page_accountability_surveys.get_table_title().text
        assert "Survey ID" in page_accountability_surveys.get_table_label()[0].text
        assert "Survey Title" in page_accountability_surveys.get_table_label()[1].text
        assert "Category" in page_accountability_surveys.get_table_label()[2].text
        assert "Number of Recipients" in page_accountability_surveys.get_table_label()[3].text
        assert "Created by" in page_accountability_surveys.get_table_label()[4].text
        assert "Creation Date" in page_accountability_surveys.get_table_label()[5].text
        assert "10 1–1 of 1" in page_accountability_surveys.get_table_pagination().text.replace("\n", " ")
        assert len(page_accountability_surveys.get_rows()) == 1
        assert add_accountability_surveys_message.unicef_id in page_accountability_surveys.get_rows()[0].text
        assert "Test survey" in page_accountability_surveys.get_rows()[0].text

    def test_smoke_accountability_surveys_details(
        self,
        test_program: Program,
        add_accountability_surveys_message: Survey,
        add_household: Household,
        page_accountability_surveys: AccountabilitySurveys,
        page_accountability_surveys_details: AccountabilitySurveysDetails,
    ) -> None:
        page_accountability_surveys.select_global_program_filter("Test Program")
        page_accountability_surveys.get_nav_accountability().click()
        page_accountability_surveys.get_nav_surveys().click()
        page_accountability_surveys.get_rows()[0].click()
        page_accountability_surveys.wait_for_page_ready()
        assert (
                add_accountability_surveys_message.unicef_id
                in page_accountability_surveys_details.get_page_header_title().text
        )
        assert "Survey with manual process" in page_accountability_surveys_details.get_label_category().text
        assert "Test survey" in page_accountability_surveys_details.get_label_survey_title().text
        created_by = add_accountability_surveys_message.created_by
        assert (
            f"{created_by.first_name} {created_by.last_name}"
            in page_accountability_surveys_details.get_label_created_by().text
        )
        assert (
            add_accountability_surveys_message.created_at.strftime("%-d %b %Y")
            in page_accountability_surveys_details.get_label_date_created().text
        )
        assert "Test Program" in page_accountability_surveys_details.get_label_programme().text
        assert "Items Group ID" in page_accountability_surveys_details.get_household_id().text
        assert "Status" in page_accountability_surveys_details.get_status().text
        assert "Head of Items Group" in page_accountability_surveys_details.get_household_head_name().text
        assert "Items Group Size" in page_accountability_surveys_details.get_household_size().text
        assert "Administrative Level 2" in page_accountability_surveys_details.get_household_location().text
        assert "Residence Status" in page_accountability_surveys_details.get_household_residence_status().text
        assert "Registration Date" in page_accountability_surveys_details.get_household_registration_date().text
        assert "Rows per page: 10 1–1 of 1" in page_accountability_surveys_details.get_table_pagination().text.replace(
            "\n", " "
        )
        assert len(page_accountability_surveys.get_rows()) == 1
        assert (
            add_accountability_surveys_message.recipients.first().unicef_id
            in page_accountability_surveys.get_rows()[0].text
        )
