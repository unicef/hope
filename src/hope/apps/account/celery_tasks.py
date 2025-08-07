import datetime
import logging
from typing import Any

from django.db.models import Q
from django.utils import timezone

from hope.apps.account.models import User
from hope.apps.account.signals import _invalidate_user_permissions_cache
from hope.apps.core.celery import app
from hope.apps.utils.logs import log_start_and_end
from hope.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def invalidate_permissions_cache_for_user_if_expired_role(self: Any) -> bool:
    # Invalidate permissions cache for users with roles that expired a day before
    day_ago = timezone.now() - datetime.timedelta(days=1)
    users = User.objects.filter(
        Q(role_assignments__expiry_date=day_ago.date()) | Q(partner__role_assignments__expiry_date=day_ago.date())
    ).distinct()
    _invalidate_user_permissions_cache(users)
    return True
