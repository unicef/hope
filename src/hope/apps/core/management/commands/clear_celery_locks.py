from typing import Any

from django.core.cache import cache
from django.core.management import BaseCommand

from hope.apps.dashboard.celery_tasks import DASH_REPORT_LOCK_PREFIX
from hope.apps.generic_import.celery_tasks import PROCESS_GENERIC_IMPORT_LOCK_PREFIX
from hope.apps.household.celery_tasks import ENROLL_HOUSEHOLDS_TO_PROGRAM_LOCK_PREFIX
from hope.apps.payment.celery_tasks import (
    EXPORT_PAYMENT_PLAN_GROUP_DELIVERY_XLSX_LOCK_PREFIX,
    PAYMENT_PLAN_FULL_REBUILD_LOCK_PREFIX,
    PAYMENT_PLAN_ORDER_NUMBERS_LOCK_PREFIX,
    PAYMENT_PLAN_REBUILD_STATS_LOCK_PREFIX,
    SEND_PAYMENT_PLAN_RECONCILIATION_OVERDUE_EMAIL_LOCK_PREFIX,
    SEND_WESTERN_UNION_REPORT_EMAIL_LOCK_PREFIX,
)
from hope.apps.payment.utils import PREPARE_PAYMENT_PLAN_LOCK_PREFIX
from hope.apps.periodic_data_update.celery_tasks import PDU_ONLINE_EDIT_MERGE_LOCK_KEY
from hope.apps.registration_data.celery_tasks import (
    DEDUPLICATE_DOCUMENTS_LOCK_KEY,
    FETCH_FINDINGS_AND_MERGE_RDI_LOCK_PREFIX,
    RDI_KOBO_IMPORT_LOCK_PREFIX,
    RDI_MERGE_LOCK_PREFIX,
    RDI_PROGRAM_POPULATION_IMPORT_LOCK_PREFIX,
    RDI_XLSX_IMPORT_LOCK_PREFIX,
)
from hope.apps.universal_update_script.celery_tasks import (
    GENERATE_UNIVERSAL_UPDATE_TEMPLATE_LOCK_PREFIX,
    RUN_UNIVERSAL_UPDATE_LOCK_PREFIX,
)
from hope.contrib.aurora.celery_tasks import AUTOMATE_RDI_CREATION_LOCK_PREFIX

# One entry per lock site in celery tasks, whatever the mechanism (cache.lock, cache.add, locked_cache, get/set guard).
# The constants live next to the code that takes the lock; add the new one here when you add a lock to a task.
LOCK_KEY_PREFIXES = (
    EXPORT_PAYMENT_PLAN_GROUP_DELIVERY_XLSX_LOCK_PREFIX,
    PAYMENT_PLAN_ORDER_NUMBERS_LOCK_PREFIX,
    PAYMENT_PLAN_REBUILD_STATS_LOCK_PREFIX,
    PAYMENT_PLAN_FULL_REBUILD_LOCK_PREFIX,
    SEND_WESTERN_UNION_REPORT_EMAIL_LOCK_PREFIX,
    SEND_PAYMENT_PLAN_RECONCILIATION_OVERDUE_EMAIL_LOCK_PREFIX,
    PREPARE_PAYMENT_PLAN_LOCK_PREFIX,
    ENROLL_HOUSEHOLDS_TO_PROGRAM_LOCK_PREFIX,
    PDU_ONLINE_EDIT_MERGE_LOCK_KEY,
    RUN_UNIVERSAL_UPDATE_LOCK_PREFIX,
    GENERATE_UNIVERSAL_UPDATE_TEMPLATE_LOCK_PREFIX,
    DASH_REPORT_LOCK_PREFIX,
    RDI_XLSX_IMPORT_LOCK_PREFIX,
    RDI_PROGRAM_POPULATION_IMPORT_LOCK_PREFIX,
    RDI_KOBO_IMPORT_LOCK_PREFIX,
    RDI_MERGE_LOCK_PREFIX,
    FETCH_FINDINGS_AND_MERGE_RDI_LOCK_PREFIX,
    PROCESS_GENERIC_IMPORT_LOCK_PREFIX,
    AUTOMATE_RDI_CREATION_LOCK_PREFIX,
    DEDUPLICATE_DOCUMENTS_LOCK_KEY,
)


class Command(BaseCommand):
    help = "Remove every celery task lock from the cache. Run only while no celery worker is running (deploy)."

    def handle(self, *args: Any, **options: Any) -> None:
        removed = sum(cache.delete_pattern(f"{prefix}*") for prefix in LOCK_KEY_PREFIXES)
        self.stdout.write(f"Removed {removed} celery task locks")
