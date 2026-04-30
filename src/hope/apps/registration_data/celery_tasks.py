from contextlib import contextmanager
import logging
from typing import TYPE_CHECKING, Any

from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from requests.exceptions import RequestException

from hope.apps.core.celery import app
from hope.apps.registration_data.api.deduplication_engine import DeduplicationEngineAPI
from hope.apps.registration_data.exceptions import (
    AlreadyRunningError,
    WrongStatusError,
)
from hope.apps.registration_data.tasks.deduplicate import HardDocumentDeduplication
from hope.apps.registration_data.tasks.rdi_program_population_create import (
    RdiProgramPopulationCreateTask,
)
from hope.apps.utils.sentry import set_sentry_business_area_tag
from hope.models import (
    AsyncRetryJob,
    DeduplicationEngineSimilarityPair,
    Document,
    Individual,
    Program,
    RegistrationDataImport,
)
from hope.models.utils import MergeStatusModel

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


def handle_rdi_exception(rdi_id: str, e: BaseException) -> None:
    try:
        from sentry_sdk import capture_exception

        err = capture_exception(e)
    except Exception as exc:  # pragma: no cover
        err = "N/A"  # pragma: no cover
        logger.exception(exc)  # pragma: no cover
    rdi = RegistrationDataImport.objects.get(id=rdi_id)
    rdi.status = RegistrationDataImport.IMPORT_ERROR
    rdi.sentry_id = err
    rdi.error_message = str(e)
    rdi.save(update_fields=["status", "sentry_id", "error_message"])


@contextmanager
def locked_cache(key: int | str, timeout: int = 60 * 60 * 24) -> Any:
    now = timezone.now()
    acquired = False
    try:
        acquired = cache.get_or_set(key, now, timeout=timeout) == now

        if acquired:
            logger.info(f"Task with key {key} started")
            yield True
        else:
            logger.info(f"Task with key {key} is already running")
            yield False
    finally:
        if acquired:
            cache.delete(key)
            logger.info(f"Task with key {key} finished")


def registration_xlsx_import_async_task_action(job: AsyncRetryJob) -> bool:
    try:
        from hope.apps.registration_data.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )
        from hope.apps.registration_data.tasks.rdi_xlsx_people_create import (
            RdiXlsxPeopleCreateTask,
        )
        from hope.models import Program

        registration_data_import_id = job.config["registration_data_import_id"]
        import_data_id = job.config["import_data_id"]
        business_area_id = job.config["business_area_id"]
        program_id = job.config["program_id"]

        with locked_cache(key=f"registration_xlsx_import_async_task-{registration_data_import_id}") as locked:
            if not locked:
                raise AlreadyRunningError(
                    f"Task with key registration_xlsx_import_async_task"
                    f" {registration_data_import_id} is already running"
                )
            rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(rdi.business_area.name)
            if rdi.status not in (
                RegistrationDataImport.IMPORT_SCHEDULED,
                RegistrationDataImport.IMPORT_ERROR,
            ):
                raise WrongStatusError("Rdi is not in status IMPORT_SCHEDULED while trying to import")
            rdi.status = RegistrationDataImport.IMPORTING
            rdi.save()

            program = Program.objects.get(id=program_id)
            is_social_worker_program = program.is_social_worker_program

            if is_social_worker_program:
                RdiXlsxPeopleCreateTask().execute(
                    registration_data_import_id=registration_data_import_id,
                    import_data_id=import_data_id,
                    business_area_id=business_area_id,
                    program_id=str(program_id),
                )
            else:
                RdiXlsxCreateTask().execute(
                    registration_data_import_id=registration_data_import_id,
                    import_data_id=import_data_id,
                    business_area_id=business_area_id,
                    program_id=str(program_id),
                )
            return True
    except (WrongStatusError, AlreadyRunningError) as exc:
        logger.info(str(exc))
        return True
    except Exception as exc:  # noqa
        handle_rdi_exception(job.config["registration_data_import_id"], exc)
        raise


