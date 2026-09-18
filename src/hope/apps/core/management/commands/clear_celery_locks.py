from typing import Any

from django.core.cache import cache
from django.core.management import BaseCommand

# One prefix per lock site in celery tasks, whatever the mechanism (cache.lock, cache.add, locked_cache, get/set guard).
# When you add a lock to a task, add its key prefix here.
LOCK_KEY_PREFIXES = (
    # cache.lock
    "export_payment_plan_group_delivery_xlsx_",
    "payment_plan_generate_token_and_order_numbers_",
    "payment_plan_rebuild_stats_",
    "payment_plan_full_rebuild_",
    "send_western_union_report_email_notifications_",
    "send_payment_plan_reconciliation_overdue_email_",
    "pdu_online_edit_merge",
    "lock:run_universal_individual_update_async_task:",
    "lock:generate_universal_individual_update_template_async_task:",
    # cache.add
    "dash_report_task_running_",
    # locked_cache, which is cache.get_or_set
    "registration_xlsx_import_async_task-",
    "registration_program_population_import_async_task-",
    "registration_kobo_import_async_task-",
    "merge_registration_data_import_async_task-",
    "classify_findings_and_schedule_merge_async_task-",
    "process_generic_import_async_task-",
    "automate_rdi_creation_async_task-",
    "deduplicate_documents",
    # cache.get / cache.set guards with hashed params
    "prepare_payment_plan_async_task_",
    "enroll_households_to_program_async_task_",
)


class Command(BaseCommand):
    help = "Remove every celery task lock from the cache. Run only while no celery worker is running (deploy)."

    def handle(self, *args: Any, **options: Any) -> None:
        removed = sum(cache.delete_pattern(f"{prefix}*") for prefix in LOCK_KEY_PREFIXES)
        self.stdout.write(f"Removed {removed} celery task locks")
