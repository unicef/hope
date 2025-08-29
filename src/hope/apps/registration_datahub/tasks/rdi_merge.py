import contextlib
import logging
from typing import Iterable

from django.core.cache import cache
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.core.utils import chunks
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
)
from hope.apps.household.celery_tasks import recalculate_population_fields_task
from hope.apps.household.documents import HouseholdDocument, get_individual_doc
from hope.apps.registration_datahub.celery_tasks import deduplicate_documents
from hope.apps.registration_datahub.services.biometric_deduplication import (
    BiometricDeduplicationService,
)
from hope.apps.registration_datahub.signals import rdi_merged
from hope.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    check_against_sanction_list_pre_merge,
)
from hope.apps.utils.elasticsearch_utils import (
    populate_index,
    remove_elasticsearch_documents_by_matching_ids,
)
from hope.apps.utils.querysets import evaluate_qs
from hope.models.account import PendingAccount
from hope.models.document import PendingDocument
from hope.models.household import (
    DUPLICATE,
    NEEDS_ADJUDICATION,
    Household,
    HouseholdCollection,
    PendingHousehold,
)
from hope.models.individual import Individual, IndividualCollection, PendingIndividual
from hope.models.individual_role_in_household import PendingIndividualRoleInHousehold
from hope.models.kobo_imported_submission import KoboImportedSubmission
from hope.models.log_entry import log_create
from hope.models.registration_data_import import (
    RegistrationDataImport,
)
from hope.models.utils import MergeStatusModel

logger = logging.getLogger(__name__)