def registration_xlsx_import_async_task(
    registration_data_import: RegistrationDataImport,
    import_data_id: str,
    business_area_id: str,
    program_id: str,
) -> None:
    registration_data_import_id = str(registration_data_import.id)
    config = {
        "registration_data_import_id": registration_data_import_id,
        "import_data_id": import_data_id,
        "business_area_id": business_area_id,
        "program_id": program_id,
    }
    AsyncRetryJob.queue_task(
        instance=registration_data_import,
        job_name=registration_xlsx_import_async_task.__name__,
        program=registration_data_import.program,
        action="hope.apps.registration_data.celery_tasks.registration_xlsx_import_async_task_action",
        config=config,
        group_key=f"registration_xlsx_import_async_task:{registration_data_import_id}",
        description=f"Import registration xlsx for {registration_data_import_id}",
    )


def registration_program_population_import_async_task_action(job: AsyncRetryJob) -> bool:
    try:
        registration_data_import_id = job.config["registration_data_import_id"]
        cache_key = f"registration_program_population_import_async_task-{registration_data_import_id}"
        with locked_cache(key=cache_key) as locked:
            if not locked:
                raise AlreadyRunningError(f"Task with key {cache_key} is already running")

            rdi = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(rdi.business_area.name)
            if rdi.status not in (
                RegistrationDataImport.IMPORT_SCHEDULED,
                RegistrationDataImport.IMPORT_ERROR,
            ):
                raise WrongStatusError("Rdi is not in status IMPORT_SCHEDULED while trying to import")
            rdi.status = RegistrationDataImport.IMPORTING
            rdi.save()

            RdiProgramPopulationCreateTask().execute(
                registration_data_import_id=registration_data_import_id,
                business_area_id=job.config["business_area_id"],
                import_from_program_id=job.config["import_from_program_id"],
                import_to_program_id=job.config["import_to_program_id"],
            )
            return True
    except (WrongStatusError, AlreadyRunningError) as exc:
        logger.info(str(exc))
        return True
    except RegistrationDataImport.DoesNotExist:
        raise
    except Exception as exc:  # noqa
        logger.warning(exc)
        handle_rdi_exception(job.config["registration_data_import_id"], exc)
        raise


def registration_program_population_import_async_task(
    registration_data_import: RegistrationDataImport,
    business_area_id: str,
    import_from_program_id: str,
    import_to_program_id: str,
) -> None:
    registration_data_import_id = str(registration_data_import.id)
    config = {
        "registration_data_import_id": registration_data_import_id,
        "business_area_id": business_area_id,
        "import_from_program_id": import_from_program_id,
        "import_to_program_id": import_to_program_id,
    }
    AsyncRetryJob.queue_task(
        instance=registration_data_import,
        job_name=registration_program_population_import_async_task.__name__,
        program=registration_data_import.program,
        action="hope.apps.registration_data.celery_tasks.registration_program_population_import_async_task_action",
        config=config,
        group_key=f"registration_program_population_import_async_task:{registration_data_import_id}",
        description=f"Import registration program population for {registration_data_import_id}",
    )


def registration_kobo_import_async_task_action(job: AsyncRetryJob) -> None:
    try:
        from hope.apps.registration_data.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )
        from hope.models import BusinessArea

        registration_data_import_id = job.config["registration_data_import_id"]
        import_data_id = job.config["import_data_id"]
        business_area_id = job.config["business_area_id"]
        program_id = job.config["program_id"]

        set_sentry_business_area_tag(BusinessArea.objects.get(pk=business_area_id).name)
        RdiKoboCreateTask(
            registration_data_import_id=registration_data_import_id,
            business_area_id=business_area_id,
        ).execute(
            import_data_id=import_data_id,
            program_id=program_id,
        )
    except Exception as exc:  # noqa
        logger.warning(exc)
        handle_rdi_exception(job.config["registration_data_import_id"], exc)
        raise


