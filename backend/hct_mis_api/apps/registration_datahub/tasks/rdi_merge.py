import contextlib
import logging
from typing import Dict, List, Tuple
from uuid import UUID

from django.core.cache import cache
from django.db import transaction
from django.db.models import QuerySet
from django.forms import model_to_dict

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketIndividualDataUpdateDetails,
)
from hct_mis_api.apps.household.celery_tasks import recalculate_population_fields_task
from hct_mis_api.apps.household.documents import HouseholdDocument, get_individual_doc
from hct_mis_api.apps.household.models import (
    HEAD,
    DocumentType,
    HouseholdCollection,
    IndividualCollection,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
    PendingBankAccountInfo,
    PendingDocument,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanismData,
    PendingDeliveryMechanismData,
)
from hct_mis_api.apps.registration_data.models import (
    KoboImportedSubmission,
    RegistrationDataImport,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.celery_tasks import deduplicate_documents
from hct_mis_api.apps.registration_datahub.documents import get_imported_individual_doc
from hct_mis_api.apps.registration_datahub.signals import rdi_merged
from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    CheckAgainstSanctionListPreMergeTask,
)
from hct_mis_api.apps.utils.elasticsearch_utils import (
    populate_index,
    remove_elasticsearch_documents_by_matching_ids,
)
from hct_mis_api.apps.utils.phone import is_valid_phone_number

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
        "collect_individual_data",
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


    #
    # def _prepare_households(
    #     self, imported_households: List[Household], obj_hct: RegistrationDataImport
    # ) -> Dict[int, Household]:
    #     households_dict = {}
    #     countries = {}
    #     for imported_household in imported_households:
    #         household_data = {**model_to_dict(imported_household, fields=self.HOUSEHOLD_FIELDS)}
    #         country = household_data.pop("country")
    #         country_origin = household_data.pop("country_origin")
    #
    #         if country and country.code not in countries:
    #             countries[country.code] = Country.objects.get(iso_code2=country.code)
    #         if country_origin and country_origin.code not in countries:
    #             countries[country_origin.code] = Country.objects.get(iso_code2=country_origin.code)
    #
    #         if country := countries.get(country.code):
    #             household_data["country"] = country
    #
    #         if country_origin := countries.get(country_origin.code):
    #             household_data["country_origin"] = country_origin
    #
    #         if record := imported_household.flex_registrations_record:
    #             household_data["registration_id"] = str(record.registration)
    #
    #         if enumerator_rec_id := imported_household.enumerator_rec_id:
    #             household_data["enumerator_rec_id"] = enumerator_rec_id
    #
    #         if unicef_id := imported_household.mis_unicef_id:
    #             household_data["unicef_id"] = unicef_id
    #             # find other household with same unicef_id and group them in the same collection
    #             household_from_collection = Household.objects.filter(
    #                 unicef_id=unicef_id, business_area=obj_hct.business_area
    #             ).first()
    #             if household_from_collection:
    #                 if collection := household_from_collection.household_collection:
    #                     household_data["household_collection"] = collection
    #                 else:
    #                     household_collection = HouseholdCollection.objects.create()
    #                     household_data["household_collection"] = household_collection
    #                     household_from_collection.household_collection = household_collection
    #                     household_from_collection.save(update_fields=["household_collection"])
    #
    #         household = Household(
    #             **household_data,
    #             registration_data_import=obj_hct,
    #             business_area=obj_hct.business_area,
    #             program=obj_hct.program,
    #         )
    #         self.merge_admin_areas(imported_household, household)
    #         households_dict[imported_household.id] = household
    #
    #     return households_dict
    #

    #
    # def _prepare_individuals(
    #     self,
    #     imported_individuals: List[Individual],
    #     households_dict: Dict[int, Household],
    #     obj_hct: RegistrationDataImport,
    # ) -> None:
    #     individuals_dict = {}
    #     documents_to_create = []
    #     identities_to_create = []
    #     for imported_individual in imported_individuals:
    #         values = model_to_dict(imported_individual, fields=self.INDIVIDUAL_FIELDS)
    #
    #         if not values.get("phone_no_valid"):
    #             values["phone_no_valid"] = False
    #         if not values.get("phone_no_alternative_valid"):
    #             values["phone_no_alternative_valid"] = False
    #
    #         imported_individual_household = imported_individual.household
    #         household = households_dict.get(imported_individual.household.id) if imported_individual_household else None
    #
    #         phone_no = values.get("phone_no")
    #         phone_no_alternative = values.get("phone_no_alternative")
    #
    #         values["phone_no_valid"] = is_valid_phone_number(str(phone_no))
    #         values["phone_no_alternative_valid"] = is_valid_phone_number(str(phone_no_alternative))
    #
    #         if unicef_id := imported_individual.mis_unicef_id:
    #             values["unicef_id"] = unicef_id
    #             # find other individual with same unicef_id and group them in the same collection
    #             individual_from_collection = Individual.objects.filter(
    #                 unicef_id=unicef_id, business_area=obj_hct.business_area
    #             ).first()
    #             if individual_from_collection:
    #                 if collection := individual_from_collection.individual_collection:
    #                     values["individual_collection"] = collection
    #                 else:
    #                     individual_collection = IndividualCollection.objects.create()
    #                     values["individual_collection"] = individual_collection
    #                     individual_from_collection.individual_collection = individual_collection
    #                     individual_from_collection.save(update_fields=["individual_collection"])
    #
    #         individual = Individual(
    #             **values,
    #             household=household,
    #             registration_id=getattr(household, "registration_id", None),
    #             business_area=obj_hct.business_area,
    #             registration_data_import=obj_hct,
    #             imported_individual_id=imported_individual.id,
    #             program=obj_hct.program,
    #         )
    #         if household:
    #             individual.registration_id = household.registration_id
    #         individuals_dict[imported_individual.id] = individual
    #
    #         is_social_worker_program = obj_hct.program.is_social_worker_program
    #
    #         if is_social_worker_program:
    #             # every household for Social DCT type program has HoH
    #             household.head_of_household = individual
    #         else:
    #             if imported_individual.relationship == HEAD and household:
    #                 household.head_of_household = individual
    #
    #         (
    #             documents,
    #             identities,
    #         ) = self._prepare_individual_documents_and_identities(imported_individual, individual)
    #
    #         documents_to_create.extend(documents)
    #         identities_to_create.extend(identities)
    #
    #

    def _create_grievance_ticket_for_delivery_mechanisms_errors(
        self, delivery_mechanism_data: DeliveryMechanismData, obj_hct: RegistrationDataImport, description: str
    ) -> Tuple[GrievanceTicket, TicketIndividualDataUpdateDetails]:
        comments = f"This is a system generated ticket for RDI {obj_hct}"
        grievance_ticket = GrievanceTicket(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=delivery_mechanism_data.individual.household.admin2,
            business_area=obj_hct.business_area,
            registration_data_import=obj_hct,
            description=description,
            comments=comments,
        )
        individual_data_with_approve_status = delivery_mechanism_data.get_grievance_ticket_payload_for_errors()
        individual_data_update_ticket = TicketIndividualDataUpdateDetails(
            individual_data={"delivery_mechanism_data_to_edit": [individual_data_with_approve_status]},
            individual=delivery_mechanism_data.individual,
            ticket=grievance_ticket,
        )

        return grievance_ticket, individual_data_update_ticket

    def _create_grievance_tickets_for_delivery_mechanisms_errors(
        self, delivery_mechanisms_data: QuerySet[PendingDeliveryMechanismData], obj_hct: RegistrationDataImport
    ) -> None:
        grievance_tickets_to_create = []
        individual_data_update_tickets_to_create = []
        for delivery_mechanism_data in delivery_mechanisms_data:
            delivery_mechanism_data.validate()
            if not delivery_mechanism_data.is_valid:
                description = (
                    f"Missing required fields {list(delivery_mechanism_data.validation_errors.keys())}"
                    f" values for delivery mechanism {delivery_mechanism_data.delivery_mechanism}"
                )
                (
                    grievance_ticket,
                    individual_data_update_ticket,
                ) = self._create_grievance_ticket_for_delivery_mechanisms_errors(
                    delivery_mechanism_data, obj_hct, description
                )
                grievance_tickets_to_create.append(grievance_ticket)
                individual_data_update_tickets_to_create.append(individual_data_update_ticket)

            else:
                delivery_mechanism_data.update_unique_field()
                if not delivery_mechanism_data.is_valid:
                    description = (
                        f"Fields not unique {list(delivery_mechanism_data.validation_errors.keys())} across program"
                        f" for delivery mechanism {delivery_mechanism_data.delivery_mechanism}, possible duplicate of {delivery_mechanism_data.possible_duplicate_of}"
                    )
                    (
                        grievance_ticket,
                        individual_data_update_ticket,
                    ) = self._create_grievance_ticket_for_delivery_mechanisms_errors(
                        delivery_mechanism_data, obj_hct, description
                    )
                    grievance_tickets_to_create.append(grievance_ticket)
                    individual_data_update_tickets_to_create.append(individual_data_update_ticket)
            delivery_mechanism_data.save()

        if grievance_tickets_to_create:
            GrievanceTicket.objects.bulk_create(grievance_tickets_to_create)
            TicketIndividualDataUpdateDetails.objects.bulk_create(individual_data_update_tickets_to_create)
            for grievance_ticket in grievance_tickets_to_create:
                grievance_ticket.programs.add(obj_hct.program)

            logger.info(
                f"RDI:{obj_hct} Created {len(grievance_tickets_to_create)} delivery mechanisms error grievance tickets"
            )

    def execute(self, registration_data_import_id: str) -> None:
        try:
            obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id)
            obj_hub = RegistrationDataImportDatahub.objects.get(hct_id=registration_data_import_id)
            households = PendingHousehold.objects.filter(registration_data_import=obj_hct)
            individuals = PendingIndividual.objects.filter(registration_data_import=obj_hct).order_by(
                "first_registration_date"
            )
            roles = PendingIndividualRoleInHousehold.objects.filter(
                household__in=households, individual__in=individuals
            )
            bank_account_infos = PendingBankAccountInfo.objects.filter(individual__in=individuals)
            delivery_mechanism_data = PendingDeliveryMechanismData.objects.filter(
                individual__in=individuals,
            )
            individual_ids = list(individuals.values_list("id", flat=True))
            household_ids = list(households.values_list("id", flat=True))
            try:
                with transaction.atomic(using="default"):
                    old_obj_hct = copy_model_object(obj_hct)

                    transaction.on_commit(lambda: recalculate_population_fields_task(household_ids, obj_hct.program_id))
                    logger.info(
                        f"RDI:{registration_data_import_id} Recalculated population fields for {len(household_ids)} households"
                    )
                    kobo_submissions = []
                    for household in households:
                        kobo_submission_uuid = household.kobo_submission_uuid
                        kobo_asset_id = household.detail_id or household.kobo_asset_id
                        kobo_submission_time = household.kobo_submission_time
                        if kobo_submission_uuid and kobo_asset_id and kobo_submission_time:
                            submission = KoboImportedSubmission(
                                kobo_submission_uuid=kobo_submission_uuid,
                                kobo_asset_id=kobo_asset_id,
                                kobo_submission_time=kobo_submission_time,
                                registration_data_import=obj_hub,
                                imported_household=household,
                            )
                            kobo_submissions.append(submission)
                    if kobo_submissions:
                        KoboImportedSubmission.objects.bulk_create(kobo_submissions)
                    logger.info(f"RDI:{registration_data_import_id} Created {len(kobo_submissions)} kobo submissions")

                    for household in households:
                        registration_id = household.registration_id
                        if registration_id:
                            self._update_program_registration_id(household.id, registration_id)

                    # DEDUPLICATION

                    populate_index(
                        PendingIndividual.objects.filter(registration_data_import=obj_hct),
                        get_individual_doc(obj_hct.business_area.slug),
                    )
                    logger.info(
                        f"RDI:{registration_data_import_id} Populated index for {len(individual_ids)} individuals"
                    )
                    populate_index(PendingHousehold.objects.filter(registration_data_import=obj_hct), HouseholdDocument)
                    logger.info(
                        f"RDI:{registration_data_import_id} Populated index for {len(household_ids)} households"
                    )
                    # if not obj_hct.business_area.postpone_deduplication:
                    # TODO: Deduplication to uncomment
                    # individuals = evaluate_qs(
                    #     Individual.objects.filter(registration_data_import=obj_hct)
                    #     .select_for_update()
                    #     .order_by("pk")
                    # )
                    # DeduplicateTask(
                    #     obj_hct.business_area.slug, obj_hct.program.id
                    # ).deduplicate_individuals_against_population(individuals)
                    # logger.info(f"RDI:{registration_data_import_id} Deduplicated {len(individual_ids)} individuals")
                    # golden_record_duplicates = Individual.objects.filter(
                    #     registration_data_import=obj_hct, deduplication_golden_record_status=DUPLICATE
                    # )
                    # logger.info(
                    #     f"RDI:{registration_data_import_id} Found {len(golden_record_duplicates)} duplicates"
                    # )
                    #
                    # create_needs_adjudication_tickets(
                    #     golden_record_duplicates,
                    #     "duplicates",
                    #     obj_hct.business_area,
                    #     registration_data_import=obj_hct,
                    # )
                    # logger.info(
                    #     f"RDI:{registration_data_import_id} Created tickets for {len(golden_record_duplicates)} duplicates"
                    # )
                    #
                    # needs_adjudication = Individual.objects.filter(
                    #     registration_data_import=obj_hct, deduplication_golden_record_status=NEEDS_ADJUDICATION
                    # )
                    # logger.info(
                    #     f"RDI:{registration_data_import_id} Found {len(needs_adjudication)} needs adjudication"
                    # )
                    #
                    # create_needs_adjudication_tickets(
                    #     needs_adjudication,
                    #     "possible_duplicates",
                    #     obj_hct.business_area,
                    #     registration_data_import=obj_hct,
                    # )
                    # logger.info(
                    #     f"RDI:{registration_data_import_id} Created tickets for {len(needs_adjudication)} needs adjudication"
                    # )

                    # SANCTION LIST CHECK
                    if obj_hct.should_check_against_sanction_list() and not obj_hct.business_area.screen_beneficiary:
                        logger.info(f"RDI:{registration_data_import_id} Checking against sanction list")
                        CheckAgainstSanctionListPreMergeTask.execute(registration_data_import=obj_hct)
                        logger.info(f"RDI:{registration_data_import_id} Checked against sanction list")

                    obj_hct.status = RegistrationDataImport.MERGED
                    obj_hct.save()

                    households.update(rdi_merge_status="MERGED")
                    individuals.update(rdi_merge_status="MERGED")
                    delivery_mechanism_data.update(rdi_merge_status="MERGED")
                    self._create_grievance_tickets_for_delivery_mechanisms_errors(delivery_mechanism_data, obj_hct)
                    roles.update(rdi_merge_status="MERGED")
                    bank_account_infos.update(rdi_merge_status="MERGED")
                    PendingDocument.objects.filter(individual_id__in=individual_ids).update(rdi_merge_status="MERGED")
                    PendingIndividualRoleInHousehold.objects.filter(individual_id__in=individual_ids).update(
                        rdi_merge_status="MERGED"
                    )

                    logger.info(f"RDI:{registration_data_import_id} Saved registration data import")
                    transaction.on_commit(lambda: deduplicate_documents.delay())
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

                # proactively try to remove also es data for imported individuals
                remove_elasticsearch_documents_by_matching_ids(
                    individual_ids,
                    get_imported_individual_doc(obj_hct.business_area.slug),
                )
                raise

            with contextlib.suppress(ConnectionError, AttributeError):
                for key in cache.keys("*"):
                    if key.startswith(
                        (
                            f"count_{obj_hub.business_area_slug}_HouseholdNodeConnection",
                            f"count_{obj_hub.business_area_slug}_IndividualNodeConnection",
                        )
                    ):
                        cache.delete(key)

        except Exception as e:
            logger.error(e)
            raise

    def _update_program_registration_id(self, household_id: UUID, registration_id: str) -> None:
        count = 0
        while PendingHousehold.objects.filter(registration_id=f"{registration_id}#{count}").exists():
            count += 1
        PendingHousehold.objects.filter(id=household_id).update(registration_id=f"{registration_id}#{count}")
