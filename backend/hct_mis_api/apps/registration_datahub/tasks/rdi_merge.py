from django.db import transaction
from django.forms import model_to_dict

from core.models import AdminArea
from household.elasticsearch_utils import rebuild_search_index
from household.models import (
    Document,
    DocumentType,
    HEAD,
    IndividualIdentity,
    IndividualRoleInHousehold,
    Agency,
    DUPLICATE,
    NEEDS_ADJUDICATION,
)
from household.models import Household
from household.models import Individual
from registration_data.models import RegistrationDataImport
from registration_datahub.models import (
    RegistrationDataImportDatahub,
    ImportedHousehold,
    ImportedIndividualRoleInHousehold,
    ImportedIndividual,
)
from registration_datahub.tasks.deduplicate import DeduplicateTask
from sanction_list.tasks.check_against_sanction_list_pre_merge import CheckAgainstSanctionListPreMergeTask


class RdiMergeTask:
    HOUSEHOLD_FIELDS = (
        "consent",
        "residence_status",
        "country_origin",
        "size",
        "address",
        "country",
        "female_age_group_0_5_count",
        "female_age_group_6_11_count",
        "female_age_group_12_17_count",
        "female_adults_count",
        "pregnant_count",
        "male_age_group_0_5_count",
        "male_age_group_6_11_count",
        "male_age_group_12_17_count",
        "male_adults_count",
        "female_age_group_0_5_disabled_count",
        "female_age_group_6_11_disabled_count",
        "female_age_group_12_17_disabled_count",
        "female_adults_disabled_count",
        "male_age_group_0_5_disabled_count",
        "male_age_group_6_11_disabled_count",
        "male_age_group_12_17_disabled_count",
        "male_adults_disabled_count",
        "first_registration_date",
        "last_registration_date",
        "flex_fields",
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
    )

    def merge_admin_area(
        self, imported_household, household,
    ):
        admin1 = imported_household.admin1
        admin2 = imported_household.admin2
        try:
            if admin2 is not None:
                admin_area = AdminArea.objects.get(title=admin2)
                household.admin_area = admin_area
                return
            if admin1 is not None:
                admin_area = AdminArea.objects.get(title=admin1)
                household.admin_area = admin_area
                return
        except AdminArea.DoesNotExist:
            print("does not exist")

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
                country=imported_document.type.country, type=imported_document.type.type,
            )
            document = Document(
                document_number=imported_document.document_number, type=document_type, individual=individual,
            )
            documents_to_create.append(document)
        identities_to_create = []
        for imported_identity in imported_individual.identities.all():
            agency, _ = Agency.objects.get_or_create(
                type=imported_identity.agency.type, label=imported_identity.agency.label,
            )
            identity = IndividualIdentity(
                agency=agency, number=imported_identity.document_number, individual=individual,
            )
            identities_to_create.append(identity)

        return documents_to_create, identities_to_create

    def _prepare_individuals(self, imported_individuals, households_dict, obj_hct):
        individuals_dict = {}
        documents_to_create = []
        identities_to_create = []
        for imported_individual in imported_individuals:
            values = model_to_dict(imported_individual, fields=self.INDIVIDUAL_FIELDS)
            household = households_dict.get(imported_individual.household.id)

            individual = Individual(**values, household=household, registration_data_import=obj_hct)
            individuals_dict[imported_individual.id] = individual
            if imported_individual.relationship == HEAD and household:
                household.head_of_household = individual

            (documents, identities,) = self._prepare_individual_documents_and_identities(
                imported_individual, individual
            )

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

    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    def execute(self, registration_data_import_id):
        obj_hub = RegistrationDataImportDatahub.objects.get(hct_id=registration_data_import_id,)
        obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id,)
        imported_households = ImportedHousehold.objects.filter(registration_data_import=obj_hub)
        imported_individuals = ImportedIndividual.objects.order_by("first_registration_date").filter(
            registration_data_import=obj_hub
        )

        imported_roles = ImportedIndividualRoleInHousehold.objects.filter(
            household__in=imported_households, individual__in=imported_individuals,
        )

        households_dict = self._prepare_households(imported_households, obj_hct)
        (individuals_dict, documents_to_create, identities_to_create,) = self._prepare_individuals(
            imported_individuals, households_dict, obj_hct
        )

        roles_to_create = self._prepare_roles(imported_roles, households_dict, individuals_dict)

        Household.objects.bulk_create(households_dict.values())
        Individual.objects.bulk_create(individuals_dict.values())
        Document.objects.bulk_create(documents_to_create)
        IndividualIdentity.objects.bulk_create(identities_to_create)
        IndividualRoleInHousehold.objects.bulk_create(roles_to_create)

        # DEDUPLICATION
        rebuild_search_index()

        DeduplicateTask.deduplicate_individuals(registration_data_import=obj_hct)

        duplicates = Individual.objects.filter(registration_data_import=obj_hct, deduplication_status=DUPLICATE)

        for individual in duplicates:
            for duplicate in individual.deduplication_results["duplicates"]:
                # TODO: Grievance
                print(f"Individual: {individual.id} is duplicate for Individual: {duplicate.get('hit_id')}")

        needs_adjudication = Individual.objects.filter(
            registration_data_import=obj_hct, deduplication_status=NEEDS_ADJUDICATION
        )
        for individual in needs_adjudication:
            for possible_duplicate in individual.deduplication_results["possible_duplicates"]:
                # TODO: Grievance
                print(
                    f"Individual: {individual.id} is possible duplicate for "
                    f"Individual: {possible_duplicate.get('hit_id')}"
                )

        # SANCTION LIST CHECK
        CheckAgainstSanctionListPreMergeTask.execute()

        obj_hct.status = RegistrationDataImport.MERGED
        obj_hct.save()
