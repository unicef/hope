import datetime
import logging

from django.db.models import Q
from django.utils import timezone

from hope.apps.account.signals import _invalidate_user_permissions_cache
from hope.apps.core.celery import app
from hope.models import AsyncRetryJob, PeriodicAsyncRetryJob

logger = logging.getLogger(__name__)


def invalidate_permissions_cache_for_user_if_expired_role_async_task_action(job: AsyncRetryJob | None = None) -> bool:
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


@app.task()
def invalidate_permissions_cache_for_user_if_expired_role_async_task() -> bool:
    PeriodicAsyncRetryJob.queue_task(
        job_name=invalidate_permissions_cache_for_user_if_expired_role_async_task.__name__,
        action="hope.apps.account.celery_tasks.invalidate_permissions_cache_for_user_if_expired_role_async_task_action",
        config={},
        group_key="invalidate_permissions_cache_for_user_if_expired_role_async_task",
        description="Invalidate permissions cache for users with expired roles",
    )
    return True
