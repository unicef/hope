import pytest

from extras.test_utils.factories import BusinessAreaFactory, FeedbackFactory

pytestmark = pytest.mark.django_db


def test_feedback_str_returns_description_and_business_area() -> None:
    feedback = FeedbackFactory(
        description="Sample feedback",
        business_area=BusinessAreaFactory(name="AFG"),
    )

    assert str(feedback) == "Sample feedback (AFG)"
