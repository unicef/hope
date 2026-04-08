from datetime import timedelta
from unittest.mock import MagicMock

from django.utils import timezone

from hope.models.survey import Survey


def test_has_valid_sample_file_returns_true_when_not_expired():
    mock = MagicMock(spec=Survey)
    mock.sample_file = True
    mock.sample_file_generated_at = timezone.now() - timedelta(days=1)
    mock.SAMPLE_FILE_EXPIRATION_IN_DAYS = Survey.SAMPLE_FILE_EXPIRATION_IN_DAYS

    result = Survey.has_valid_sample_file(mock)

    assert result is True


def test_has_valid_sample_file_returns_false_when_expired():
    mock = MagicMock(spec=Survey)
    mock.sample_file = True
    mock.sample_file_generated_at = timezone.now() - timedelta(days=31)
    mock.SAMPLE_FILE_EXPIRATION_IN_DAYS = Survey.SAMPLE_FILE_EXPIRATION_IN_DAYS

    result = Survey.has_valid_sample_file(mock)

    assert result is False
