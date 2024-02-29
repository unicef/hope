import random

import pytest
from page_object.grievance.details_feedback_page import FeedbackDetailsPage
from page_object.grievance.feedback import Feedback
from page_object.grievance.new_feedback import NewFeedback

pytestmark = pytest.mark.django_db(transaction=True)


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
