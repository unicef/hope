from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.grievance.details_feedback_page import FeedbackDetailsPage
from page_object.grievance.feedback import Feedback
from page_object.grievance.new_feedback import NewFeedback
from page_object.programme_details.programme_details import ProgrammeDetails

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def add_feedbacks() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/accountability/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_households() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    return


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


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
        pageFeedback.getRows()[0].click()
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
        pageFeedback.getRows()[0].click()
        assert "-" in pageFeedbackDetails.getProgramme().text
        pageFeedbackDetails.getButtonEdit().click()
        pageNewFeedback.selectProgramme("Test Programm").click()
        pageNewFeedback.getButtonNext().click()
        # Check Feedback filtering by chosen Programme
        assert "Test Programm" in pageFeedbackDetails.getProgramme().text
        assert pageFeedback.globalProgramFilterText in pageFeedback.getGlobalProgramFilter().text
        pageFeedback.selectGlobalProgramFilter("Test Programm").click()
        assert "Test Programm" in pageProgrammeDetails.getHeaderTitle().text
        pageFeedback.wait_for_disappear(pageFeedback.navGrievanceDashboard)
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        pageFeedback.disappearTableRowLoading()
        assert 1 == len(pageFeedback.getRows())
        assert "Negative Feedback" in pageFeedback.getRows()[0].find_elements("tag name", "td")[1].text

        pageFeedback.selectGlobalProgramFilter("Draft Program").click()
        assert "Draft Program" in pageProgrammeDetails.getHeaderTitle().text
        pageFeedback.wait_for_disappear(pageFeedback.navGrievanceDashboard)
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
        assert 0 == len(pageFeedback.getRows())

        pageFeedback.selectGlobalProgramFilter("All Programmes").click()
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
        pageFeedback.getRows()[0].click()
        assert "-" in pageFeedbackDetails.getProgramme().text
        pageFeedbackDetails.getButtonEdit().click()
        pageNewFeedback.selectProgramme("Draft Programm").click()
        pageNewFeedback.getDescription().clear()
        pageNewFeedback.getDescription().send_keys("New description")
        pageNewFeedback.getComments().clear()
        pageNewFeedback.getComments().send_keys("New comment, new comment. New comment?")
        pageNewFeedback.getInputArea().clear()
        pageNewFeedback.getInputArea().send_keys("Abkamari")
        pageNewFeedback.getInputLanguage().clear()
        pageNewFeedback.getInputLanguage().send_keys("English")
        pageNewFeedback.getAdminAreaAutocomplete().click()
        pageNewFeedback.screenshot("tutu")

    @pytest.mark.skip(reason="Create during Grievance tickets creation tests")
    def test_create_linked_ticket(
        self,
        pageFeedback: Feedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavGrievance().click()
        pageFeedback.getNavFeedback().click()