def registration_kobo_import_async_task(
    registration_data_import: RegistrationDataImport,
    import_data_id: str,
    business_area_id: str,
    program_id: str,
) -> None:
    registration_data_import_id = str(registration_data_import.id)
    config = {
        "registration_data_import_id": registration_data_import_id,
        "import_data_id": import_data_id,
        "business_area_id": business_area_id,
        "program_id": program_id,
    }
    AsyncRetryJob.queue_task(
        instance=registration_data_import,
        job_name=registration_kobo_import_async_task.__name__,
        program=registration_data_import.program,
        action="hope.apps.registration_data.celery_tasks.registration_kobo_import_async_task_action",
        config=config,
        group_key=f"registration_kobo_import_async_task:{registration_data_import_id}",
        description=f"Import Kobo registration data for {registration_data_import_id}",
    )


def registration_kobo_import_hourly_async_task_action(job: AsyncRetryJob | None = None) -> None:
    from hope.apps.registration_data.tasks.rdi_kobo_create import (
        RdiKoboCreateTask,
    )

    not_started_rdi = (
        RegistrationDataImport.objects.select_related("business_area", "program", "import_data")
        .filter(status=RegistrationDataImport.LOADING)
        .first()
    )
    if not_started_rdi is None:
        return
    business_area = not_started_rdi.business_area
    program_id = not_started_rdi.program.id
    set_sentry_business_area_tag(business_area.name)

    RdiKoboCreateTask(
        registration_data_import_id=str(not_started_rdi.id),
        business_area_id=str(business_area.id),
    ).execute(
        import_data_id=str(not_started_rdi.import_data.id),
        program_id=str(program_id),
    )


@app.task()
def registration_kobo_import_hourly_async_task() -> None:
    AsyncRetryJob.queue_task(
        job_name=registration_kobo_import_hourly_async_task.__name__,
        action="hope.apps.registration_data.celery_tasks.registration_kobo_import_hourly_async_task_action",
        config={},
        group_key="registration_kobo_import_hourly_async_task",
        description="Import hourly Kobo registration data",
    )


def merge_registration_data_import_async_task_action(job: AsyncRetryJob) -> bool:
    registration_data_import_id = job.config["registration_data_import_id"]
    logger.info(
        f"merge_registration_data_import_async_task started for"
        f" registration_data_import_id: {registration_data_import_id}"
    )
    with locked_cache(key=f"merge_registration_data_import_async_task-{registration_data_import_id}") as locked:
        if not locked:
            return True
        from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
        from hope.models import RegistrationDataImport

        try:
            obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id)
            set_sentry_business_area_tag(obj_hct.business_area.name)

            obj_hct.status = RegistrationDataImport.MERGING
            obj_hct.save(update_fields=["status"])

            RdiMergeTask().execute(registration_data_import_id)
        except Exception as e:  # noqa
            logger.exception(e)
            RegistrationDataImport.objects.filter(
                id=registration_data_import_id,
            ).update(status=RegistrationDataImport.MERGE_ERROR, error_message=str(e))
            raise

    logger.info(
        f"merge_registration_data_import_async_task finished for"
        f" registration_data_import_id: {registration_data_import_id}"
    )
    return True


def merge_registration_data_import_async_task(registration_data_import: RegistrationDataImport) -> None:
    registration_data_import_id = str(registration_data_import.id)
    config = {"registration_data_import_id": registration_data_import_id}
    AsyncRetryJob.queue_task(
        instance=registration_data_import,
        job_name=merge_registration_data_import_async_task.__name__,
        program=registration_data_import.program,
        action="hope.apps.registration_data.celery_tasks.merge_registration_data_import_async_task_action",
        config=config,
        group_key=f"merge_registration_data_import_async_task:{registration_data_import_id}",
        description=f"Merge registration data import {registration_data_import_id}",
    )


