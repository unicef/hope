"""Fill in Active Directory job titles on approval records that existed before the snapshot columns.

The payment migration that defines ``copy_actor_from_user_record`` copied name + job title from the user
rows and marked them USER_RECORD. This replaces the title with the one AD holds today, for the same rows
only: source still USER_RECORD and dated before that migration ran. Rows written after the deploy keep
whatever the approval itself recorded, including a USER_RECORD fallback from an AD outage at that moment.

Idempotent. Users AD holds no title for, users AD does not know, and users whose lookup fails keep their
rows unchanged and are listed by email; the last line is the summary with the counts. Re-run after fixing
the cause and only the remaining rows are touched. Needs AZURE_CLIENT_ID / AZURE_CLIENT_SECRET.

Run from a Django shell::

    from hope.one_time_scripts.backfill_ad_job_titles import backfill_ad_job_titles

    backfill_ad_job_titles()
"""

from datetime import datetime
from importlib import import_module
import pkgutil

from django.db.migrations.recorder import MigrationRecorder
from django.db.models import QuerySet
from django.http import Http404

from hope.apps.account.actor_snapshot import JobTitleSource, fetch_ad_job_title
from hope.apps.account.microsoft_graph import MicrosoftGraphAPI
from hope.apps.payment import migrations as payment_migrations
from hope.models import Approval, ApprovalProcess, User

PREFILL_FUNCTION = "copy_actor_from_user_record"
TARGETS: tuple[tuple[type[Approval] | type[ApprovalProcess], str, str], ...] = (
    (Approval, "created_by", "created_at"),
    (ApprovalProcess, "sent_for_approval_by", "sent_for_approval_date"),
    (ApprovalProcess, "sent_for_authorization_by", "sent_for_authorization_date"),
    (ApprovalProcess, "sent_for_finance_release_by", "sent_for_finance_release_date"),
)


def _pending_rows(
    model: type[Approval] | type[ApprovalProcess], field: str, date_field: str, cutoff: datetime
) -> QuerySet:
    return model.objects.filter(
        **{f"{field}_job_title_source": JobTitleSource.USER_RECORD, f"{date_field}__lte": cutoff}
    )


def backfill_ad_job_titles() -> None:
    # Found by its function, not by its number: the number changes whenever the migrations are renumbered.
    prefill_migration = next(
        name
        for _, name, _ in pkgutil.iter_modules(payment_migrations.__path__)
        if hasattr(import_module(f"{payment_migrations.__name__}.{name}"), PREFILL_FUNCTION)
    )
    cutoff = MigrationRecorder.Migration.objects.get(app="payment", name=prefill_migration).applied
    print(f"prefill migration: payment/{prefill_migration}, applied {cutoff}\n")

    user_ids: set = set()
    for model, field, date_field in TARGETS:
        user_ids |= set(_pending_rows(model, field, date_field, cutoff).values_list(f"{field}_id", flat=True))

    ms_graph = MicrosoftGraphAPI()
    updated_users = []
    no_title = []
    not_found = []
    failed = []
    for user in User.objects.filter(pk__in=user_ids).order_by("email"):
        try:
            job_title = fetch_ad_job_title(ms_graph, user)
        except Http404:
            not_found.append(user.email)
            continue
        except Exception as error:  # noqa: BLE001 - one user must not stop the run
            failed.append(f"{user.email}: {error}")
            continue
        if not job_title:
            no_title.append(user.email)
            continue
        rows = 0
        for model, field, date_field in TARGETS:
            rows += (
                _pending_rows(model, field, date_field, cutoff)
                .filter(**{field: user})
                .update(**{f"{field}_job_title": job_title, f"{field}_job_title_source": JobTitleSource.AD})
            )
        updated_users.append(f"{user.email}: {job_title!r} on {rows} rows")

    print("users with AD title applied:")
    print("\n".join(updated_users))
    print("\nusers with no title in AD (left as USER_RECORD):")
    print("\n".join(no_title))
    print("\nusers not found in AD (left as USER_RECORD):")
    print("\n".join(not_found))
    print("\nusers whose lookup failed (left as USER_RECORD, re-run):")
    print("\n".join(failed))
    print("\n-----------------------------------------------")
    total = len(updated_users) + len(no_title) + len(not_found) + len(failed)
    print(
        f"\nusers: {total}, AD title applied: {len(updated_users)}, no title in AD: {len(no_title)}, "
        f"not found in AD: {len(not_found)}, failed: {len(failed)}"
    )
