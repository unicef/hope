import logging

from hope.models import RegistrationDataImport

logger = logging.getLogger(__name__)


class RdiMergeDispatcher:
    """Lock-free "who's next" policy for a program's Country Workspace merge queue.

    The queue is every RDI for the program that has finished uploading but not yet
    merged, ordered by ``import_date`` (arrival order). The head decides everything:

    - empty                              → nothing to do
    - head is ``MERGE_SCHEDULED``        → enqueue the per-RDI merge job for it
    - head is ``MERGE_ERROR`` / ``IMPORT_ERROR`` → queue is paused (needs admin retry)
    - head is ``MERGING``                → a worker is already on it

    The dispatcher holds no lock. Serialization is enforced downstream by the
    per-program lock in ``fetch_findings_and_merge_rdi_action`` plus the
    ``MERGE_SCHEDULED``→``MERGING`` transition, so overlapping dispatcher runs are safe:
    two runs may enqueue the same head, but only one merge job body ever runs.
    """

    # Statuses that occupy the merge queue. IMPORT_ERROR is included defensively — it is an
    # invalid state for a CW RDI, but if one ever appears it blocks the queue rather than
    # letting newer RDIs merge ahead of it and break arrival order.
    _QUEUE_STATUSES = [
        RegistrationDataImport.MERGE_SCHEDULED,
        RegistrationDataImport.MERGING,
        RegistrationDataImport.MERGE_ERROR,
        RegistrationDataImport.IMPORT_ERROR,
    ]

    def execute(self, program_id: str) -> None:
        from hope.apps.registration_data.celery_tasks import fetch_findings_and_merge_rdi

        head = (
            RegistrationDataImport.objects.filter(program_id=program_id, status__in=self._QUEUE_STATUSES)
            # "id" is a stable tiebreak so same-instant import_dates don't let the head flap
            # between dispatcher runs (import_date is auto_now_add, ties are possible).
            .order_by("import_date", "id")
            .first()
        )
        if head is None:
            logger.info(f"RDI merge queue empty for program {program_id}")
            return
        if head.status != RegistrationDataImport.MERGE_SCHEDULED:
            logger.info(f"RDI merge queue for program {program_id} not advanced: head RDI:{head.id} is {head.status}")
            return
        fetch_findings_and_merge_rdi(head)
