import random

import pytest
from page_object.grievance.details_feedback_page import FeedbackDetailsPage
from page_object.grievance.feedback import Feedback
from page_object.grievance.new_feedback import NewFeedback
from django.conf import settings
from django.core.management import call_command

from hct_mis_api.apps.core.models import BusinessArea

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def add_feedbacks():
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/accountability/fixtures/data-cypress.json")
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


@pytest.mark.skip(reason="ToDo")
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

#
# @pytest.mark.skip(reason="ToDo")
# @pytest.mark.usefixtures("login")
# class TestFeedback:
#     @pytest.mark.parametrize(
#         "test_data",
#         [
#             pytest.param(
#                 {
#                     "description": "New Feedback - " + str(random.random()),
#                     "type": "Negative",
#                 },
#                 id="Negative",
#             ),
#         ],
#         [
#             pytest.param(
#                 {
#                     "description": "New Feedback - " + str(random.random()),
#                     "type": "Positive",
#                 },
#                 id="Positive",
#             ),
#         ],
#     )
#     def test_create_feedback_mandatory_fields(
#         self,
#         pageFeedback: Feedback,
#         pageFeedbackDetails: FeedbackDetailsPage,
#         pageNewFeedback: NewFeedback,
#         test_data: dict,
#     ) -> None:
#         # Go to Feedback
#         pageFeedback.getNavFeedback().click()
#         # Create Feedback
#
#         # Check Details page
#
#     def test_create_feedback_optional_fields(
#         self,
#         pageFeedback: Feedback,
#         pageFeedbackDetails: FeedbackDetailsPage,
#         pageNewFeedback: NewFeedback,
#         test_data: dict,
#     ) -> None:
#         # Go to Feedback
#         pageFeedback.getNavFeedback().click()
#
#     def test_create_feedback_with_household(
#         self,
#         pageFeedback: Feedback,
#     ) -> None:
#         # Go to Feedback
#         pageFeedback.getNavFeedback().click()
#
#     def test_create_feedback_with_individual(
#         self,
#         pageFeedback: Feedback,
#     ) -> None:
#         # Go to Feedback
#         pageFeedback.getNavFeedback().click()
#
#     def test_create_feedback_error_messages(
#         self,
#         pageFeedback: Feedback,
#         pageFeedbackDetails: FeedbackDetailsPage,
#         pageNewFeedback: NewFeedback,
#         test_data: dict,
#     ) -> None:
#         # Go to Feedback
#         pageFeedback.getNavFeedback().click()
#
#     def test_create_linked_ticket(
#         self,
#         pageFeedback: Feedback,
#         pageFeedbackDetails: FeedbackDetailsPage,
#         pageNewFeedback: NewFeedback,
#         test_data: dict,
#     ) -> None:
#         # Go to Feedback
#         pageFeedback.getNavFeedback().click()
#
#     def test_edit_feedback(
#         self,
#         pageFeedback: Feedback,
#         pageFeedbackDetails: FeedbackDetailsPage,
#         pageNewFeedback: NewFeedback,
#         test_data: dict,
#     ) -> None:
#         # Go to Feedback
#         pageFeedback.getNavFeedback().click()
