import datetime
import logging
from typing import Any

from django.db.models import Q
from django.utils import timezone
from django_celery_boost.models import AsyncJobModel

from hope.apps.account.signals import _invalidate_user_permissions_cache
from hope.apps.core.celery import app
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags
from hope.models import AsyncRetryJob

logger = logging.getLogger(__name__)


def invalidate_permissions_cache_for_user_if_expired_role_action(job: AsyncRetryJob) -> bool:
    # Invalidate permissions cache for users with roles that expired a day before
    from hope.models import User

    try:
        day_ago = timezone.now() - datetime.timedelta(days=1)
        users = User.objects.filter(
            Q(role_assignments__expiry_date=day_ago.date()) | Q(partner__role_assignments__expiry_date=day_ago.date())
        ).distinct()
        _invalidate_user_permissions_cache(users)
        return True
    except Exception:
        logger.exception("Failed to invalidate permissions cache for users with expired roles")
        raise


@app.task(bind=True)
@log_start_and_end
@sentry_tags
def invalidate_permissions_cache_for_user_if_expired_role(self: Any) -> bool:
    job = AsyncRetryJob.objects.create(
        job_name=invalidate_permissions_cache_for_user_if_expired_role.__name__,
        type=AsyncJobModel.JobType.JOB_TASK,
        repeatable=True,
        action="hope.apps.account.celery_tasks.invalidate_permissions_cache_for_user_if_expired_role_action",
        config={},
        group_key="invalidate_permissions_cache_for_user_if_expired_role",
        description="Invalidate permissions cache for users with expired roles",
    )
    job.queue()
    return True
