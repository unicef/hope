import json

from django.conf import settings
from django.test import TestCase

from hct_mis_api.apps.registration_datahub.utils import (
    calculate_hash_for_kobo_submission,
)


class TestRdiUtils(TestCase):
    def test_calculate_hash_for_kobo_submission(self) -> None:
        with open(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/test_calculate_hash_for_kobo_submission1.json"
        ) as test_file1:
            test_data1 = json.load(test_file1)
            hash1 = calculate_hash_for_kobo_submission(test_data1)

        with open(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/test_calculate_hash_for_kobo_submission2.json"
        ) as test_file2:
            test_data2 = json.load(test_file2)
            hash2 = calculate_hash_for_kobo_submission(test_data2)

        with open(
            f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/test_calculate_hash_for_kobo_submission3.json"
        ) as test_file3:
            test_data3 = json.load(test_file3)
            hash3 = calculate_hash_for_kobo_submission(test_data3)
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
