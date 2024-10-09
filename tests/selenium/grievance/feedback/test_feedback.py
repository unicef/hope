from typing import Generator

from django.conf import settings
from django.core.management import call_command

import pytest
from selenium.webdriver import Keys

from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import HOST, Household
from tests.selenium.helpers.fixtures import get_program_with_dct_type_and_name
from tests.selenium.page_object.grievance.details_feedback_page import (
    FeedbackDetailsPage,
)
from tests.selenium.page_object.grievance.details_grievance_page import (
    GrievanceDetailsPage,
)
from tests.selenium.page_object.grievance.feedback import Feedback
from tests.selenium.page_object.grievance.new_feedback import NewFeedback
from tests.selenium.page_object.grievance.new_ticket import NewTicket
from tests.selenium.page_object.programme_details.programme_details import (
    ProgrammeDetails,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def add_feedbacks() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/accountability/fixtures/data-cypress.json")
    yield


@pytest.fixture
def add_households() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    yield


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    yield


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
        pageFeedback: Feedback,
    ) -> None:
        """
        Go to Grievance page
        Go to Feedback page
        Check if all elements on page exist
        """
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Check Feedback page
        pageFeedback.getTitlePage()
        pageFeedback.getButtonSubmitNewFeedback()
        pageFeedback.getFilterSearch()
        pageFeedback.getFilterIssueType()
        pageFeedback.getFilterCreatedBy()
        pageFeedback.getFilterCreationDateFrom()
        pageFeedback.getFilterCreationDateTo()
        pageFeedback.getButtonClear()
        pageFeedback.getButtonApply()
        assert pageFeedback.textTableTitle in pageFeedback.getTableTitle().text
        assert pageFeedback.textFeedbackID in pageFeedback.getFeedbackID().text
        assert pageFeedback.textIssueType in pageFeedback.getIssueType().text
        assert pageFeedback.textHouseholdID in pageFeedback.getHouseholdID().text
        assert pageFeedback.textLinkedGrievance in pageFeedback.getLinkedGrievance().text
        assert pageFeedback.textCreatedBy in pageFeedback.getCreatedBy().text
        assert pageFeedback.textCreationDate in pageFeedback.getCreationDate().text

    def test_check_feedback_details_page(
        self,
        add_feedbacks: None,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
    ) -> None:
        """
        Go to Grievance page
        Go to Feedback page
        Choose Feedback
        Check if all elements on page exist
        """
        # Go to Feedback
        pageFeedback.driver.refresh()
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        pageFeedback.getRow(0).click()
        # Check Feedback details page
        assert pageFeedbackDetails.textTitle in pageFeedbackDetails.getTitlePage().text
        pageFeedbackDetails.getButtonEdit()
        assert pageFeedbackDetails.textCategory in pageFeedbackDetails.getCategory().text
        assert pageFeedbackDetails.textIssueType in pageFeedbackDetails.getIssueType().text
        pageFeedbackDetails.getHouseholdID()
        pageFeedbackDetails.getIndividualID()
        pageFeedbackDetails.getCreatedBy()
        pageFeedbackDetails.getDateCreated()
        pageFeedbackDetails.getLastModifiedDate()
        pageFeedbackDetails.getAdministrativeLevel2()


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
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        pageNewFeedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Create Feedback
        pageFeedback.getButtonSubmitNewFeedback().click()
        pageNewFeedback.chooseOptionByName(issue_type)
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getHouseholdTab()
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getReceivedConsent().click()
        pageNewFeedback.getButtonNext().click()
        assert "Feedback" in pageNewFeedback.getLabelCategory().text
        pageNewFeedback.getDescription().send_keys("Test")
        pageNewFeedback.check_page_after_click(pageNewFeedback.getButtonNext(), "=")
        # Check Details page
        assert pageFeedbackDetails.textCategory in pageFeedbackDetails.getCategory().text
        assert issue_type in pageFeedbackDetails.getIssueType().text
        assert "-" in pageFeedbackDetails.getHouseholdID().text
        assert "-" in pageFeedbackDetails.getIndividualID().text
        assert "-" in pageFeedbackDetails.getProgramme().text
        assert "Test" in pageFeedbackDetails.getDescription().text
        pageFeedbackDetails.getLastModifiedDate()
        pageFeedbackDetails.getAdministrativeLevel2()

    @pytest.mark.parametrize("issue_type", ["Positive", "Negative"])
    def test_create_feedback_optional_fields(
        self,
        issue_type: None,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        pageNewFeedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Create Feedback
        pageFeedback.getButtonSubmitNewFeedback().click()
        pageNewFeedback.chooseOptionByName(issue_type)
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getHouseholdTab()
        pageNewFeedback.getIndividualTab()
        pageFeedback.getTableRowLoading()
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getReceivedConsent().click()
        pageNewFeedback.getButtonNext().click()
        assert "Feedback" in pageNewFeedback.getLabelCategory().text
        pageNewFeedback.getDescription().send_keys("Test")
        pageNewFeedback.check_page_after_click(pageNewFeedback.getButtonNext(), "=")
        # Check Details page
        assert pageFeedbackDetails.textCategory in pageFeedbackDetails.getCategory().text
        assert issue_type in pageFeedbackDetails.getIssueType().text
        assert "-" in pageFeedbackDetails.getHouseholdID().text
        assert "-" in pageFeedbackDetails.getIndividualID().text
        assert "-" in pageFeedbackDetails.getProgramme().text
        assert "Test" in pageFeedbackDetails.getDescription().text
        pageFeedbackDetails.getLastModifiedDate()
        pageFeedbackDetails.getAdministrativeLevel2()

    def test_check_feedback_filtering_by_chosen_programme(
        self,
        create_programs: None,
        add_feedbacks: None,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        pageNewFeedback: NewFeedback,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Edit field Programme in Feedback
        pageFeedback.getRow(0).click()
        assert "-" in pageFeedbackDetails.getProgramme().text
        pageFeedbackDetails.getButtonEdit().click()
        pageNewFeedback.selectProgramme("Test Programm")
        pageNewFeedback.getButtonNext().click()
        # Check Feedback filtering by chosen Programme
        assert "Test Programm" in pageFeedbackDetails.getProgramme().text
        assert pageFeedback.globalProgramFilterText in pageFeedback.getGlobalProgramFilter().text
        pageFeedback.selectGlobalProgramFilter("Test Programm")
        assert "Test Programm" in pageProgrammeDetails.getHeaderTitle().text
        pageFeedback.wait_for_disappear(pageFeedback.navGrievanceDashboard)
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        pageFeedback.disappearTableRowLoading()
        assert 1 == len(pageFeedback.getRows())
        assert "Negative Feedback" in pageFeedback.getRow(0).find_elements("tag name", "td")[1].text

        pageFeedback.selectGlobalProgramFilter("Draft Program")
        assert "Draft Program" in pageProgrammeDetails.getHeaderTitle().text
        pageFeedback.wait_for_disappear(pageFeedback.navGrievanceDashboard)
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        assert 0 == len(pageFeedback.getRows())

        pageFeedback.selectGlobalProgramFilter("All Programmes")
        assert "Programme Management" in pageProgrammeDetails.getHeaderTitle().text
        pageFeedback.wait_for_disappear(pageFeedback.navGrievanceDashboard)
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        pageFeedback.disappearTableRowLoading()
        assert 2 == len(pageFeedback.getRows())

    def test_create_feedback_with_household(
        self,
        create_programs: None,
        add_households: None,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        pageNewFeedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Create Feedback
        pageFeedback.getButtonSubmitNewFeedback().click()
        pageNewFeedback.chooseOptionByName("Negative feedback")
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getHouseholdTab()
        pageNewFeedback.getHouseholdTableRows(1).click()
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getReceivedConsent().click()
        pageNewFeedback.getButtonNext().click()
        assert "Feedback" in pageNewFeedback.getLabelCategory().text
        pageNewFeedback.getDescription().send_keys("Test")
        pageNewFeedback.check_page_after_click(pageNewFeedback.getButtonNext(), "=")
        # Check Details page
        assert "Test Programm" in pageFeedbackDetails.getProgramme().text
        pageFeedback.getNavFeedback().click()
        pageFeedback.getRows()

    def test_create_feedback_with_household_and_individual(
        self,
        create_programs: None,
        add_households: None,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        pageNewFeedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Create Feedback
        pageFeedback.getButtonSubmitNewFeedback().click()
        pageNewFeedback.chooseOptionByName("Negative feedback")
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getHouseholdTab()
        pageNewFeedback.getHouseholdTableRows(1).click()
        pageNewFeedback.getIndividualTab().click()
        pageNewFeedback.getIndividualTableRow(2).click()
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getReceivedConsent().click()
        pageNewFeedback.getButtonNext().click()
        assert "Feedback" in pageNewFeedback.getLabelCategory().text
        pageNewFeedback.getDescription().send_keys("Test")
        pageNewFeedback.check_page_after_click(pageNewFeedback.getButtonNext(), "=")
        # Check Details page
        assert "Test Programm" in pageFeedbackDetails.getProgramme().text
        pageFeedback.getNavFeedback().click()
        pageFeedback.getRows()

    def test_create_feedback_with_individual(
        self,
        create_programs: None,
        add_households: None,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        pageNewFeedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Create Feedback
        pageFeedback.getButtonSubmitNewFeedback().click()
        pageNewFeedback.chooseOptionByName("Negative feedback")
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getHouseholdTab()
        pageNewFeedback.getHouseholdTableRows(1).click()
        pageNewFeedback.getIndividualTab().click()
        pageNewFeedback.getIndividualTableRow(2).click()
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getReceivedConsent().click()
        pageNewFeedback.getButtonNext().click()
        assert "Feedback" in pageNewFeedback.getLabelCategory().text
        pageNewFeedback.getDescription().send_keys("Test")
        pageNewFeedback.check_page_after_click(pageNewFeedback.getButtonNext(), "=")
        # Check Details page
        assert "Test Programm" in pageFeedbackDetails.getProgramme().text
        pageFeedback.getNavFeedback().click()
        pageFeedback.getRows()

    def test_edit_feedback(
        self,
        create_programs: None,
        add_feedbacks: None,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        pageNewFeedback: NewFeedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Edit field Programme in Feedback
        pageFeedback.getRow(0).click()
        assert "-" in pageFeedbackDetails.getProgramme().text
        pageFeedbackDetails.getButtonEdit().click()
        from hct_mis_api.apps.program.models import Program

        print(Program.objects.all())
        pageNewFeedback.selectProgramme("Draft Program")
        pageNewFeedback.getDescription().click()
        pageNewFeedback.getDescription().send_keys(Keys.CONTROL, "a")
        pageNewFeedback.getDescription().send_keys("New description")
        pageNewFeedback.getComments().send_keys("New comment, new comment. New comment?")
        pageNewFeedback.getInputArea().send_keys("Abkamari")
        pageNewFeedback.getInputLanguage().send_keys("English")
        pageNewFeedback.selectArea("Shakardara")
        pageNewFeedback.getButtonNext().click()
        # Check edited Feedback
        assert "Draft Program" in pageFeedbackDetails.getProgramme().text
        assert "New description" in pageFeedbackDetails.getDescription().text
        assert "New comment, new comment. New comment?" in pageFeedbackDetails.getComments().text
        assert "Abkamari" in pageFeedbackDetails.getAreaVillagePayPoint().text
        assert "English" in pageFeedbackDetails.getLanguagesSpoken().text

    def test_create_linked_ticket(
        self,
        pageGrievanceNewTicket: NewTicket,
        pageGrievanceDetailsPage: GrievanceDetailsPage,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        add_feedbacks: None,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        pageFeedback.waitForRows()[0].click()
        pageFeedbackDetails.getButtonCreateLinkedTicket().click()
        pageGrievanceNewTicket.getSelectCategory().click()
        pageGrievanceNewTicket.select_option_by_name("Referral")
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getHouseholdTab()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getReceivedConsent().click()
        pageGrievanceNewTicket.getButtonNext().click()
        pageGrievanceNewTicket.getDescription().send_keys("Linked Ticket Referral")
        pageGrievanceNewTicket.getButtonNext().click()
        assert "Linked Ticket Referral" in pageGrievanceDetailsPage.getTicketDescription().text
        grievance_ticket = pageGrievanceDetailsPage.getTitle().text.split(" ")[-1]
        pageFeedback.getNavFeedback().click()
        assert grievance_ticket in pageFeedback.waitForRows()[0].text
        pageFeedback.waitForRows()[0].click()
        assert grievance_ticket in pageGrievanceDetailsPage.getTitle().text.split(" ")[-1]
        pageFeedback.getNavFeedback().click()
        pageFeedback.waitForRows()[0].find_elements("tag name", "a")[0].click()

    def test_feedback_errors(
        self,
        pageFeedback: Feedback,
        pageNewFeedback: NewFeedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        create_households_and_individuals: Household,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Create Feedback
        pageFeedback.getButtonSubmitNewFeedback().click()
        # ToDo: Uncomment after fix 209087
        # pageNewFeedback.getButtonNext().click()
        # assert for pageNewFeedback.getError().text
        # with pytest.raises(Exception):
        #     pageNewFeedback.getHouseholdTab()
        pageNewFeedback.chooseOptionByName("Negative feedback")
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getHouseholdTab()
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getReceivedConsent()
        pageNewFeedback.getButtonNext().click()
        assert "Consent is required" in pageNewFeedback.getError().text
        pageNewFeedback.getReceivedConsent().click()
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getDescription()
        pageNewFeedback.getButtonNext().click()
        assert "Description is required" in pageNewFeedback.getDivDescription().text
        pageNewFeedback.getDescription().send_keys("New description")
        pageNewFeedback.getButtonNext().click()
        assert "New description" in pageFeedbackDetails.getDescription().text

    def test_feedback_identity_verification(
        self,
        create_households_and_individuals: Household,
        pageFeedback: Feedback,
        pageFeedbackDetails: FeedbackDetailsPage,
        pageNewFeedback: NewFeedback,
    ) -> None:
        pageFeedback.getMenuUserProfile().click()
        pageFeedback.getMenuItemClearCache().click()
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        # Create Feedback
        pageFeedback.getButtonSubmitNewFeedback().click()
        pageNewFeedback.chooseOptionByName("Negative feedback")
        pageNewFeedback.getButtonNext().click()
        pageNewFeedback.getHouseholdTab()
        pageNewFeedback.getHouseholdTableRows(0).click()
        pageNewFeedback.getIndividualTab().click()
        individual_name = pageNewFeedback.getIndividualTableRow(0).text.split(" HH")[0][17:]
        individual_unicef_id = pageNewFeedback.getIndividualTableRow(0).text.split(" ")[0]
        pageNewFeedback.getIndividualTableRow(0).click()
        pageNewFeedback.getButtonNext().click()

        pageNewFeedback.getInputQuestionnaire_size().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in pageNewFeedback.getLabelHouseholdSize().text
        pageNewFeedback.getInputQuestionnaire_malechildrencount().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in pageNewFeedback.getLabelNumberOfMaleChildren().text
        pageNewFeedback.getInputQuestionnaire_femalechildrencount().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in pageNewFeedback.getLabelNumberOfFemaleChildren().text
        pageNewFeedback.getInputQuestionnaire_childrendisabledcount().click()
        assert "-" in pageNewFeedback.getLabelNumberOfDisabledChildren().text
        pageNewFeedback.getInputQuestionnaire_headofhousehold().click()
        # ToDo: Uncomment after fix: 211708
        # assert "" in pageNewFeedback.getLabelHeadOfHousehold().text
        pageNewFeedback.getInputQuestionnaire_countryorigin().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in pageNewFeedback.getLabelCountryOfOrigin().text
        pageNewFeedback.getInputQuestionnaire_address().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in pageNewFeedback.getLabelAddress().text
        pageNewFeedback.getInputQuestionnaire_village().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in pageNewFeedback.getLabelVillage().text
        pageNewFeedback.getInputQuestionnaire_admin1().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in pageNewFeedback.getLabelAdministrativeLevel1().text
        pageNewFeedback.getInputQuestionnaire_admin2().click()
        assert "Shakardara" in pageNewFeedback.getLabelAdministrativeLevel2().text
        pageNewFeedback.getInputQuestionnaire_admin3().click()
        assert "-" in pageNewFeedback.getLabelAdministrativeLevel3().text
        pageNewFeedback.getInputQuestionnaire_admin4().click()
        assert "-" in pageNewFeedback.getLabelAdministrativeLevel4().text
        pageNewFeedback.getInputQuestionnaire_months_displaced_h_f().click()
        assert "-" in pageNewFeedback.getLabelLengthOfTimeSinceArrival().text
        pageNewFeedback.getInputQuestionnaire_fullname().click()
        assert (
            create_households_and_individuals.active_individuals.get(unicef_id=individual_unicef_id).full_name
            in pageNewFeedback.getLabelIndividualFullName().text
        )
        assert individual_name in pageNewFeedback.getLabelIndividualFullName().text
        pageNewFeedback.getInputQuestionnaire_birthdate().click()
        # ToDo: Uncomment after fix: 211708
        # assert "-" in pageNewFeedback.getLabelBirthDate().text
        pageNewFeedback.getInputQuestionnaire_phoneno().click()
        assert "-" in pageNewFeedback.getLabelPhoneNumber().text
        pageNewFeedback.getInputQuestionnaire_relationship().click()
        # ToDo: Uncomment after fix: 211708
        # assert "Head of Household" in pageNewFeedback.getLabelRelationshipToHoh().text
        pageNewFeedback.getReceivedConsent().click()
        pageNewFeedback.getButtonNext().click()
        assert "Feedback" in pageNewFeedback.getLabelCategory().text
