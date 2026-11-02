import logging
import os
from typing import Any

from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger
from kombu import Exchange, Queue

from hope.apps.core.celery_queues import CELERY_QUEUE_DEFAULT, CELERY_QUEUE_PERIODIC
from hope.apps.utils.logs import LogForgingFilter

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope.config.settings")

app = Celery("hct_mis")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf["task_queues"] = (
    Queue(
        CELERY_QUEUE_DEFAULT,
        Exchange(CELERY_QUEUE_DEFAULT),
        routing_key=CELERY_QUEUE_DEFAULT,
    ),
    Queue(
        CELERY_QUEUE_PERIODIC,
        Exchange(CELERY_QUEUE_PERIODIC),
        routing_key=CELERY_QUEUE_PERIODIC,
    ),
)
app.conf["worker_prefetch_multiplier"] = 1
app.conf["task_default_queue"] = CELERY_QUEUE_DEFAULT

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(related_name="celery_tasks")


@after_setup_logger.connect
@after_setup_task_logger.connect
def add_log_forging_filter(logger: logging.Logger, **kwargs: Any) -> None:
    # Celery workers replace the handlers from settings.LOGGING with their own, which lack LogForgingFilter.
    for handler in logger.handlers:
        handler.addFilter(LogForgingFilter())
