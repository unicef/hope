from django.db import transaction
from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.accountability.surveys import AccountabilitySurveys
from e2e.page_object.accountability.surveys_details import AccountabilitySurveysDetails
import pytest

from extras.test_utils.factories.accountability import SurveyFactory
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import PaymentPlanFactory
from hope.apps.account.models import User
from hope.apps.accountability.models import Survey
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.household.models import REFUGEE, Household
from hope.apps.payment.models import PaymentPlan
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.fixture
def add_household() -> Household:
    program = Program.objects.first()
    with transaction.atomic():
        household, individuals = create_household_and_individuals(
            household_data={
                "business_area": program.business_area,
                "program": program,
                "residence_status": REFUGEE,
            },
            individuals_data=[
                {"business_area": program.business_area, "observed_disability": []},
            ],
        )
        return household


@pytest.fixture
def add_accountability_surveys_message() -> Survey:
    ba = BusinessArea.objects.first()
    user = User.objects.first()
    cycle = Program.objects.get(name="Test Program").cycles.first()
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=user,
        business_area=ba,
        program_cycle=cycle,
    )
    return SurveyFactory(
        title="Test survey",
        category="MANUAL",
        unicef_id="SUR-24-0005",
        payment_plan=payment_plan,
        created_by=User.objects.first(),
    )


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
        assert "SUR-24-0005" in page_accountability_surveys.get_rows()[0].text
        assert "Test survey" in page_accountability_surveys.get_rows()[0].text

    def test_smoke_accountability_surveys_details(
        self,
        test_program: Program,
        add_accountability_surveys_message: Survey,
        add_household: Household,
        page_accountability_surveys: AccountabilitySurveys,
        page_accountability_surveys_details: AccountabilitySurveysDetails,
    ) -> None:
        add_accountability_surveys_message.recipients.set([Household.objects.first()])
        page_accountability_surveys.select_global_program_filter("Test Program")
        page_accountability_surveys.get_nav_accountability().click()
        page_accountability_surveys.get_nav_surveys().click()
        page_accountability_surveys.get_rows()[0].click()

        assert "SUR-24-0005" in page_accountability_surveys_details.get_page_header_title().text
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
            add_accountability_surveys_message.recipients.all()[0].unicef_id
            in page_accountability_surveys.get_rows()[0].text
        )
