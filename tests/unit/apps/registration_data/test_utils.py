import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from extras.test_utils.factories.core import BeneficiaryGroupFactory, BusinessAreaFactory, DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.registration_data.utils import (
    calculate_hash_for_kobo_submission,
    collectors_str_ids_to_list,
    post_process_dedupe_results,
)
from hope.apps.registration_data.validators import UploadXLSXInstanceValidator
from hope.models import DataCollectingType

FILES_DIR = Path(__file__).resolve().parent / "test_file"


@pytest.fixture
def kobo_test_data() -> dict[str, Any]:
    with (
        open(FILES_DIR / "test_calculate_hash_for_kobo_submission1.json") as f1,
        open(FILES_DIR / "test_calculate_hash_for_kobo_submission2.json") as f2,
        open(FILES_DIR / "test_calculate_hash_for_kobo_submission3.json") as f3,
    ):
        return {
            "data1": json.load(f1),
            "data2": json.load(f2),
            "data3": json.load(f3),
        }


@pytest.fixture
def social_program() -> Any:
    business_area = BusinessAreaFactory()
    data_collecting_type = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL)
    beneficiary_group = BeneficiaryGroupFactory(master_detail=False)
    return ProgramFactory(
        business_area=business_area,
        data_collecting_type=data_collecting_type,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def record_with_batch_and_golden_record_duplicates() -> SimpleNamespace:
    return SimpleNamespace(
        deduplication_batch_results={"duplicates": [{"score": 2.0}, {"score": 9.0}]},
        deduplication_golden_record_results={"duplicates": [{"score": 5.0}]},
    )


def test_calculate_hash_for_kobo_submission(kobo_test_data: dict[str, Any]) -> None:
    hash1 = calculate_hash_for_kobo_submission(kobo_test_data["data1"])
    hash2 = calculate_hash_for_kobo_submission(kobo_test_data["data2"])
    hash3 = calculate_hash_for_kobo_submission(kobo_test_data["data3"])

    assert hash1 == hash2
    assert hash1 != hash3


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", True),
        ("1;2;3", True),
        (1, True),
        ("", True),
        (None, True),
        (True, False),
        ("InvalidValue", False),
    ],
)
def test_list_of_integer_validator_for_primary_collector_id(
    social_program: Any,
    value: Any,
    expected: bool,
) -> None:
    validator = UploadXLSXInstanceValidator(program=social_program)
    assert validator.list_of_integer_validator(value, "pp_primary_collector_id") is expected


def test_list_of_integer_validator_for_required_primary_collector_id(
    social_program: Any,
) -> None:
    validator = UploadXLSXInstanceValidator(program=social_program)
    assert validator.list_of_integer_validator(None, "pp_index_id") is False


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1.0, ["1"]),
        (1.5, ["1.5"]),
        (2, ["2"]),
        ("3;4", ["3", "4"]),
        (None, None),
    ],
)
def test_collectors_str_ids_to_list(value: Any, expected: Any) -> None:
    assert collectors_str_ids_to_list(value) == expected


def test_post_process_dedupe_results_scores_each_field_separately(
    record_with_batch_and_golden_record_duplicates: SimpleNamespace,
) -> None:
    post_process_dedupe_results(record_with_batch_and_golden_record_duplicates)

    assert record_with_batch_and_golden_record_duplicates.deduplication_batch_results["score"] == {
        "max": 9.0,
        "min": 2.0,
        "qty": 2,
    }
    assert record_with_batch_and_golden_record_duplicates.deduplication_golden_record_results["score"] == {
        "max": 5.0,
        "min": 5.0,
        "qty": 1,
    }
