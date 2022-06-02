from django.db import transaction
from django_countries.fields import Country

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_DICT,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportedIndividual,
    ImportedHousehold,
    RegistrationDataImportDatahub,
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    DiiaIndividual,
    DiiaHousehold,
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
    def execute(self, registration_data_import_id):
        registration_data_import = RegistrationDataImportDatahub.objects.select_for_update().get(
            id=registration_data_import_id,
        )

        old_rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
        registration_data_import.import_done = RegistrationDataImportDatahub.STARTED
        registration_data_import.save()

        self._get_document_types()

        households_to_create = []
        households_to_update = []
        for household in registration_data_import.diia_households.all():
            household_obj = ImportedHousehold(
                consent=household.consent,
                address=household.address,
                registration_data_import=registration_data_import,
                first_registration_date=household.created_at,
                last_registration_date=household.created_at,
                diia_rec_id=household.rec_id,
                size=household.individuals.all().count(),
                country=Country("UA"),
            )

            individuals_to_create_list = []
            individuals_to_update_list = []
            head_of_household = None
            documents = []
            bank_accounts = []

            for individual in household.individuals.all():
                individual_obj = ImportedIndividual(
                    individual_id=individual.individual_id,
                    given_name=individual.first_name,
                    middle_name=individual.second_name,
                    family_name=individual.last_name,
                    full_name=f"{individual.first_name} {individual.last_name}",
                    relationship=individual.relationship,
                    sex=individual.sex,
                    birth_date=individual.birth_date,
                    marital_status=individual.marital_status,
                    disability=individual.disability,
                    registration_data_import=registration_data_import,
                    first_registration_date=individual.created_at,
                    last_registration_date=individual.created_at,
                    household=household_obj,
                )
                individuals_to_create_list.append(individual_obj)

                if individual.relationship == HEAD:
                    head_of_household = individual_obj

                    hh_doc = {
                        "type": individual.doc_type,
                        "document_number": f"{individual.doc_serie} {individual.doc_number}",
                        "doc_date": individual.doc_issue_date,
                        individual: individual_obj
                    }
                    self._add_hh_doc(hh_doc, documents)

                if individual.birth_doc:
                    self._add_birth_document(documents, individual, individual_obj)

                if individual.iban:
                    self._add_bank_account(bank_accounts, individual, individual_obj)

                individual.imported_individual = individual_obj
                individuals_to_update_list.append(individual)

            # create Individuals
            ImportedIndividual.objects.bulk_create(individuals_to_create_list)
            # update imported_individual
            DiiaIndividual.objects.bulk_update(individuals_to_update_list, ["imported_individual"], 1000)

            if household.vpo_doc:
                self._add_vpo_document(documents, head_of_household, household)

            ImportedDocument.objects.bulk_create(documents)
            ImportedBankAccountInfo.objects.bulk_create(bank_accounts)

            household_obj.head_of_household = head_of_household
            households_to_create.append(household_obj)

            household.imported_household = household_obj
            households_to_update.append(household)

        ImportedHousehold.objects.bulk_create(households_to_create)
        DiiaHousehold.objects.bulk_update(households_to_update, ["imported_household"], 1000)

        registration_data_import.import_done = RegistrationDataImportDatahub.DONE
        registration_data_import.save()

        rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
        rdi_mis.status = RegistrationDataImport.IN_REVIEW
        rdi_mis.save()
        log_create(RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, old_rdi_mis, rdi_mis)

        DeduplicateTask.deduplicate_imported_individuals(registration_data_import_datahub=registration_data_import)

    def _add_bank_account(self, bank_accounts, individual, individual_obj):
        bank_accounts.append(
            ImportedBankAccountInfo(
                individual=individual_obj,
                bank_name=individual.bank_name,
                bank_account_number=individual.iban.replace(" ", ""),
            )
        )

    def _add_vpo_document(self, documents, head_of_household, household):
        documents.append(
            ImportedDocument(
                document_number=household.vpo_doc_id,
                individual=head_of_household,
                type=self.other_document_type,
                photo=household.vpo_doc,
                doc_date=household.vpo_doc_date,
            )
        )

    def _add_birth_document(self, documents, individual, individual_obj):
        documents.append(
            ImportedDocument(
                document_number=individual.birth_doc,
                individual=individual_obj,
                type=self.birth_document_type,
            )
        )

    def _add_hh_doc(self, data, documents):
        # TODO: add more types maybe
        doc_type = self.national_passport_document_type if data.get("type") == "passport" else self.other_document_type

        documents.append(
            ImportedDocument(
                document_number=data.get("document_number"),
                individual=data.get("individual"),
                doc_date=data.get("doc_date"),
                type=doc_type,
            )
        )

    def _get_document_types(self):
        self.national_passport_document_type, _ = ImportedDocumentType.objects.get_or_create(
            country=Country("UA"),  # DiiaIndividual don't has issuing country
            label=IDENTIFICATION_TYPE_DICT.get(IDENTIFICATION_TYPE_NATIONAL_PASSPORT),
            type=IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
        )

        self.birth_document_type, _ = ImportedDocumentType.objects.get_or_create(
            country=Country("UA"),  # DiiaIndividual don't has issuing country
            label=IDENTIFICATION_TYPE_DICT.get(IDENTIFICATION_TYPE_BIRTH_CERTIFICATE),
            type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
        )
        self.other_document_type, _ = ImportedDocumentType.objects.get_or_create(
            country=Country("UA"),  # DiiaIndividual don't has issuing country
            label=IDENTIFICATION_TYPE_DICT.get(IDENTIFICATION_TYPE_OTHER),
            type=IDENTIFICATION_TYPE_OTHER,
        )