def rdi_deduplication_async_task_action(job: AsyncRetryJob) -> None:
    try:
        from hope.apps.registration_data.tasks.deduplicate import DeduplicateTask

        rdi_obj = RegistrationDataImport.objects.get(id=job.config["registration_data_import_id"])
        program_id = rdi_obj.program.id
        set_sentry_business_area_tag(rdi_obj.business_area.slug)
        with transaction.atomic():
            DeduplicateTask(rdi_obj.business_area.slug, program_id).deduplicate_pending_individuals(
                registration_data_import=rdi_obj
            )
    except Exception as exc:  # noqa
        handle_rdi_exception(job.config["registration_data_import_id"], exc)
        raise


def rdi_deduplication_async_task(registration_data_import: RegistrationDataImport) -> None:
    config = {"registration_data_import_id": str(registration_data_import.id)}
    AsyncRetryJob.queue_task(
        instance=registration_data_import,
        job_name=rdi_deduplication_async_task.__name__,
        program=registration_data_import.program,
        action="hope.apps.registration_data.celery_tasks.rdi_deduplication_async_task_action",
        config=config,
        group_key=f"rdi_deduplication_async_task:{str(registration_data_import.id)}",
        description=f"Deduplicate registration data import {str(registration_data_import.id)}",
    )


def pull_kobo_submissions_async_task_action(job: AsyncRetryJob) -> dict:
    from hope.models import KoboImportData

    kobo_import_data = KoboImportData.objects.get(id=job.config["import_data_id"])
    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(kobo_import_data.business_area_slug)
    from hope.apps.registration_data.tasks.pull_kobo_submissions import (
        PullKoboSubmissions,
    )

    try:
        return PullKoboSubmissions().execute(kobo_import_data, program)
    except Exception as exc:  # noqa
        KoboImportData.objects.filter(
            id=kobo_import_data.id,
        ).update(status=KoboImportData.STATUS_ERROR, error=str(exc))
        raise


def pull_kobo_submissions_async_task(import_data_id: str, program_id: str) -> None:
    config = {
        "import_data_id": import_data_id,
        "program_id": program_id,
    }
    AsyncRetryJob.queue_task(
        job_name=pull_kobo_submissions_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.pull_kobo_submissions_async_task_action",
        config=config,
        group_key=f"pull_kobo_submissions_async_task:{import_data_id}",
        description=f"Pull Kobo submissions for import data {import_data_id}",
    )


def validate_xlsx_import_async_task_action(job: AsyncRetryJob) -> dict:
    from hope.apps.registration_data.tasks.validate_xlsx_import import (
        ValidateXlsxImport,
    )
    from hope.models import ImportData, Program

    import_data = ImportData.objects.get(id=job.config["import_data_id"])
    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(import_data.business_area_slug)
    try:
        return ValidateXlsxImport().execute(import_data, program)
    except Exception as exc:  # noqa
        ImportData.objects.filter(
            id=import_data.id,
        ).update(status=ImportData.STATUS_ERROR, error=str(exc))
        raise


def validate_xlsx_import_async_task(import_data_id: str, program_id: str) -> None:
    config = {
        "import_data_id": import_data_id,
        "program_id": program_id,
    }
    AsyncRetryJob.queue_task(
        job_name=validate_xlsx_import_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.validate_xlsx_import_async_task_action",
        config=config,
        group_key=f"validate_xlsx_import_async_task:{import_data_id}",
        description=f"Validate XLSX import {import_data_id}",
    )


def check_and_set_taxid(queryset: "QuerySet") -> dict:
    qs = queryset.filter(unique_field__isnull=True)
    results = {"updated": [], "processed": [], "errors": []}
    for record in qs.iterator(chunk_size=1000):
        try:
            for individual in record.fields["individuals"]:
                if individual["role_i_c"] == "y":
                    record.unique_field = individual["tax_id_no_i_c"]
                    record.save(update_fields=["unique_field"])
                    results["updated"].append(record.pk)
                    break
            results["processed"].append(record.pk)

        except Exception as e:  # noqa
            results["errors"].append(f"Record: {record.pk} - {e.__class__.__name__}: {str(e)}")
    return results


