import logging

from django.db import transaction
from django.db.models.deletion import ProtectedError

from hope.apps.core.celery_tasks import NonRetriableTaskError
from hope.apps.registration_data.services.rdi_removal import remove_rdi_population
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import RegistrationDataImport

logger = logging.getLogger(__name__)


class RdiPopulationRemoval:
    """Retriable hard-delete of a CW-managed RDI's population.

    Outcomes:
      - success / already-gone row  → enqueue the CW success callback (success-only).
      - MERGED                       → nothing to wipe; leave status intact, no retry, no callback.
      - ProtectedError (dependents) → DELETE_FAILED, no retry.
      - any other error             → propagates; async_retry_job_task retries and, once
                                      spent, the on_failure hook marks DELETE_FAILED.
    """

    def execute(self, rdi_id: str, callback_url: str, signed_token: str) -> None:
        from hope.apps.registration_data.celery_tasks import locked_cache, notify_rdi_deleted_async_task

        logger.info("RDI reset job started for %s", rdi_id)
        with locked_cache(key=f"merge_registration_data_import_async_task-{rdi_id}") as acquired:
            if not acquired:
                logger.info("RDI wipe for %s deferred: a merge holds the lock", rdi_id)
                raise RuntimeError("rdi_merge_in_progress")
            try:
                if not self._wipe(rdi_id):
                    logger.info("RDI wipe for %s: row already gone.", rdi_id)
                    notify_rdi_deleted_async_task(callback_url, signed_token)
                    return
            except NonRetriableTaskError:  # MERGED
                logger.warning("RDI wipe for %s aborted: RDI already MERGED.", rdi_id)
                raise
            except ProtectedError as exc:
                logger.warning("RDI wipe for %s blocked by protected dependents: %s", rdi_id, exc)
                self.mark_failed(rdi_id, reason=str(exc))
                raise NonRetriableTaskError(str(exc)) from exc

            logger.info("RDI wipe for %s succeeded → notifying CW", rdi_id)
            notify_rdi_deleted_async_task(callback_url, signed_token)

    @staticmethod
    def _wipe(rdi_id: str) -> bool:
        """Lock the RDI, fail fast if MERGED, and hard-delete its population. False if the row is gone."""
        with transaction.atomic():
            rdi = (
                RegistrationDataImport.objects.select_for_update(of=("self",))
                .select_related("program")
                .filter(id=rdi_id)
                .first()
            )
            if rdi is None:
                return False
            set_sentry_business_area_tag(rdi.business_area.slug)
            if rdi.status == RegistrationDataImport.MERGED:
                raise NonRetriableTaskError("rdi_already_merged")
            remove_rdi_population(rdi, delete_rdi=True, swallow_es_errors=True)
            return True

    @staticmethod
    def mark_failed(rdi_id: str, *, reason: str) -> None:
        # Internal use only, CW is not told about failure.
        with transaction.atomic():
            RegistrationDataImport.objects.filter(id=rdi_id).update(
                status=RegistrationDataImport.DELETE_FAILED,
                error_message=reason,
            )
