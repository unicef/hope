from collections.abc import Callable
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
import pytest

from extras.test_utils.factories import LogEntryFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BusinessArea, LogEntry, Program, User

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
TIMESTAMP_CELL = '[data-cy="timestamp-cell"]'
USER_CELL = '[data-cy="user-cell"]'
CONTENT_TYPE_CELL = '[data-cy="content-type-cell"]'
OBJECT_REPRESENTATION_CELL = '[data-cy="object-representation-cell"]'
ACTION_CELL = '[data-cy="action-cell"]'
CHANGE_KEY_CELL = '[data-cy="change-key-cell"]'
FROM_VALUE_CELL = '[data-cy="from-value-cell"]'
TO_VALUE_CELL = '[data-cy="to-value-cell"]'
TABLE_PAGINATION = '[data-cy="table-pagination"]'


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.FINISHED)


@pytest.fixture
def log_entry(program: Program, create_super_user: User) -> LogEntry:
    return LogEntryFactory(
        action=LogEntry.UPDATE,
        business_area=program.business_area,
        programs=[program],
        user=create_super_user,
        content_type=ContentType.objects.get_for_model(Program),
        object_id=program.id,
        object_repr=str(program),
        changes={"status": {"from": Program.ACTIVE, "to": Program.FINISHED}},
    )


def programme_log_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/activity-log"


def all_programmes_log_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/all/activity-log"


@pytest.mark.parametrize(
    "build_url",
    [
        pytest.param(programme_log_url, id="programme-log"),
        pytest.param(all_programmes_log_url, id="activity-log"),
    ],
)
def test_activity_log_lists_entry(
    log_entry: LogEntry,
    program: Program,
    login: HopeTestBrowser,
    build_url: Callable[[Program], str],
) -> None:
    login.open(build_url(program))

    login.assert_text("Activity Log", PAGE_HEADER_TITLE)
    login.assert_text("Update", ACTION_CELL)
    # Date only — asserting the hour flakes when the test crosses an hour boundary
    login.assert_text(datetime.today().strftime("%-d %b %Y"), TIMESTAMP_CELL)
    login.assert_text(f"{log_entry.user.first_name} {log_entry.user.last_name}", USER_CELL)
    login.assert_text("Programme", CONTENT_TYPE_CELL)
    login.assert_text(str(program.id), OBJECT_REPRESENTATION_CELL)
    login.assert_text("status", CHANGE_KEY_CELL)
    login.assert_text("ACTIVE", FROM_VALUE_CELL)
    login.assert_text("FINISHED", TO_VALUE_CELL)
    login.assert_text("1–1 of 1", TABLE_PAGINATION)
