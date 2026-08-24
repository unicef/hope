import logging

from django.db import transaction
from django.db.models.deletion import ProtectedError

from hope.apps.core.celery_tasks import NonRetriableTaskError
from hope.apps.registration_data.services.rdi_removal import remove_rdi_population
from hope.apps.registration_data.signals import invalidate_rdi_cache
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import Program, RegistrationDataImport

logger = logging.getLogger(__name__)


class RdiPopulationRemoval:
    """Retriable hard-delete of a CW-managed RDI's population.

    Concurrency: the merge is excluded by the RDI row lock taken in ``_wipe`` — the CW merge
    (``fetch_findings_and_merge_rdi_action``) holds ``select_for_update`` on the same row for its
    whole merge transaction and re-picks the RDI with ``skip_locked`` plus a status filter that
    excludes ``DELETE_SCHEDULED``. A second concurrent wipe is prevented one layer up by
    ``AsyncRetryJob.requeue``, which refuses to queue while a job for this RDI is active.

    Outcomes:
      - success / already-gone row  → enqueue the CW success callback (success-only).
      - MERGED                       → nothing to wipe; leave status intact, no retry, no callback.
      - ProtectedError (dependents) → DELETE_FAILED, no retry.
      - any other error             → propagates; async_retry_job_task retries and, once
                                      spent, the on_failure hook marks DELETE_FAILED.
    """

    def execute(self, rdi_id: str, callback_url: str, signed_token: str, program_id: str) -> None:
        from hope.apps.registration_data.celery_tasks import notify_rdi_deleted_async_task

        logger.info("RDI reset job started for %s", rdi_id)
        try:
            if not self._wipe(rdi_id):
                logger.info("RDI wipe for %s: row already gone.", rdi_id)
                notify_rdi_deleted_async_task(callback_url, signed_token, Program.objects.get(id=program_id))
                return
        except NonRetriableTaskError:  # MERGED
            logger.warning("RDI wipe for %s aborted: RDI already MERGED.", rdi_id)
            raise
        except ProtectedError as exc:
            logger.warning("RDI wipe for %s blocked by protected dependents: %s", rdi_id, exc)
            self.mark_failed(rdi_id, reason=str(exc))
            raise NonRetriableTaskError(str(exc)) from exc

        logger.info("RDI wipe for %s succeeded → notifying CW", rdi_id)
        notify_rdi_deleted_async_task(callback_url, signed_token, Program.objects.get(id=program_id))

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
            rdi = (
                RegistrationDataImport.objects.select_related("business_area", "program")
                .filter(id=rdi_id)
                .first()
            )
            if rdi is None:
                return
            RegistrationDataImport.objects.filter(id=rdi_id).update(
                status=RegistrationDataImport.DELETE_FAILED,
                error_message=reason,
            )
            invalidate_rdi_cache(rdi.business_area.slug, rdi.program.code)
