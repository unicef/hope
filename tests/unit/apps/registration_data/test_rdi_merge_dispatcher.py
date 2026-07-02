import datetime
from unittest.mock import Mock, patch
import uuid

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.registration_data.tasks.rdi_merge_dispatcher import RdiMergeDispatcher
from hope.models import Program, RegistrationDataImport

pytestmark = pytest.mark.django_db

DISPATCH_TARGET = "hope.apps.registration_data.celery_tasks.fetch_findings_and_merge_rdi"


@pytest.fixture
def program() -> Program:
    business_area = BusinessAreaFactory(slug="syria", name="Syria")
    return ProgramFactory(business_area=business_area, biometric_deduplication_enabled=True)


def _rdi(program: Program, status: str, arrived_hours_ago: int) -> RegistrationDataImport:
    rdi = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        status=status,
        country_workspace_id=str(uuid.uuid4()),
    )
    # import_date is auto_now_add, so it can only be set after creation. It is the queue's
    # ordering key — smaller (earlier) == older == processed first.
    RegistrationDataImport.objects.filter(pk=rdi.pk).update(
        import_date=timezone.now() - datetime.timedelta(hours=arrived_hours_ago)
    )
    return rdi


@patch(DISPATCH_TARGET)
def test_dispatcher_noop_when_queue_empty(mock_fetch: Mock, program: Program) -> None:
    RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        status=RegistrationDataImport.MERGED,
        country_workspace_id=str(uuid.uuid4()),
    )

    RdiMergeDispatcher().execute(str(program.id))

    mock_fetch.assert_not_called()


@patch(DISPATCH_TARGET)
def test_dispatcher_enqueues_oldest_merge_scheduled(mock_fetch: Mock, program: Program) -> None:
    oldest = _rdi(program, RegistrationDataImport.MERGE_SCHEDULED, arrived_hours_ago=3)
    _rdi(program, RegistrationDataImport.MERGE_SCHEDULED, arrived_hours_ago=1)

    RdiMergeDispatcher().execute(str(program.id))

    mock_fetch.assert_called_once()
    assert mock_fetch.call_args.args[0].pk == oldest.pk


@patch(DISPATCH_TARGET)
def test_dispatcher_skips_merged_and_takes_next_scheduled(mock_fetch: Mock, program: Program) -> None:
    _rdi(program, RegistrationDataImport.MERGED, arrived_hours_ago=5)
    scheduled = _rdi(program, RegistrationDataImport.MERGE_SCHEDULED, arrived_hours_ago=2)

    RdiMergeDispatcher().execute(str(program.id))

    mock_fetch.assert_called_once()
    assert mock_fetch.call_args.args[0].pk == scheduled.pk


@patch(DISPATCH_TARGET)
def test_dispatcher_paused_when_head_in_merge_error(mock_fetch: Mock, program: Program) -> None:
    _rdi(program, RegistrationDataImport.MERGE_ERROR, arrived_hours_ago=3)
    _rdi(program, RegistrationDataImport.MERGE_SCHEDULED, arrived_hours_ago=1)

    RdiMergeDispatcher().execute(str(program.id))

    mock_fetch.assert_not_called()


@patch(DISPATCH_TARGET)
def test_dispatcher_paused_when_head_in_import_error(mock_fetch: Mock, program: Program) -> None:
    # IMPORT_ERROR blocks the queue defensively (decision: an invalid CW state must not let
    # newer RDIs merge ahead of it).
    _rdi(program, RegistrationDataImport.IMPORT_ERROR, arrived_hours_ago=3)
    _rdi(program, RegistrationDataImport.MERGE_SCHEDULED, arrived_hours_ago=1)

    RdiMergeDispatcher().execute(str(program.id))

    mock_fetch.assert_not_called()


@patch(DISPATCH_TARGET)
def test_dispatcher_waits_when_head_already_merging(mock_fetch: Mock, program: Program) -> None:
    _rdi(program, RegistrationDataImport.MERGING, arrived_hours_ago=3)
    _rdi(program, RegistrationDataImport.MERGE_SCHEDULED, arrived_hours_ago=1)

    RdiMergeDispatcher().execute(str(program.id))

    mock_fetch.assert_not_called()


@patch(DISPATCH_TARGET)
def test_dispatcher_is_scoped_to_its_program(mock_fetch: Mock, program: Program) -> None:
    other_program = ProgramFactory(business_area=program.business_area, biometric_deduplication_enabled=True)
    _rdi(other_program, RegistrationDataImport.MERGE_SCHEDULED, arrived_hours_ago=10)
    own = _rdi(program, RegistrationDataImport.MERGE_SCHEDULED, arrived_hours_ago=1)

    RdiMergeDispatcher().execute(str(program.id))

    mock_fetch.assert_called_once()
    assert mock_fetch.call_args.args[0].pk == own.pk
