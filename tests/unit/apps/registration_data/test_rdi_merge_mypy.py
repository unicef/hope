from unittest.mock import MagicMock

import pytest

from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask

pytestmark = pytest.mark.django_db


@pytest.fixture
def rdi_merge_task():
    return RdiMergeTask()


@pytest.fixture
def mock_individuals():
    return MagicMock()


def test_run_deduplication_raises_when_business_area_is_none(rdi_merge_task, mock_individuals):
    rdi = MagicMock()
    rdi.business_area = None
    rdi.program = MagicMock()

    with pytest.raises(ValueError, match="RDI business_area must not be None"):
        rdi_merge_task._run_deduplication(rdi, mock_individuals, "test-rdi-id")


def test_run_deduplication_raises_when_program_is_none(rdi_merge_task, mock_individuals):
    rdi = MagicMock()
    rdi.business_area = MagicMock()
    rdi.program = None

    with pytest.raises(ValueError, match="RDI program must not be None"):
        rdi_merge_task._run_deduplication(rdi, mock_individuals, "test-rdi-id")


def test_run_biometric_deduplication_skips_when_program_is_none(rdi_merge_task):
    rdi = MagicMock()
    rdi.program = None

    # Should not raise and should not call any deduplication service
    rdi_merge_task._run_biometric_deduplication(rdi, [])

    rdi.assert_not_called()


def test_run_biometric_deduplication_skips_when_biometric_deduplication_disabled(rdi_merge_task):
    rdi = MagicMock()
    rdi.program = MagicMock()
    rdi.program.biometric_deduplication_enabled = False

    # Should not raise - guard condition prevents execution
    rdi_merge_task._run_biometric_deduplication(rdi, [])