class RdiMergeTask:
    def execute(self, registration_data_import_id: str) -> None:
        try:
            obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id)
            households = PendingHousehold.objects.filter(registration_data_import=obj_hct)

            individuals = PendingIndividual.objects.filter(registration_data_import=obj_hct).order_by(
                "first_registration_date"
            )
            individual_ids = list(individuals.values_list("id", flat=True))
            household_ids = list(households.values_list("id", flat=True))
            if not individual_ids and not household_ids:
                # empty RDI, nothing to merge, happens when all households have extra_rdi
                obj_hct.status = RegistrationDataImport.MERGED
                obj_hct.save()
                return

            household_ids_to_exclude = []
            if obj_hct.program.collision_detection_enabled:
                for ids in chunks(household_ids, 1000):
                    households = PendingHousehold.objects.filter(id__in=ids)
                    for household in households:
                        collided_id = obj_hct.program.collision_detector.detect_collision(household)
                        if not collided_id:
                            continue
                        household_ids_to_exclude.append(household.id)
                        obj_hct.program.collision_detector.update_household(household)
                        updated_household = Household.objects.get(id=collided_id)
                        updated_household.extra_rdis.add(obj_hct)
            household_ids = list(set(household_ids) - set(household_ids_to_exclude))
            individual_ids = list(
                Individual.all_objects.filter(registration_data_import=obj_hct, id__in=individual_ids)
                .exclude(household__in=household_ids_to_exclude)
                .values_list("id", flat=True)
            )

            try:
                with transaction.atomic():
                    old_obj_hct = copy_model_object(obj_hct)

                    transaction.on_commit(lambda: recalculate_population_fields_task(household_ids, obj_hct.program_id))
                    logger.info(
                        f"RDI:{registration_data_import_id} Recalculated population fields for {len(household_ids)}"
                        f" households"
                    )
                    kobo_submissions = []
                    for household in households.only("kobo_submission_uuid", "detail_id", "kobo_submission_time"):
                        kobo_submission_uuid = household.kobo_submission_uuid
                        kobo_asset_id = household.detail_id
                        kobo_submission_time = household.kobo_submission_time
                        if kobo_submission_uuid and kobo_asset_id and kobo_submission_time:
                            submission = KoboImportedSubmission(
                                kobo_submission_uuid=kobo_submission_uuid,
                                kobo_asset_id=kobo_asset_id,
                                kobo_submission_time=kobo_submission_time,
                                registration_data_import=obj_hct,
                                imported_household=household,
                            )
                            kobo_submissions.append(submission)
                    if kobo_submissions:
                        KoboImportedSubmission.objects.bulk_create(kobo_submissions)
                    logger.info(f"RDI:{registration_data_import_id} Created {len(kobo_submissions)} kobo submissions")
                    logger.info(
                        f"RDI:{registration_data_import_id} Populated index for {len(household_ids)} households"
                    )

                    dmds = PendingAccount.objects.filter(
                        individual_id__in=individual_ids,
                    )
                    PendingAccount.validate_uniqueness(dmds)
                    dmds.update(rdi_merge_status=MergeStatusModel.MERGED)
                    PendingIndividualRoleInHousehold.objects.filter(
                        household_id__in=household_ids, individual_id__in=individual_ids
                    ).update(rdi_merge_status=MergeStatusModel.MERGED)
                    PendingDocument.objects.filter(individual_id__in=individual_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED
                    )
                    PendingIndividualRoleInHousehold.objects.filter(individual_id__in=individual_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED
                    )
                    PendingHousehold.objects.filter(id__in=household_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED,
                        updated_at=timezone.now(),
                    )
                    PendingIndividual.objects.filter(id__in=individual_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED,
                        updated_at=timezone.now(),
                    )
                    populate_index(
                        Individual.objects.filter(registration_data_import=obj_hct),
                        get_individual_doc(obj_hct.business_area.slug),
                    )

                    individuals = evaluate_qs(
                        Individual.objects.filter(registration_data_import=obj_hct).select_for_update().order_by("pk")
                    )
                    households = evaluate_qs(
                        Household.objects.filter(registration_data_import=obj_hct).select_for_update().order_by("pk")
                    )

                    if not obj_hct.business_area.postpone_deduplication and len(individuals):
                        # DEDUPLICATION
                        DeduplicateTask(
                            obj_hct.business_area.slug, obj_hct.program.id
                        ).deduplicate_individuals_against_population(individuals)
                        logger.info(f"RDI:{registration_data_import_id} Deduplicated {len(individual_ids)} individuals")
                        golden_record_duplicates = Individual.objects.filter(
                            registration_data_import=obj_hct,
                            deduplication_golden_record_status=DUPLICATE,
                        )
                        logger.info(
                            f"RDI:{registration_data_import_id} Found {len(golden_record_duplicates)} duplicates"
                        )

                        create_needs_adjudication_tickets(
                            golden_record_duplicates,
                            "duplicates",
                            obj_hct.business_area,
                            registration_data_import=obj_hct,
                            issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
                        )
                        logger.info(
                            f"RDI:{registration_data_import_id} Created tickets for {len(golden_record_duplicates)}"
                            f" duplicates"
                        )

                        needs_adjudication = Individual.objects.filter(
                            registration_data_import=obj_hct,
                            deduplication_golden_record_status=NEEDS_ADJUDICATION,
                        )
                        logger.info(
                            f"RDI:{registration_data_import_id} Found {len(needs_adjudication)} needs adjudication"
                        )

                        create_needs_adjudication_tickets(
                            needs_adjudication,
                            "possible_duplicates",
                            obj_hct.business_area,
                            registration_data_import=obj_hct,
                            issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
                        )
                        logger.info(
                            f"RDI:{registration_data_import_id} Created tickets for {len(needs_adjudication)}"
                            f" needs adjudication"
                        )

                    # SANCTION LIST CHECK
                    if obj_hct.should_check_against_sanction_list() and obj_hct.program.sanction_lists.exists():
                        logger.info(f"RDI:{registration_data_import_id} Checking against sanction list")
                        check_against_sanction_list_pre_merge(
                            program_id=obj_hct.program.id,
                            registration_data_import=obj_hct,
                            individuals_ids=Individual.objects.filter(registration_data_import=obj_hct).values_list(
                                "id", flat=True
                            ),
                        )
                        logger.info(f"RDI:{registration_data_import_id} Checked against sanction list")

                    # synchronously deduplicate documents
                    deduplicate_documents(rdi_id=obj_hct.id)
                    #  synchronously deduplicate biometrics
                    if obj_hct.program.biometric_deduplication_enabled:
                        dedupe_service = BiometricDeduplicationService()
                        dedupe_service.create_grievance_tickets_for_duplicates(obj_hct)
                        dedupe_service.update_rdis_deduplication_statistics(obj_hct.program, exclude_rdi=obj_hct)

                    obj_hct.status = RegistrationDataImport.MERGED
                    obj_hct.save()
                    obj_hct.update_duplicates_against_population_statistics()
                    # create household and individual collections - only for Program Population Import
                    if obj_hct.data_source == RegistrationDataImport.PROGRAM_POPULATION:
                        self._update_household_collections(households, obj_hct)
                        self._update_individual_collections(individuals, obj_hct)

                    logger.info(
                        f"RDI:{registration_data_import_id} Populated index for {len(individual_ids)} individuals"
                    )
                    populate_index(
                        Household.objects.filter(registration_data_import=obj_hct),
                        HouseholdDocument,
                    )
                    logger.info(f"RDI:{registration_data_import_id} Saved registration data import")

                    rdi_merged.send(sender=obj_hct.__class__, instance=obj_hct)
                    log_create(
                        RegistrationDataImport.ACTIVITY_LOG_MAPPING,
                        "business_area",
                        None,
                        obj_hct.program_id,
                        old_obj_hct,
                        obj_hct,
                    )
                    logger.info(f"Datahub data for RDI: {obj_hct.id} was cleared")
            except Exception:
                # remove es individuals if exists
                remove_elasticsearch_documents_by_matching_ids(
                    individual_ids, get_individual_doc(obj_hct.business_area.slug)
                )

                # remove es households if exists
                remove_elasticsearch_documents_by_matching_ids(household_ids, HouseholdDocument)
                raise

            with contextlib.suppress(ConnectionError, AttributeError):
                for key in cache.keys("*"):
                    if key.startswith(
                        (
                            f"count_{obj_hct.business_area.slug}_HouseholdNodeConnection",
                            f"count_{obj_hct.business_area.slug}_IndividualNodeConnection",
                        )
                    ):
                        cache.delete(key)

        except Exception as e:
            logger.warning(e)
            raise

    def _update_household_collections(self, households: QuerySet[Household], rdi: RegistrationDataImport) -> None:
        households_to_update = []
        # if there are at least 2 households with the same unicef_id, they already have a collection -
        # and new representation will be added to it
        # if this is the 2nd representation -
        # the collection is created now for the new representation and the existing one
        for household in households:
            # find other household with the same unicef_id and group them in the same collection
            household_from_collection = (
                Household.objects.filter(unicef_id=household.unicef_id, business_area=rdi.business_area)
                .exclude(registration_data_import=rdi)
                .first()
            )
            if household_from_collection:
                if collection := household_from_collection.household_collection:
                    household.household_collection = collection
                    households_to_update.append(household)
                else:
                    household_collection = HouseholdCollection.objects.create()
                    household.household_collection = household_collection
                    household_from_collection.household_collection = household_collection
                    households_to_update.append(household)
                    households_to_update.append(household_from_collection)

        Household.all_objects.bulk_update(households_to_update, ["household_collection"])

    def _update_individual_collections(self, individuals: Iterable, rdi: RegistrationDataImport) -> None:
        individuals_to_update = []
        for individual in individuals:
            # find other individual with the same unicef_id and group them in the same collection
            individual_from_collection = (
                Individual.objects.filter(
                    unicef_id=individual.unicef_id,
                    business_area=rdi.business_area,
                )
                .exclude(registration_data_import=rdi)
                .first()
            )
            if individual_from_collection:
                if collection := individual_from_collection.individual_collection:
                    individual.individual_collection = collection
                    individuals_to_update.append(individual)
                else:
                    individual_collection = IndividualCollection.objects.create()
                    individual.individual_collection = individual_collection
                    individual_from_collection.individual_collection = individual_collection

                    individuals_to_update.append(individual_from_collection)
                    individuals_to_update.append(individual)
        Individual.all_objects.bulk_update(individuals_to_update, ["individual_collection"])
