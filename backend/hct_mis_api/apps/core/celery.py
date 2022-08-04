import os

from celery import Celery
from kombu import Exchange, Queue

CELERY_QUEUE_DEFAULT = "default"
CELERY_QUEUE_OTHER = "priority"

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hct_mis_api.settings")

app = Celery("hct_mis")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf["task_queues"] = (
    Queue(
        CELERY_QUEUE_DEFAULT,
        Exchange(CELERY_QUEUE_DEFAULT),
        routing_key=CELERY_QUEUE_DEFAULT,
    ),
    Queue(
        CELERY_QUEUE_OTHER,
        Exchange(CELERY_QUEUE_OTHER),
        routing_key=CELERY_QUEUE_OTHER,
    ),
)
app.conf["worker_prefetch_multiplier"] = 1
app.conf["task_default_queue"] = CELERY_QUEUE_DEFAULT

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(related_name="celery_tasks")
