import traceback

from django.core.cache import cache
from django.db import transaction

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.universal_update_script.models import UniversalUpdate
from hct_mis_api.apps.universal_update_script.universal_individual_update_script.universal_individual_update_script import \
    UniversalIndividualUpdateEngine
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags
from celery.exceptions import SoftTimeLimitExceeded

SOFT_TIME_LIMIT = 30 * 60
HARD_TIME_LIMIT = 35 * 60

RESULT_LOCKED = "locked"
RESULT_SUCCESS = "success"
RESULT_FAILED = "failed"


@app.task(bind=True, acks_late=True, soft_time_limit=SOFT_TIME_LIMIT, time_limit=HARD_TIME_LIMIT)
@log_start_and_end
@sentry_tags
def run_universal_update(self, universal_update_id: str) -> str:
    universal_update = UniversalUpdate.objects.get(id=universal_update_id)
    lock_id = f"lock:run_universal_update:{universal_update_id}"
    lock = cache.lock(lock_id, timeout=HARD_TIME_LIMIT)
    if not lock.acquire(blocking=False):
        return RESULT_LOCKED
    try:
        universal_update.clear_logs()
        universal_update.save_logs("Update was started")
        engine = UniversalIndividualUpdateEngine(universal_update, ignore_empty_values=True, deduplicate_es=True,
                                                 deduplicate_documents=True)
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
