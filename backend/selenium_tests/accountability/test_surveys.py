import pytest
from helpers.fixtures import get_program_with_dct_type_and_name

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.accountability.fixtures import CommunicationMessageFactory
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import TargetPopulation

from page_object.accountability.surveys import AccountabilitySurveys
from page_object.accountability.surveys_details import AccountabilitySurveysDetails

from hct_mis_api.apps.accountability.fixtures import SurveyFactory
from hct_mis_api.apps.accountability.models import Survey

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.fixture
def add_accountability_surveys_message() -> Survey:
    targeting_criteria = TargetingCriteriaFactory()

    target_population = TargetPopulationFactory(
        created_by=User.objects.first(),
        targeting_criteria=targeting_criteria,
        business_area=BusinessArea.objects.first(),
    )
    return SurveyFactory(title="Test survey",
                         target_population=target_population,
                         created_by=User.objects.first())


@pytest.mark.usefixtures("login")
class TestSmokeAccountabilitySurveys:
    def test_smoke_accountability_surveys(
        self,
        test_program: Program,
        add_accountability_surveys_message: Survey,
        pageAccountabilitySurveys: AccountabilitySurveys,
    ) -> None:
        pageAccountabilitySurveys.selectGlobalProgramFilter("Test Program").click()
        pageAccountabilitySurveys.getNavAccountability().click()
        pageAccountabilitySurveys.getNavSurveys().click()

        pageAccountabilitySurveys.screenshot("AccountabilitySurveys")
        from selenium_tests.tools.tag_name_finder import printing
        printing("Mapping", pageAccountabilitySurveys.driver)
        printing("Methods", pageAccountabilitySurveys.driver)
        printing("Assert", pageAccountabilitySurveys.driver)

    @pytest.mark.skip()
    def test_smoke_accountability_surveys_details(
        self,
        test_program: Program,
        add_accountability_surveys_message: Survey,
        pageAccountabilitySurveys: AccountabilitySurveys,
        pageAccountabilitySurveysDetails: AccountabilitySurveysDetails,
    ) -> None:
        pageAccountabilitySurveys.selectGlobalProgramFilter("Test Program").click()
        pageAccountabilitySurveys.getNavAccountability().click()
        pageAccountabilitySurveys.getNavSurveys().click()
        pageAccountabilitySurveys.getRows()[0].click()
