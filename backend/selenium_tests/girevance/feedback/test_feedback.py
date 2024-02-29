import random

import pytest
from page_object.grievance.details_feedback_page import FeedbackDetailsPage
from page_object.grievance.feedback import Feedback
from page_object.grievance.new_feedback import NewFeedback
from page_object.filters import Filters

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.skip(reason="ToDo")
@pytest.mark.usefixtures("login")
class TestSmokeFeedback:
    def test_check_feedback_page(
            self,
            pageFeedback: Feedback,
            test_data: dict,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()
        # Check Feedback page

    def test_check_feedback_details_page(
            self,
            pageFeedback: Feedback,
            test_data: dict,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()
        # Check Feedback details page


@pytest.mark.skip(reason="ToDo")
@pytest.mark.usefixtures("login")
class TestFeedbackFilters:
    def feedback_search_filter(self):
        pass

    def feedback_programme_filter(self):
        pass

    def feedback_issue_type_filter(self):
        pass

    def feedback_created_by_filter(self):
        pass

    def feedback_creation_date_filter(self):
        pass

    def feedback_programme_state_filter(self):
        pass

    def feedback_clear_button(self):
        pass

@pytest.mark.skip(reason="ToDo")
@pytest.mark.usefixtures("login")
class TestFeedback:
    @pytest.mark.parametrize(
        "test_data",
        [
            pytest.param(
                {
                    "description": "New Feedback - " + str(random.random()),
                    "type": "Negative",
                },
                id="Negative",
            ),
        ],
        [
            pytest.param(
                {
                    "description": "New Feedback - " + str(random.random()),
                    "type": "Positive",
                },
                id="Positive",
            ),
        ],
    )
    def test_create_feedback_mandatory_fields(
            self,
            pageFeedback: Feedback,
            pageFeedbackDetails: FeedbackDetailsPage,
            pageNewFeedback: NewFeedback,
            test_data: dict,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()
        # Create Feedback

        # Check Details page

    def test_create_feedback_optional_fields(
            self,
            pageFeedback: Feedback,
            pageFeedbackDetails: FeedbackDetailsPage,
            pageNewFeedback: NewFeedback,
            test_data: dict,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()

    def test_create_feedback_with_household(
            self,
            pageFeedback: Feedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()

    def test_create_feedback_with_individual(
            self,
            pageFeedback: Feedback,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()

    def test_create_feedback_error_messages(
            self,
            pageFeedback: Feedback,
            pageFeedbackDetails: FeedbackDetailsPage,
            pageNewFeedback: NewFeedback,
            test_data: dict,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()

    def test_create_linked_ticket(
            self,
            pageFeedback: Feedback,
            pageFeedbackDetails: FeedbackDetailsPage,
            pageNewFeedback: NewFeedback,
            test_data: dict,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()

    def test_edit_feedback(
            self,
            pageFeedback: Feedback,
            pageFeedbackDetails: FeedbackDetailsPage,
            pageNewFeedback: NewFeedback,
            test_data: dict,
    ) -> None:
        # Go to Feedback
        pageFeedback.getNavFeedback().click()