def deduplicate_documents_for_rdi(rdi_id: str) -> bool:
    with locked_cache(key="deduplicate_documents") as locked:
        if not locked:
            return True
        rdi = RegistrationDataImport.objects.get(id=rdi_id)
        with transaction.atomic():
            documents_query = Document.objects.filter(
                status=Document.STATUS_PENDING, individual__registration_data_import=rdi
            )
            HardDocumentDeduplication().deduplicate(
                documents_query,
                registration_data_import=rdi,
            )
    return True


def deduplication_engine_process_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.registration_data.services.biometric_deduplication import (
        BiometricDeduplicationService,
    )

    program = Program.objects.get(id=job.config["program_id"])
    set_sentry_business_area_tag(program.business_area.name)
    BiometricDeduplicationService().upload_and_process_deduplication_set(program)


def deduplication_engine_process_async_task(program_id: str) -> None:
    config = {"program_id": program_id}
    AsyncRetryJob.queue_task(
        job_name=deduplication_engine_process_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.deduplication_engine_process_async_task_action",
        config=config,
        group_key=f"deduplication_engine_process_async_task:{program_id}",
        description=f"Process biometric deduplication for program {program_id}",
    )


def fetch_biometric_deduplication_results_and_process_async_task_action(job: AsyncRetryJob) -> None:
    from hope.apps.registration_data.services.biometric_deduplication import (
        BiometricDeduplicationService,
    )

    program = Program.objects.get(id=job.config["program_id"])
    rdi_id = job.config.get("rdi_id")
    rdi = RegistrationDataImport.objects.get(id=rdi_id) if rdi_id else None
    set_sentry_business_area_tag(program.business_area.name)

    service = BiometricDeduplicationService()
    service.fetch_biometric_deduplication_results_and_process(program, rdi)


def fetch_biometric_deduplication_results_and_process_async_task(
    program_id: str,
    rdi_id: str | None = None,
) -> None:
    config = {
        "program_id": program_id,
        "rdi_id": rdi_id,
    }
    AsyncRetryJob.queue_task(
        job_name=fetch_biometric_deduplication_results_and_process_async_task.__name__,
        program_id=program_id,
        action="hope.apps.registration_data.celery_tasks.fetch_biometric_deduplication_results_and_process_async_task_action",
        config=config,
        group_key=f"fetch_biometric_deduplication_results_and_process_async_task:{program_id}:{rdi_id}",
        description=f"Fetch biometric deduplication results for program {program_id}",
    )


def _persist_individual_duplicates_snapshot(
    program: Program,
    individuals: list[Individual],
) -> None:
    # Denormalised snapshot for FE consumption — `IndividualSerializer` reads these JSON
    # fields directly so the "Possible duplicates" panels can render on individual detail
    # without re-joining DeduplicationEngineSimilarityPair. Kept for parity with legacy
    # (operator-driven) RDIs even though CW RDIs only stay IN_REVIEW transiently — once
    # merged, this snapshot is the historical record of what matched at arrival time.
    #
    # NOTE: legacy flow does the equivalent in
    # `BiometricDeduplicationService.store_rdi_deduplication_statistics`. That version is
    # full-RDI scoped (uses two extra queryset filters per individual → N+1) and also
    # writes status fields + RDI counters. This one is targeted at individuals touched by
    # an arrival finding and does the split in-memory from a single prefetched list.
    # Worth unifying if a third call site appears.
    individual_ids = [ind.id for ind in individuals]
    pairs = list(
        DeduplicationEngineSimilarityPair.objects.filter(program=program)
        .filter(Q(individual1_id__in=individual_ids) | Q(individual2_id__in=individual_ids))
        .select_related("individual1", "individual2")
    )

    for individual in individuals:
        batch_pairs = []
        population_pairs = []
        for pair in pairs:
            if pair.individual1_id == individual.id:
                other = pair.individual2
            elif pair.individual2_id == individual.id:
                other = pair.individual1
            else:
                continue
            if other is None:
                continue
            if other.rdi_merge_status == MergeStatusModel.MERGED:
                population_pairs.append(pair)
            else:
                batch_pairs.append(pair)

        individual.biometric_deduplication_batch_results = (
            DeduplicationEngineSimilarityPair.serialize_for_individual(individual, batch_pairs) if batch_pairs else []
        )
        individual.biometric_deduplication_golden_record_results = (
            DeduplicationEngineSimilarityPair.serialize_for_individual(individual, population_pairs)
            if population_pairs
            else []
        )
        individual.save(
            update_fields=[
                "biometric_deduplication_batch_results",
                "biometric_deduplication_golden_record_results",
            ]
        )


