import pytest

from extras.test_utils.factories import (
    CommunicationMessageFactory,
    FeedbackFactory,
    FeedbackMessageFactory,
    SurveyFactory,
)

pytestmark = pytest.mark.django_db


def test_accountability_factories():
    assert FeedbackFactory()
    assert FeedbackMessageFactory()
    assert CommunicationMessageFactory()
    assert SurveyFactory()
