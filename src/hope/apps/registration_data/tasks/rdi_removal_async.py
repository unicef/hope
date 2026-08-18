import logging

from django.db import transaction
from django.db.models.deletion import ProtectedError

from hope.apps.core.celery_tasks import NonRetriableTaskError
from hope.apps.registration_data.services.rdi_removal import remove_rdi_population
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import RegistrationDataImport

logger = logging.getLogger(__name__)


class RdiPopulationRemoval:
    """Retriable hard-delete of a CW-managed RDI's population (REWORK #3).

    Two locked txns:
      A — lock, fail fast if MERGED, commit the DELETING marker in its OWN txn so a
          worker crash mid-wipe leaves the row visibly DELETING in the admin.
      B — re-lock, defensively re-check MERGED, hard-delete the population.

    Outcomes:
      - success / already-gone row  → enqueue the CW success callback (success-only).
      - MERGED (terminal success)   → leave status intact, no retry.
      - ProtectedError (dependents) → DELETE_FAILED, no retry.
      - any other error             → propagates; async_retry_job_task retries and, once
                                      spent, the on_failure hook marks DELETE_FAILED.
    """

    def execute(self, rdi_id: str, callback_url: str) -> None:
        # lazy import: celery_tasks imports this class, so import the enqueuer at call time
        from hope.apps.registration_data.celery_tasks import notify_rdi_deleted_async_task

        logger.info("RDI wipe job started for %s", rdi_id)
        try:
            marked = self._mark_deleting(rdi_id)  # Txn A
            wiped = marked and self._wipe(rdi_id)  # Txn B (skipped if the row was already gone)
            if not marked or not wiped:
                logger.info("RDI wipe for %s: row already gone → idempotent success", rdi_id)
                notify_rdi_deleted_async_task(callback_url)
                return
        except NonRetriableTaskError as exc:  # MERGED — terminal success, leave status intact, no retry
            logger.warning("RDI wipe for %s aborted: already MERGED, status left intact: %s", rdi_id, exc)
            raise
        except ProtectedError as exc:  # rdi_has_dependents → deterministic, fail fast
            logger.warning("RDI wipe for %s blocked by protected dependents: %s", rdi_id, exc)
            self.mark_failed(rdi_id, reason=str(exc))
            raise NonRetriableTaskError(str(exc)) from exc

        logger.info("RDI wipe for %s succeeded → notifying CW", rdi_id)
        notify_rdi_deleted_async_task(callback_url)

    @staticmethod
    def _mark_deleting(rdi_id: str) -> bool:
        """Lock the RDI, fail fast if MERGED, commit the DELETING marker; False if the row is gone."""
        with transaction.atomic():
            rdi = RegistrationDataImport.objects.select_for_update(of=("self",)).filter(id=rdi_id).first()
            if rdi is None:
                return False
            set_sentry_business_area_tag(rdi.business_area.slug)
            if rdi.status == RegistrationDataImport.MERGED:
                raise NonRetriableTaskError("rdi_already_merged")
            rdi.status = RegistrationDataImport.DELETING
            rdi.save(update_fields=["status"])
            return True

    @staticmethod
    def _wipe(rdi_id: str) -> bool:
        """Re-lock the RDI, defensively fail fast if MERGED, and hard-delete its population. False if gone."""
        with transaction.atomic():
            rdi = (
                RegistrationDataImport.objects.select_for_update(of=("self",))
                .select_related("program")
                .filter(id=rdi_id)
                .first()
            )
            if rdi is None:
                return False
            if rdi.status == RegistrationDataImport.MERGED:
                raise NonRetriableTaskError("rdi_already_merged")
            remove_rdi_population(rdi, delete_rdi=True, swallow_es_errors=True)
            return True

    @staticmethod
    def mark_failed(rdi_id: str, *, reason: str) -> None:
        # own txn so the FAILED write survives the rolled-back wipe txn; keyed on rdi_id so it works
        # even if the wipe's SELECT/lock raised. CW is not told (success-only).
        with transaction.atomic():
            RegistrationDataImport.objects.filter(id=rdi_id).update(
                status=RegistrationDataImport.DELETE_FAILED,
                error_message=reason,
            )