@app.task(
    autoretry_for=(RequestException,),
    retry_backoff=True,
    retry_backoff_max=120,
    retry_kwargs={"max_retries": 5},
)
def classify_findings_and_schedule_merge_task(rdi_id: str) -> None:
    rdi = RegistrationDataImport.objects.select_related("program").get(pk=rdi_id)
    set_sentry_business_area_tag(rdi.business_area.name)

    findings = list(DeduplicationEngineAPI().get_group_findings(rdi.correlation_id))

    cw_ids: set[str] = set()
    for finding in findings:
        cw_ids.add(str(finding["first"]["reference_pk"]))
        cw_ids.add(str(finding["second"]["reference_pk"]))

    cw_to_individual: dict[str, Individual] = {}
    if cw_ids:
        cw_to_individual = {
            ind.country_workspace_id: ind for ind in Individual.all_objects.filter(country_workspace_id__in=cw_ids)
        }

    pairs_to_create: list[DeduplicationEngineSimilarityPair] = []
    touched_individuals: dict[str, Individual] = {}

    for finding in findings:
        first_cw = str(finding["first"]["reference_pk"])
        second_cw = str(finding["second"]["reference_pk"])
        ind1 = cw_to_individual.get(first_cw)
        ind2 = cw_to_individual.get(second_cw)
        if ind1 is None or ind2 is None:
            missing = first_cw if ind1 is None else second_cw
            other = second_cw if ind1 is None else first_cw
            logger.warning(
                "Arrival hook: country_workspace_id %s not found in HOPE; dropping finding (other side cw_id=%s)",
                missing,
                other,
            )
            continue
        if ind1.id == ind2.id:
            logger.warning(
                "Arrival hook: dedup engine returned self-pair for individual %s (cw_ids %s, %s); skipping",
                ind1.id,
                first_cw,
                second_cw,
            )
            continue

        # Sorted to satisfy DeduplicationEngineSimilarityPair's individual1__lt=individual2 CHECK constraint
        ordered = sorted([ind1, ind2], key=lambda i: i.id)
        pairs_to_create.append(
            DeduplicationEngineSimilarityPair(
                program=rdi.program,
                individual1=ordered[0],
                individual2=ordered[1],
                similarity_score=finding["score"] * 100,
                status_code=str(finding["status_code"]),
            )
        )
        touched_individuals[str(ind1.id)] = ind1
        touched_individuals[str(ind2.id)] = ind2

    if pairs_to_create:
        # ignore_conflicts: pair model has unique_together (individual1, individual2);
        # task can re-run (Celery retry or repeated webhook) so duplicates must be silently skipped
        DeduplicationEngineSimilarityPair.objects.bulk_create(pairs_to_create, ignore_conflicts=True)

    if touched_individuals:
        _persist_individual_duplicates_snapshot(rdi.program, list(touched_individuals.values()))

    with transaction.atomic():
        locked_rdi = RegistrationDataImport.objects.select_for_update().get(pk=rdi_id)
        if locked_rdi.status != RegistrationDataImport.IN_REVIEW:
            return
        locked_rdi.status = RegistrationDataImport.MERGE_SCHEDULED
        locked_rdi.save(update_fields=["status"])
        merge_registration_data_import_async_task(locked_rdi)
