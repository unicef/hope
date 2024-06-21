import pytest
from helpers.fixtures import get_program_with_dct_type_and_name
from page_object.accountability.communication import AccountabilityCommunication
from page_object.accountability.comunication_details import (
    AccountabilityCommunicationDetails,
)

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

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def test_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.fixture
def add_accountability_communication_message() -> Message:
    targeting_criteria = TargetingCriteriaFactory()

    target_population = TargetPopulationFactory(
        created_by=User.objects.first(),
        targeting_criteria=targeting_criteria,
        business_area=BusinessArea.objects.first(),
    )
    return CommunicationMessageFactory(
        unicef_id="MSG-24-0666",
        title="You got credit of USD 100",
        body="Greetings, we have sent you USD 100 in your registered account on 2022-09-19 20:00:00 UTC",
        business_area=BusinessArea.objects.first(),
        target_population=target_population,
        created_by=User.objects.first(),
    )


@pytest.mark.usefixtures("login")
class TestSmokeAccountabilityCommunication:
    def test_smoke_accountability_communication(
        self,
        test_program: Program,
        add_accountability_communication_message: Message,
        pageAccountabilityCommunication: AccountabilityCommunication,
    ) -> None:
        pageAccountabilityCommunication.selectGlobalProgramFilter("Test Program").click()
        pageAccountabilityCommunication.getNavAccountability().click()
        assert "Communication" in pageAccountabilityCommunication.getPageHeaderTitle().text
        assert "NEW MESSAGE" in pageAccountabilityCommunication.getButtonCommunicationCreateNew().text
        assert "Target Population" in pageAccountabilityCommunication.getFiltersTargetPopulationAutocomplete().text
        assert "Target Population" in pageAccountabilityCommunication.getTargetPopulationInput().text
        assert "Created by" in pageAccountabilityCommunication.getFiltersCreatedByAutocomplete().text
        assert "Created by" in pageAccountabilityCommunication.getCreatedByInput().text
        assert "From" in pageAccountabilityCommunication.getFiltersCreationDateFrom().text
        assert "To" in pageAccountabilityCommunication.getFiltersCreationDateTo().text
        assert "CLEAR" in pageAccountabilityCommunication.getButtonFiltersClear().text
        assert "APPLY" in pageAccountabilityCommunication.getButtonFiltersApply().text
        assert "Messages List" in pageAccountabilityCommunication.getTableTitle().text
        assert "Message ID" in pageAccountabilityCommunication.getTableLabel()[0].text
        assert "Title" in pageAccountabilityCommunication.getTableLabel()[1].text
        assert "Number of Recipients" in pageAccountabilityCommunication.getTableLabel()[2].text
        assert "Created by" in pageAccountabilityCommunication.getTableLabel()[3].text
        assert "Creation Date" in pageAccountabilityCommunication.getTableLabel()[4].text
        assert "Rows per page: 10 1–1 of 1" in pageAccountabilityCommunication.getTablePagination().text.replace(
            "\n", " "
        )
        assert 1 == len(pageAccountabilityCommunication.getRows())

    def test_smoke_accountability_communication_details(
        self,
        test_program: Program,
        add_accountability_communication_message: Message,
        pageAccountabilityCommunication: AccountabilityCommunication,
        pageAccountabilityCommunicationDetails: AccountabilityCommunicationDetails,
    ) -> None:
        pageAccountabilityCommunication.selectGlobalProgramFilter("Test Program").click()
        pageAccountabilityCommunication.getNavAccountability().click()
        pageAccountabilityCommunication.getRows()[0].click()
        # pageAccountabilityCommunication.screenshot("123")
        #
        # from selenium_tests.tools.tag_name_finder import printing
        # printing("Mapping", pageAccountabilityCommunication.driver)
        # printing("Methods", pageAccountabilityCommunication.driver)
        # printing("Assert", pageAccountabilityCommunication.driver)
        assert "MSG-24-0666" in pageAccountabilityCommunicationDetails.getPageHeaderTitle().text
        created_by = add_accountability_communication_message.created_by
        assert (
            f"{created_by.first_name} {created_by.last_name}"
            in pageAccountabilityCommunicationDetails.getLabelCreatedBy().text
        )
        assert (
            add_accountability_communication_message.created_at.strftime("%-d %b %Y")
            in pageAccountabilityCommunicationDetails.getLabelDateCreated().text
        )
        assert (
            TargetPopulation.objects.first().name
            in pageAccountabilityCommunicationDetails.getLabelTargetPopulation().text
        )
        assert "Recipients" in pageAccountabilityCommunicationDetails.getTableTitle().text
        assert "Household Id" in pageAccountabilityCommunicationDetails.getHouseholdId().text
        assert "Status" in pageAccountabilityCommunicationDetails.getStatus().text
        assert "Head of Household" in pageAccountabilityCommunicationDetails.getHouseholdHeadName().text
        assert "Household Size" in pageAccountabilityCommunicationDetails.getHouseholdSize().text
        assert "Administrative Level 2" in pageAccountabilityCommunicationDetails.getHouseholdLocation().text
        assert "Residence Status" in pageAccountabilityCommunicationDetails.getHouseholdResidenceStatus().text
        assert "Registration Date" in pageAccountabilityCommunicationDetails.getHouseholdRegistrationDate().text
        assert (
            "No results Try adjusting your search or your filters to find what you are looking for."
            in pageAccountabilityCommunicationDetails.getTableRow().text.replace("\n", " ")
        )
        assert "Rows per page: 10 0–0 of 0" in pageAccountabilityCommunicationDetails.getTablePagination().text.replace(
            "\n", " "
        )
