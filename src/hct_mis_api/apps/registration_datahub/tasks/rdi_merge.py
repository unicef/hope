import contextlib
import logging

from django.core.cache import cache
from django.db import transaction

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
)
from hct_mis_api.apps.household.celery_tasks import recalculate_population_fields_task
from hct_mis_api.apps.household.documents import HouseholdDocument, get_individual_doc
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    NEEDS_ADJUDICATION,
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
    PendingBankAccountInfo,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import PendingDeliveryMechanismData
from hct_mis_api.apps.registration_data.models import (
    KoboImportedSubmission,
    RegistrationDataImport,
)
from hct_mis_api.apps.registration_datahub.celery_tasks import deduplicate_documents
from hct_mis_api.apps.registration_datahub.services.biometric_deduplication import (
    BiometricDeduplicationService,
)
from hct_mis_api.apps.registration_datahub.signals import rdi_merged
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    CheckAgainstSanctionListPreMergeTask,
)
from hct_mis_api.apps.utils.elasticsearch_utils import (
    populate_index,
    remove_elasticsearch_documents_by_matching_ids,
)
from hct_mis_api.apps.utils.models import MergeStatusModel
from hct_mis_api.apps.utils.querysets import evaluate_qs

logger = logging.getLogger(__name__)


class RdiMergeTask:
    HOUSEHOLD_FIELDS = (
        "consent_sign",
        "consent",
        "consent_sharing",
        "residence_status",
        "country_origin",
        "zip_code",
        "size",
        "address",
        "country",
        "female_age_group_0_5_count",
        "female_age_group_6_11_count",
        "female_age_group_12_17_count",
        "female_age_group_18_59_count",
        "female_age_group_60_count",
        "pregnant_count",
        "male_age_group_0_5_count",
        "male_age_group_6_11_count",
        "male_age_group_12_17_count",
        "male_age_group_18_59_count",
        "male_age_group_60_count",
        "female_age_group_0_5_disabled_count",
        "female_age_group_6_11_disabled_count",
        "female_age_group_12_17_disabled_count",
        "female_age_group_18_59_disabled_count",
        "female_age_group_60_disabled_count",
        "male_age_group_0_5_disabled_count",
        "male_age_group_6_11_disabled_count",
        "male_age_group_12_17_disabled_count",
        "male_age_group_18_59_disabled_count",
        "male_age_group_60_disabled_count",
        "other_sex_group_count",
        "unknown_sex_group_count",
        "first_registration_date",
        "last_registration_date",
        "flex_fields",
        "start",
        "deviceid",
        "name_enumerator",
        "org_enumerator",
        "org_name_enumerator",
        "village",
        "registration_method",
        "currency",
        "unhcr_id",
        "geopoint",
        "returnee",
        "fchild_hoh",
        "child_hoh",
        "detail_id",
        "collect_type",
    )

    INDIVIDUAL_FIELDS = (
        "id",
        "photo",
        "full_name",
        "given_name",
        "middle_name",
        "family_name",
        "relationship",
        "sex",
        "birth_date",
        "estimated_birth_date",
        "marital_status",
        "phone_no",
        "phone_no_alternative",
        "email",
        "disability",
        "flex_fields",
        "first_registration_date",
        "last_registration_date",
        "deduplication_batch_status",
        "deduplication_batch_results",
        "observed_disability",
        "seeing_disability",
        "hearing_disability",
        "physical_disability",
        "memory_disability",
        "selfcare_disability",
        "comms_disability",
        "who_answers_phone",
        "who_answers_alt_phone",
        "pregnant",
        "work_status",
        "detail_id",
        "disability_certificate_picture",
        "preferred_language",
        "age_at_registration",
        "payment_delivery_phone_no",
        "wallet_name",
        "blockchain_name",
        "wallet_address",
    )

    def execute(self, registration_data_import_id: str) -> None:
        try:
            obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id)
            households = PendingHousehold.objects.filter(registration_data_import=obj_hct)
            individuals = PendingIndividual.objects.filter(registration_data_import=obj_hct).order_by(
                "first_registration_date"
            )
            individual_ids = list(individuals.values_list("id", flat=True))
            household_ids = list(households.values_list("id", flat=True))
            try:
                with transaction.atomic():
                    old_obj_hct = copy_model_object(obj_hct)

                    transaction.on_commit(lambda: recalculate_population_fields_task(household_ids, obj_hct.program_id))
                    logger.info(
                        f"RDI:{registration_data_import_id} Recalculated population fields for {len(household_ids)} households"
                    )
                    kobo_submissions = []
                    for household in households:
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

                    dmds = PendingDeliveryMechanismData.objects.filter(
                        individual_id__in=individual_ids,
                    )
                    PendingDeliveryMechanismData.validate_uniqueness(dmds)
                    dmds.update(rdi_merge_status=MergeStatusModel.MERGED)
                    PendingIndividualRoleInHousehold.objects.filter(
                        household_id__in=household_ids, individual_id__in=individual_ids
                    ).update(rdi_merge_status=MergeStatusModel.MERGED)
                    PendingBankAccountInfo.objects.filter(individual_id__in=individual_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED
                    )
                    PendingDocument.objects.filter(individual_id__in=individual_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED
                    )
                    PendingIndividualRoleInHousehold.objects.filter(individual_id__in=individual_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED
                    )
                    PendingHousehold.objects.filter(id__in=household_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED
                    )
                    PendingIndividual.objects.filter(id__in=individual_ids).update(
                        rdi_merge_status=MergeStatusModel.MERGED
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

                    if not obj_hct.business_area.postpone_deduplication:
                        # DEDUPLICATION
                        DeduplicateTask(
                            obj_hct.business_area.slug, obj_hct.program.id
                        ).deduplicate_individuals_against_population(individuals)
                        logger.info(f"RDI:{registration_data_import_id} Deduplicated {len(individual_ids)} individuals")
                        golden_record_duplicates = Individual.objects.filter(
                            registration_data_import=obj_hct, deduplication_golden_record_status=DUPLICATE
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
                            f"RDI:{registration_data_import_id} Created tickets for {len(golden_record_duplicates)} duplicates"
                        )

                        needs_adjudication = Individual.objects.filter(
                            registration_data_import=obj_hct, deduplication_golden_record_status=NEEDS_ADJUDICATION
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
                            f"RDI:{registration_data_import_id} Created tickets for {len(needs_adjudication)} needs adjudication"
                        )

                    # SANCTION LIST CHECK
                    if obj_hct.should_check_against_sanction_list() and obj_hct.business_area.screen_beneficiary:
                        logger.info(f"RDI:{registration_data_import_id} Checking against sanction list")
                        CheckAgainstSanctionListPreMergeTask.execute(registration_data_import=obj_hct)
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
                    populate_index(Household.objects.filter(registration_data_import=obj_hct), HouseholdDocument)
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
            logger.error(e)
            raise

    def _update_household_collections(self, households: list, rdi: RegistrationDataImport) -> None:
        households_to_update = []
        # if there are at least 2 households with the same unicef_id, they already have a collection - and new representation will be added to it
        # if this is the 2nd representation - the collection is created now for the new representation and the existing one
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

    def _update_individual_collections(self, individuals: list, rdi: RegistrationDataImport) -> None:
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
