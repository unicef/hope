import json

from django.conf import settings
from django.test import TestCase

from hct_mis_api.apps.registration_datahub.utils import (
    calculate_hash_for_kobo_submission,
)


class TestRdiUtils(TestCase):
    def test_calculate_hash_for_kobo_submission(self) -> None:
        test_data1 = json.load(
            open(
                f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/test_calculate_hash_for_kobo_submission1.json"
            )
        )
        test_data2 = json.load(
            open(
                f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/test_calculate_hash_for_kobo_submission2.json"
            )
        )
        test_data3 = json.load(
            open(
                f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/test_calculate_hash_for_kobo_submission3.json"
            )
        )
        hash1 = calculate_hash_for_kobo_submission(test_data1)
        hash2 = calculate_hash_for_kobo_submission(test_data2)
        hash3 = calculate_hash_for_kobo_submission(test_data3)
        assert hash1 == hash2
        assert hash1 != hash3
