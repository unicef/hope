from django.db import transaction

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    HEAD
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportedIndividual,
    ImportedHousehold,
    RegistrationDataImportDatahub,
    ImportData, ImportedBankAccountInfo, ImportedDocument,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.registration_datahub.tasks.rdi_base_create import RdiBaseCreateTask


class RdiDiiaCreateTask(RdiBaseCreateTask):
    """
    Imports project data from DIIA models
    """

    business_area = BusinessArea.objects.get(slug="ukraine")

    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    def execute(self, registration_data_import_id, import_data_id):
        registration_data_import = RegistrationDataImportDatahub.objects.select_for_update().get(
            id=registration_data_import_id,
        )


        old_rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
        registration_data_import_mis = old_rdi_mis
        registration_data_import_datahub = registration_data_import
        registration_data_import.import_done = RegistrationDataImportDatahub.STARTED
        registration_data_import.save()

        import_data = ImportData.objects.get(id=import_data_id)

        head_of_households_mapping = {}
        households_to_create = []
        individuals_to_create_list = []
        individuals_to_create = {}

        for household in registration_data_import.diia_households.all():  # maybe add filter by imported_household__isnull=True


            household_obj = ImportedHousehold(
                consent=household.consent,
                address=household.address,
                # TODO: need add this new fields for Diia import
                diia_rec_id=household.rec_id,  # ?
                diia_vpo_doc=household.vpo_doc,  # ?
                diia_vpo_doc_id=household.vpo_doc_id,  # ?
                diia_vpo_doc_date=household.diia_vpo_doc_date,  # ?

                registration_data_import=registration_data_import,
                first_registration_date = household.created_at,
                last_registration_date = household.created_at
                # head_of_household

            )

            for individual in household.individuals.all():
                individual_obj = ImportedIndividual(
                    individual_id=individual.individual_id,
                    given_name=individual.first_name,
                    middle_name=individual.second_name,
                    family_name=individual.last_name,
                    relationship=individual.relationship,
                    sex=individual.sex,
                    birth_date=individual.birth_date,
                    marital_status=individual.marital_status,
                    disability=individual.disability,
                    # household=household_obj,

                )
                if individual.relationship == HEAD:
                    head_of_households_mapping[household_obj] = individual_obj

                # if individual.birth_doc create ImportedDocument
                ImportedDocument(
                )

                # if individual.iban and create ImportedBankAccountInfo
                ImportedBankAccountInfo(
                )


            household_obj.first_registration_date = household.created_at
            household_obj.last_registration_date = household.registration_date
            household_obj.registration_data_import = registration_data_import
            household_obj = self._assign_admin_areas_titles(household_obj)
            households_to_create.append(household_obj)

            ImportedIndividual.objects.bulk_create(individuals_to_create_list)

        ImportedHousehold.objects.bulk_create(households_to_create)

        households_to_update = []
        for household, individual in head_of_households_mapping.items():
            household.head_of_household = individual
            households_to_update.append(household)
        ImportedHousehold.objects.bulk_update(
            households_to_update,
            ["head_of_household"],
            1000,
        )
        registration_data_import.import_done = RegistrationDataImportDatahub.DONE
        registration_data_import.save()

        rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
        rdi_mis.status = RegistrationDataImport.IN_REVIEW
        rdi_mis.save()
        log_create(RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, old_rdi_mis, rdi_mis)

        DeduplicateTask.deduplicate_imported_individuals(registration_data_import_datahub=registration_data_import)
