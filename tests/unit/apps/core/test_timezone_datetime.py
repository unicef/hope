import datetime

from django.utils import timezone
import pytest
import pytz

from hope.apps.core.utils import timezone_datetime


@pytest.mark.parametrize(
    "date_input",
    [
        "2022-09-24",
        datetime.date(2022, 9, 24),
        timezone.datetime(2022, 9, 24, tzinfo=pytz.timezone("Europe/Warsaw")),
    ],
)
def test_timezone_datetime_converts_various_formats_to_utc(date_input):
    assert timezone_datetime(date_input) == timezone.datetime(2022, 9, 24, tzinfo=pytz.utc)
