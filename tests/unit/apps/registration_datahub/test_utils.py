import json
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from hope.apps.registration_datahub.utils import (
    calculate_hash_for_kobo_submission,
)


class TestRdiUtils(TestCase):
    def test_calculate_hash_for_kobo_submission(self) -> None:
        test_file_dir = Path(settings.TESTS_ROOT) / "apps/registration_datahub/test_file"

        with (
            open(test_file_dir / "test_calculate_hash_for_kobo_submission1.json") as f1,
            open(test_file_dir / "test_calculate_hash_for_kobo_submission2.json") as f2,
            open(test_file_dir / "test_calculate_hash_for_kobo_submission3.json") as f3,
        ):
            test_data1 = json.load(f1)
            test_data2 = json.load(f2)
            test_data3 = json.load(f3)

        hash1 = calculate_hash_for_kobo_submission(test_data1)
        hash2 = calculate_hash_for_kobo_submission(test_data2)
        hash3 = calculate_hash_for_kobo_submission(test_data3)

        assert hash1 == hash2
        assert hash1 != hash3
