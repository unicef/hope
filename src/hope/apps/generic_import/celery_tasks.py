import traceback

from celery.exceptions import SoftTimeLimitExceeded
from django.core.cache import cache
from django.core.files.base import ContentFile

from hope.apps.core.celery import app
from hope.apps.universal_update_script.models import UniversalUpdate
from hope.apps.universal_update_script.universal_individual_update_service.create_backup_snapshot import (
    create_and_save_snapshot_chunked,
)
from hope.apps.universal_update_script.universal_individual_update_service.universal_individual_update_service import (
    UniversalIndividualUpdateService,
)
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags

SOFT_TIME_LIMIT = 30 * 60
HARD_TIME_LIMIT = 35 * 60

RESULT_LOCKED = "locked"
RESULT_SUCCESS = "success"
RESULT_FAILED = "failed"


@
