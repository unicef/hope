from django.test import TestCase

from freezegun import freeze_time
from parameterized import parameterized

from hct_mis_api.apps.power_query.utils import should_run


class TestRunToday(TestCase):
    databases = {"default"}

    @parameterized.expand(
        [
            ("Sat", True),
            ("sat", True),
            ("Mon", False),
            ("3", True),
            ("31", False),
            ("3/1", True),
            ("03/01", True),
            ("1/3", False),
            ("1/3,sat", True),
            ("1/3,Mon", False),
            ("1/3,Mon,3/1", True),
            ("mon,tue", False),
            ("mon,sat", True),
            ("3/1,4/1", True),
        ]
    )
    @freeze_time("1987-01-03")
    def test_query_execution(self, pattern: str, value: bool) -> None:
        self.assertEqual(should_run(pattern), value)
