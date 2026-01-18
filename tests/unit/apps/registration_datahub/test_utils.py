import json
from pathlib import Path

from django.conf import settings
from django.test import TestCase
import pytest

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.registration_datahub.utils import calculate_hash_for_kobo_submission
from hope.apps.registration_datahub.validators import UploadXLSXInstanceValidator


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

    def test_list_of_integer_validator_for_primary_collector_id(self) -> None:
        business_area = create_afghanistan()
        program = ProgramFactory(business_area=business_area, data_collecting_type__type="SOCIAL")
        assert UploadXLSXInstanceValidator(program=program).list_of_integer_validator("1", "pp_primary_collector_id")
        assert UploadXLSXInstanceValidator(program=program).list_of_integer_validator(
            "1;2;3", "pp_primary_collector_id"
        )
        assert UploadXLSXInstanceValidator(program=program).list_of_integer_validator(1, "pp_primary_collector_id")
        assert UploadXLSXInstanceValidator(program=program).list_of_integer_validator("", "pp_primary_collector_id")
        assert UploadXLSXInstanceValidator(program=program).list_of_integer_validator(None, "pp_primary_collector_id")

        with pytest.raises(ValueError, match="InvalidValue") as e:
            UploadXLSXInstanceValidator(program=program).list_of_integer_validator(
                "InvalidValue", "pp_primary_collector_id"
            )
        assert str(e.value) == "invalid literal for int() with base 10: 'InvalidValue'"
