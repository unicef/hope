# pragma: no cover
import traceback

from django.core.cache import cache
from django.core.files.base import ContentFile

from celery.exceptions import SoftTimeLimitExceeded

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.universal_update_script.models import UniversalUpdate
from hct_mis_api.apps.universal_update_script.universal_individual_update_service.create_backup_snapshot import (
    create_and_save_snapshot_chunked,
)
from hct_mis_api.apps.universal_update_script.universal_individual_update_service.universal_individual_update_service import (
    UniversalIndividualUpdateService,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

SOFT_TIME_LIMIT = 30 * 60
HARD_TIME_LIMIT = 35 * 60

RESULT_LOCKED = "locked"
RESULT_SUCCESS = "success"
RESULT_FAILED = "failed"


@app.task(acks_late=True, soft_time_limit=SOFT_TIME_LIMIT, time_limit=HARD_TIME_LIMIT)
@log_start_and_end
@sentry_tags
def run_universal_individual_update(universal_update_id: str) -> str:
    universal_update = UniversalUpdate.objects.get(id=universal_update_id)
    lock_id = f"lock:run_universal_individual_update:{universal_update_id}"
    lock = cache.lock(lock_id, timeout=HARD_TIME_LIMIT)
    if not lock.acquire(blocking=False):
        return RESULT_LOCKED
    try:
        universal_update.clear_logs()
        universal_update.save_logs("Creating backup snapshot was started")
        create_and_save_snapshot_chunked(universal_update)
        universal_update.save_logs("Update was started")
        engine = UniversalIndividualUpdateService(
            universal_update, ignore_empty_values=True, deduplicate_es=True, deduplicate_documents=True
        )
        engine.execute()
        return RESULT_SUCCESS
    except SoftTimeLimitExceeded:
        universal_update.save_logs("Task time limit exceeded")
        return RESULT_FAILED
    except Exception as e:
        error_message = f"Unexpected error occurred in run_universal_update for UniversalUpdate {universal_update_id}\n{traceback.format_exc()}"
        universal_update.save_logs(error_message)
        raise e
    finally:
        lock.release()


@app.task(acks_late=True, soft_time_limit=SOFT_TIME_LIMIT, time_limit=HARD_TIME_LIMIT)
@log_start_and_end
@sentry_tags
def generate_universal_individual_update_template(universal_update_id: str) -> str:
    universal_update = UniversalUpdate.objects.get(id=universal_update_id)
    lock_id = f"lock:generate_universal_individual_update_template:{universal_update_id}"
    lock = cache.lock(lock_id, timeout=HARD_TIME_LIMIT)
    if not lock.acquire(blocking=False):
        return RESULT_LOCKED
    try:
        universal_update.clear_logs()
        universal_update.save_logs("Update was started")
        engine = UniversalIndividualUpdateService(universal_update)
        template_file = engine.generate_xlsx_template()
        content = template_file.getvalue()
        universal_update.template_file.save("template.xlsx", ContentFile(content))
        universal_update.save()
        universal_update.save_logs("Finished Generating Template")
        return RESULT_SUCCESS
    except SoftTimeLimitExceeded:
        universal_update.save_logs("Task time limit exceeded")
        return RESULT_FAILED
    except Exception as e:
        error_message = f"Unexpected error occurred in run_universal_update for UniversalUpdate {universal_update_id}\n{traceback.format_exc()}"
        universal_update.save_logs(error_message)
        raise e
    finally:
        lock.release()
