from django.test import TestCase

from hct_mis_api.apps.core.utils import get_count_and_percentage


class TestCoreUtils(TestCase):

    def test_get_count_and_percentage(self) -> None:
        self.assertEqual(get_count_and_percentage(1), {"count": 1, "percentage": 100.0})
        self.assertEqual(get_count_and_percentage(0), {"count": 0, "percentage": 0.0})
        self.assertEqual(get_count_and_percentage(5, 1), {"count": 5, "percentage": 500.0})
        self.assertEqual(get_count_and_percentage(20, 20), {"count": 20, "percentage": 100.0})
        self.assertEqual(get_count_and_percentage(5, 25), {"count": 5, "percentage": 20.0})
