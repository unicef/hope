from django.db import transaction

import pytest

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.accountability.fixtures import SurveyFactory
from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import REFUGEE, Household
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from tests.selenium.helpers.fixtures import get_program_with_dct_type_and_name
from tests.selenium.page_object.accountability.surveys import AccountabilitySurveys
from tests.selenium.page_object.accountability.surveys_details import (
    AccountabilitySurveysDetails,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.fixture
def add_household() -> Household:
    program = Program.objects.first()
    with transaction.atomic():
        household, individuals = create_household_and_individuals(
            household_data={"business_area": program.business_area, "program": program, "residence_status": REFUGEE},
            individuals_data=[
                {"business_area": program.business_area, "observed_disability": []},
            ],
        )
        return household


@pytest.fixture
def add_accountability_surveys_message() -> Survey:
    targeting_criteria = TargetingCriteriaFactory()

    target_population = TargetPopulationFactory(
        created_by=User.objects.first(),
        targeting_criteria=targeting_criteria,
        business_area=BusinessArea.objects.first(),
    )
    return SurveyFactory(
        title="Test survey",
        category="MANUAL",
        unicef_id="SUR-24-0005",
        target_population=target_population,
        created_by=User.objects.first(),
    )


@pytest.mark.usefixtures("login")
class TestSmokeAccountabilitySurveys:
    def test_smoke_accountability_surveys(
        self,
        test_program: Program,
        add_accountability_surveys_message: Survey,
        pageAccountabilitySurveys: AccountabilitySurveys,
    ) -> None:
        pageAccountabilitySurveys.selectGlobalProgramFilter("Test Program")
        pageAccountabilitySurveys.getNavAccountability().click()
        pageAccountabilitySurveys.getNavSurveys().click()

        assert "Surveys" in pageAccountabilitySurveys.getPageHeaderTitle().text
        assert "NEW SURVEY" in pageAccountabilitySurveys.getButtonNewSurvey().text
        assert "Search" in pageAccountabilitySurveys.getFiltersSearch().text
        assert "Target Population" in pageAccountabilitySurveys.getTargetPopulationInput().text
        assert "Created by" in pageAccountabilitySurveys.getFiltersCreatedByAutocomplete().text
        assert "Created by" in pageAccountabilitySurveys.getCreatedByInput().text
        assert "From" in pageAccountabilitySurveys.getFiltersCreationDateFrom().text
        assert "To" in pageAccountabilitySurveys.getFiltersCreationDateTo().text
        assert "CLEAR" in pageAccountabilitySurveys.getButtonFiltersClear().text
        assert "APPLY" in pageAccountabilitySurveys.getButtonFiltersApply().text
        assert "Surveys List" in pageAccountabilitySurveys.getTableTitle().text
        assert "Survey ID" in pageAccountabilitySurveys.getTableLabel()[0].text
        assert "Survey Title" in pageAccountabilitySurveys.getTableLabel()[1].text
        assert "Category" in pageAccountabilitySurveys.getTableLabel()[2].text
        assert "Number of Recipients" in pageAccountabilitySurveys.getTableLabel()[3].text
        assert "Created by" in pageAccountabilitySurveys.getTableLabel()[4].text
        assert "Creation Date" in pageAccountabilitySurveys.getTableLabel()[5].text
        assert "10 1–1 of 1" in pageAccountabilitySurveys.getTablePagination().text.replace("\n", " ")
        assert 1 == len(pageAccountabilitySurveys.getRows())
        assert "SUR-24-0005" in pageAccountabilitySurveys.getRows()[0].text
        assert "Test survey" in pageAccountabilitySurveys.getRows()[0].text

    def test_smoke_accountability_surveys_details(
        self,
        test_program: Program,
        add_accountability_surveys_message: Survey,
        add_household: Household,
        pageAccountabilitySurveys: AccountabilitySurveys,
        pageAccountabilitySurveysDetails: AccountabilitySurveysDetails,
    ) -> None:
        add_accountability_surveys_message.recipients.set([Household.objects.first()])
        pageAccountabilitySurveys.selectGlobalProgramFilter("Test Program")
        pageAccountabilitySurveys.getNavAccountability().click()
        pageAccountabilitySurveys.getNavSurveys().click()
        pageAccountabilitySurveys.getRows()[0].click()

        assert "SUR-24-0005" in pageAccountabilitySurveysDetails.getPageHeaderTitle().text
        assert "Survey with manual process" in pageAccountabilitySurveysDetails.getLabelCategory().text
        assert "Test survey" in pageAccountabilitySurveysDetails.getLabelSurveyTitle().text
        created_by = add_accountability_surveys_message.created_by
        assert (
            f"{created_by.first_name} {created_by.last_name}"
            in pageAccountabilitySurveysDetails.getLabelCreatedBy().text
        )
        assert (
            add_accountability_surveys_message.created_at.strftime("%-d %b %Y")
            in pageAccountabilitySurveysDetails.getLabelDateCreated().text
        )
        assert "Test Program" in pageAccountabilitySurveysDetails.getLabelProgramme().text
        assert "Household Id" in pageAccountabilitySurveysDetails.getHouseholdId().text
        assert "Status" in pageAccountabilitySurveysDetails.getStatus().text
        assert "Head of Household" in pageAccountabilitySurveysDetails.getHouseholdHeadName().text
        assert "Household Size" in pageAccountabilitySurveysDetails.getHouseholdSize().text
        assert "Administrative Level 2" in pageAccountabilitySurveysDetails.getHouseholdLocation().text
        assert "Residence Status" in pageAccountabilitySurveysDetails.getHouseholdResidenceStatus().text
        assert "Registration Date" in pageAccountabilitySurveysDetails.getHouseholdRegistrationDate().text
        assert "Rows per page: 10 1–1 of 1" in pageAccountabilitySurveysDetails.getTablePagination().text.replace(
            "\n", " "
        )
        assert 1 == len(pageAccountabilitySurveys.getRows())
        assert (
            add_accountability_surveys_message.recipients.all()[0].unicef_id
            in pageAccountabilitySurveys.getRows()[0].text
        )
