import logging
from django.db import transaction
from django.forms import model_to_dict

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.models import AdminArea
from hct_mis_api.apps.grievance.common import create_needs_adjudication_tickets
from hct_mis_api.apps.household.documents import IndividualDocument
from hct_mis_api.apps.household.elasticsearch_utils import populate_index, remove_document_by_matching_ids
from hct_mis_api.apps.household.models import (
    Document,
    DocumentType,
    HEAD,
    IndividualIdentity,
    IndividualRoleInHousehold,
    Agency,
    DUPLICATE,
    NEEDS_ADJUDICATION,
)
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    RegistrationDataImportDatahub,
    ImportedHousehold,
    ImportedIndividualRoleInHousehold,
    ImportedIndividual,
    KoboImportedSubmission,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    CheckAgainstSanctionListPreMergeTask,
)

logger = logging.getLogger(__name__)


class RdiMergeTask:
    HOUSEHOLD_FIELDS = (
        "consent_sign",
        "consent",
        "consent_sharing",
        "residence_status",
        "country_origin",
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
    )

    def merge_admin_area(
        self,
        imported_household,
        household,
    ):
        admin1 = imported_household.admin1
        admin2 = imported_household.admin2
        try:
            if admin2 is not None:
                admin_area = AdminArea.objects.filter(p_code=admin2).first()
                household.admin_area = admin_area
                return
            if admin1 is not None:
                admin_area = AdminArea.objects.filter(p_code=admin1).first()
                household.admin_area = admin_area
                return
        except AdminArea.DoesNotExist as e:
            logger.exception(e)

    def _prepare_households(self, imported_households, obj_hct):
        households_dict = {}
        business_area = obj_hct.business_area
        for imported_household in imported_households:
            household = Household(
                **model_to_dict(imported_household, fields=self.HOUSEHOLD_FIELDS),
                registration_data_import=obj_hct,
                business_area=business_area,
            )
            self.merge_admin_area(imported_household, household)
            households_dict[imported_household.id] = household

        return households_dict

    def _prepare_individual_documents_and_identities(self, imported_individual, individual):
        documents_to_create = []
        for imported_document in imported_individual.documents.all():
            document_type, _ = DocumentType.objects.get_or_create(
                country=imported_document.type.country,
                type=imported_document.type.type,
            )
            document = Document(
                document_number=imported_document.document_number,
                type=document_type,
                individual=individual,
            )
            documents_to_create.append(document)
        identities_to_create = []
        for imported_identity in imported_individual.identities.all():
            agency, _ = Agency.objects.get_or_create(
                type=imported_identity.agency.type,
                country=imported_identity.agency.country,
                label=imported_identity.agency.label,
            )
            identity = IndividualIdentity(
                agency=agency,
                number=imported_identity.document_number,
                individual=individual,
            )
            identities_to_create.append(identity)

        return documents_to_create, identities_to_create

    def _prepare_individuals(self, imported_individuals, households_dict, obj_hct):
        individuals_dict = {}
        documents_to_create = []
        identities_to_create = []
        for imported_individual in imported_individuals:
            values = model_to_dict(imported_individual, fields=self.INDIVIDUAL_FIELDS)
            imported_individual_household = imported_individual.household
            household = households_dict.get(imported_individual.household.id) if imported_individual_household else None
            individual = Individual(
                **values,
                household=household,
                business_area=obj_hct.business_area,
                registration_data_import=obj_hct,
                imported_individual_id=imported_individual.id,
            )
            individuals_dict[imported_individual.id] = individual
            if imported_individual.relationship == HEAD and household:
                household.head_of_household = individual

            (
                documents,
                identities,
            ) = self._prepare_individual_documents_and_identities(imported_individual, individual)

            documents_to_create.extend(documents)
            identities_to_create.extend(identities)

        return individuals_dict, documents_to_create, identities_to_create

    def _prepare_roles(self, imported_roles, households_dict, individuals_dict):
        roles_to_create = []
        for imported_role in imported_roles:
            role = IndividualRoleInHousehold(
                household=households_dict.get(imported_role.household.id),
                individual=individuals_dict.get(imported_role.individual.id),
                role=imported_role.role,
            )
            roles_to_create.append(role)

        return roles_to_create

    def execute(self, registration_data_import_id):
        individual_ids = []
        try:
            with transaction.atomic(using="default"):
                with transaction.atomic(using="registration_datahub"):
                    obj_hub = RegistrationDataImportDatahub.objects.get(
                        hct_id=registration_data_import_id,
                    )
                    obj_hct = RegistrationDataImport.objects.get(
                        id=registration_data_import_id,
                    )
                    old_obj_hct = copy_model_object(obj_hct)
                    imported_households = ImportedHousehold.objects.filter(registration_data_import=obj_hub)
                    imported_individuals = ImportedIndividual.objects.order_by("first_registration_date").filter(
                        registration_data_import=obj_hub
                    )

                    imported_roles = ImportedIndividualRoleInHousehold.objects.filter(
                        household__in=imported_households,
                        individual__in=imported_individuals,
                    )

                    households_dict = self._prepare_households(imported_households, obj_hct)
                    (
                        individuals_dict,
                        documents_to_create,
                        identities_to_create,
                    ) = self._prepare_individuals(imported_individuals, households_dict, obj_hct)

                    roles_to_create = self._prepare_roles(imported_roles, households_dict, individuals_dict)
                    Household.objects.bulk_create(households_dict.values())
                    Individual.objects.bulk_create(individuals_dict.values())
                    Document.objects.bulk_create(documents_to_create)
                    IndividualIdentity.objects.bulk_create(identities_to_create)
                    IndividualRoleInHousehold.objects.bulk_create(roles_to_create)
                    individual_ids = [str(individual.id) for individual in individuals_dict.values()]

                    kobo_submissions = []
                    for imported_household in imported_households:
                        kobo_submission_uuid = imported_household.kobo_submission_uuid
                        kobo_asset_id = imported_household.kobo_asset_id
                        kobo_submission_time = imported_household.kobo_submission_time
                        if kobo_submission_uuid and kobo_asset_id and kobo_submission_time:
                            submission = KoboImportedSubmission(
                                kobo_submission_uuid=kobo_submission_uuid,
                                kobo_asset_id=kobo_asset_id,
                                kobo_submission_time=kobo_submission_time,
                            )
                            kobo_submissions.append(submission)
                    if kobo_submissions:
                        KoboImportedSubmission.objects.bulk_create(kobo_submissions)

                    # DEDUPLICATION

                    populate_index(Individual.objects.filter(registration_data_import=obj_hct), IndividualDocument)

                    DeduplicateTask.deduplicate_individuals(registration_data_import=obj_hct)

                    golden_record_duplicates = Individual.objects.filter(
                        registration_data_import=obj_hct, deduplication_golden_record_status=DUPLICATE
                    )

                    create_needs_adjudication_tickets(golden_record_duplicates, "duplicates", obj_hct.business_area)

                    needs_adjudication = Individual.objects.filter(
                        registration_data_import=obj_hct, deduplication_golden_record_status=NEEDS_ADJUDICATION
                    )

                    create_needs_adjudication_tickets(needs_adjudication, "possible_duplicates", obj_hct.business_area)

                    # SANCTION LIST CHECK
                    CheckAgainstSanctionListPreMergeTask.execute()

                    obj_hct.status = RegistrationDataImport.MERGED
                    obj_hct.save()
                    DeduplicateTask.hard_deduplicate_documents(documents_to_create)
                    log_create(RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, old_obj_hct, obj_hct)
        except:
            remove_document_by_matching_ids(individual_ids, IndividualDocument)
            raise
