import datetime

from django.test import TestCase
from django.utils import timezone

import pytz
from parameterized import parameterized

from hct_mis_api.apps.core.utils import timezone_datetime


class TestTimezoneDatetime(TestCase):
    @parameterized.expand(
        [
            ("2022-09-24",),
            (datetime.date(2022, 9, 24),),
            (timezone.datetime(2022, 9, 24, tzinfo=pytz.timezone("Europe/Warsaw")),),
        ]
    )
    def test_timezone_datetime(self, date):
        self.assertEqual(timezone_datetime(date), timezone.datetime(2022, 9, 24, tzinfo=pytz.utc))
