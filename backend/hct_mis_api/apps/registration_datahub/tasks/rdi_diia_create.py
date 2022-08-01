import logging
import dateutil.parser

from django.db import transaction
from django_countries.fields import Country
from django.core.exceptions import ValidationError

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_DICT,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_TAX_ID,
    DISABLED,
    NOT_DISABLED,
    WIFE_HUSBAND,
    SON_DAUGHTER,
    RELATIONSHIP_UNKNOWN,
    MALE,
    FEMALE,
    YES,
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
    ImportData,
    DIIA_DISABLED,
    DIIA_RELATIONSHIP_HEAD,
    DIIA_RELATIONSHIP_SON,
    DIIA_RELATIONSHIP_DAUGHTER,
    DIIA_RELATIONSHIP_WIFE,
    DIIA_RELATIONSHIP_HUSBAND,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask


logger = logging.getLogger(__name__)


class RdiDiiaCreateTask:
    """
    Imports project data from DIIA models
    """

    DIIA_DISABILITY_MAP = {DIIA_DISABLED: DISABLED}
    DIIA_RELATION = {
        DIIA_RELATIONSHIP_HEAD: HEAD,
        DIIA_RELATIONSHIP_SON: SON_DAUGHTER,
        DIIA_RELATIONSHIP_DAUGHTER: SON_DAUGHTER,
        DIIA_RELATIONSHIP_WIFE: WIFE_HUSBAND,
        DIIA_RELATIONSHIP_HUSBAND: WIFE_HUSBAND,
    }
    DIIA_SEX_MAP = {
        "M": MALE,
        "F": FEMALE
    }

    def __init__(self):
        self.bank_accounts = []
        self.documents = []
        self.business_area = BusinessArea.objects.get(slug="ukraine")

    @transaction.atomic("default")
    @transaction.atomic("registration_datahub")
    def create_rdi(self, imported_by, rdi_name="rdi_name"):

        number_of_individuals = 0
        number_of_households = 0

        rdi = RegistrationDataImport.objects.create(
            name=rdi_name,
            data_source=RegistrationDataImport.DIIA,
            imported_by=imported_by,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            business_area=self.business_area,
            status=RegistrationDataImport.IMPORTING,
        )

        import_data = ImportData.objects.create(
            status=ImportData.STATUS_PENDING,
            business_area_slug=self.business_area.slug,
            data_type=ImportData.DIIA,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            created_by_id=imported_by.id if imported_by else None,
        )
        rdi_datahub = RegistrationDataImportDatahub.objects.create(
            name=rdi_name,
            hct_id=rdi.id,
            import_data=import_data,
            import_done=RegistrationDataImportDatahub.NOT_STARTED,
            business_area_slug=self.business_area.slug,
        )
        rdi.datahub_id = rdi_datahub.id
        rdi.save()
        return rdi

    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    def execute(self, registration_data_import_id, diia_hh_ids=None, diia_hh_count=None):
        if diia_hh_ids and diia_hh_count:
            raise ValueError("You can't set two args diia_hh_ids and diia_hh_count")

        if not diia_hh_ids:
            diia_household_import_ids = DiiaHousehold.objects.filter(status=DiiaHousehold.STATUS_TO_IMPORT).values_list(
                "id", flat=True
            )[:diia_hh_count]
        else:
            diia_household_import_ids = DiiaHousehold.objects.filter(
                status=DiiaHousehold.STATUS_TO_IMPORT, id__in=diia_hh_ids
            ).values_list("id", flat=True)

        rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import_id)

        registration_data_import_data_hub = RegistrationDataImportDatahub.objects.select_for_update().get(
            id=rdi_mis.datahub_id,
        )

        if not diia_household_import_ids:
            rdi_mis.delete()
            registration_data_import_data_hub.import_data.delete()
            registration_data_import_data_hub.delete()
            raise ValidationError("Rdi doesn't found any records within status to import")

        registration_data_import_data_hub.import_done = RegistrationDataImportDatahub.STARTED
        registration_data_import_data_hub.save()

        self._get_document_types()

        households_to_create = []
        households_to_update = []
        individual_count = 0

        for diia_household_id in diia_household_import_ids:
            diia_household = DiiaHousehold.objects.defer("source_data").get(id=diia_household_id)
            try:
                all_individuals = DiiaIndividual.objects.filter(rec_id=diia_household.rec_id)
                household_obj = ImportedHousehold(
                    consent=diia_household.consent,
                    address=diia_household.address,
                    registration_data_import=registration_data_import_data_hub,
                    first_registration_date=registration_data_import_data_hub.created_at,
                    last_registration_date=registration_data_import_data_hub.created_at,
                    collect_individual_data=YES,
                    diia_rec_id=diia_household.rec_id,
                    size=all_individuals.count(),
                    country=Country("UA"),
                )

                # if True ignore create HH and Individuals and set status 'STATUS_TAX_ID_ERROR'
                pass_hh_and_individuals_tax_id_error = False

                individuals_to_create_list = []
                individuals_to_update_list = []
                head_of_household = None
                self.bank_accounts = []
                self.documents = []
                individual_count += all_individuals.count()

                for individual in all_individuals:
                    if pass_hh_and_individuals_tax_id_error:
                        continue

                    # validate tax_id
                    if individual.individual_id and self.tax_id_exists(individual.individual_id.replace(" ", "")):
                        pass_hh_and_individuals_tax_id_error = True
                        individuals_to_create_list = []
                        individuals_to_update_list = []
                        head_of_household = None
                        individual_count -= all_individuals.count()
                        self.bank_accounts = []
                        self.documents = []
                        continue

                    b_date = (
                        dateutil.parser.parse(individual.birth_date, dayfirst=True) if individual.birth_date else ""
                    )

                    individual_obj = ImportedIndividual(
                        individual_id=individual.individual_id.replace(" ", "") if individual.individual_id else "",
                        given_name=individual.first_name,
                        middle_name=individual.second_name,
                        family_name=individual.last_name,
                        full_name=f"{individual.first_name} {individual.last_name}",
                        relationship=self.DIIA_RELATION.get(individual.relationship, RELATIONSHIP_UNKNOWN),
                        sex=self.DIIA_SEX_MAP.get(individual.sex, ""),
                        birth_date=b_date,
                        marital_status=individual.marital_status if individual.marital_status else "",
                        disability=self.DIIA_DISABILITY_MAP.get(individual.disability, NOT_DISABLED),
                        registration_data_import=registration_data_import_data_hub,
                        first_registration_date=registration_data_import_data_hub.created_at,
                        last_registration_date=registration_data_import_data_hub.created_at,
                        household=household_obj,
                    )
                    individuals_to_create_list.append(individual_obj)

                    if individual.relationship == HEAD:
                        head_of_household = individual_obj

                        hh_doc = {
                            "type": individual.doc_type,
                            "document_number": f"{individual.doc_serie} {individual.doc_number}",
                            "doc_date": dateutil.parser.parse(individual.doc_issue_date, dayfirst=True)
                            if individual.doc_issue_date
                            else None,
                            "individual": individual_obj,
                        }
                        self._add_hh_doc(hh_doc)

                    if individual.birth_doc:
                        self._add_birth_document(individual, individual_obj)

                    if individual.iban:
                        self._add_bank_account(individual, individual_obj)

                    if individual.individual_id:
                        self._add_tax_id_document(individual.individual_id.replace(" ", ""), individual_obj)

                    individual.imported_individual = individual_obj
                    individuals_to_update_list.append(individual)

                # create Individuals
                ImportedIndividual.objects.bulk_create(individuals_to_create_list)
                # update imported_individual
                DiiaIndividual.objects.bulk_update(individuals_to_update_list, ["imported_individual"], 1000)

                if diia_household.vpo_doc:
                    self._add_vpo_document(head_of_household, diia_household)

                ImportedDocument.objects.bulk_create(self.documents)
                ImportedBankAccountInfo.objects.bulk_create(self.bank_accounts)

                if not pass_hh_and_individuals_tax_id_error:
                    household_obj.head_of_household = head_of_household
                    households_to_create.append(household_obj)
                    diia_household.imported_household = household_obj

                    diia_household.registration_data_import = registration_data_import_data_hub
                    diia_household.status = DiiaHousehold.STATUS_IMPORTED
                    households_to_update.append(diia_household)

                else:
                    # STATUS_TAX_ID_ERROR
                    logger.error(f"Error importing DiiaHousehold {diia_household.pk}, duplicate Tax ID.")
                    diia_household.registration_data_import = registration_data_import_data_hub
                    diia_household.status = DiiaHousehold.STATUS_TAX_ID_ERROR
                    households_to_update.append(diia_household)
                    print(f"Error importing DiiaHousehold {diia_household.pk}, duplicate Tax ID.  <<")

            except Exception as e:
                logger.exception(f"Error importing DiiaHousehold {diia_household.pk}. {e}")
                diia_household.status = DiiaHousehold.STATUS_ERROR
                households_to_update.append(diia_household)

        ImportedHousehold.objects.bulk_create(households_to_create)
        DiiaHousehold.objects.bulk_update(
            households_to_update, ["imported_household", "status", "registration_data_import"], 1000
        )

        registration_data_import_data_hub.import_done = RegistrationDataImportDatahub.DONE
        registration_data_import_data_hub.save()

        registration_data_import_data_hub.import_data.number_of_individuals = individual_count
        registration_data_import_data_hub.import_data.number_of_households = len(households_to_create)
        registration_data_import_data_hub.import_data.status = ImportData.STATUS_FINISHED
        registration_data_import_data_hub.import_data.save()

        rdi_mis.status = RegistrationDataImport.IN_REVIEW
        rdi_mis.number_of_individuals = individual_count
        rdi_mis.number_of_households = len(households_to_create)
        rdi_mis.save()
        log_create(RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, rdi_mis, rdi_mis)
        if not rdi_mis.business_area.postpone_deduplication:
            DeduplicateTask.deduplicate_imported_individuals(
                registration_data_import_datahub=registration_data_import_data_hub
            )

    def _add_bank_account(self, individual, individual_obj):
        self.bank_accounts.append(
            ImportedBankAccountInfo(
                individual=individual_obj,
                bank_name=individual.bank_name,
                bank_account_number=individual.iban.replace(" ", ""),
            )
        )

    def _add_vpo_document(self, head_of_household, household):
        vpo_doc_date = dateutil.parser.parse(household.vpo_doc_date)

        self.documents.append(
            ImportedDocument(
                document_number=household.vpo_doc_id,
                individual=head_of_household,
                type=self.other_document_type,
                photo=household.vpo_doc,
                doc_date=vpo_doc_date,
            )
        )

    def _add_birth_document(self, individual, individual_obj):
        self.documents.append(
            ImportedDocument(
                document_number=individual.birth_doc,
                individual=individual_obj,
                type=self.birth_document_type,
            )
        )

    def _add_hh_doc(self, data):
        # TODO: add more types maybe
        doc_type = self.national_passport_document_type if data.get("type") == "passport" else self.other_document_type

        self.documents.append(
            ImportedDocument(
                document_number=data.get("document_number"),
                individual=data.get("individual"),
                doc_date=data.get("doc_date"),
                type=doc_type,
            )
        )

    def _add_tax_id_document(self, tax_id, individual_obj):
        self.documents.append(
            ImportedDocument(
                document_number=tax_id,
                individual=individual_obj,
                type=self.tax_id_document_type,
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
        self.tax_id_document_type, _ = ImportedDocumentType.objects.get_or_create(
            country=Country("UA"),  # DiiaIndividual don't has issuing country
            label=IDENTIFICATION_TYPE_DICT.get(IDENTIFICATION_TYPE_TAX_ID),
            type=IDENTIFICATION_TYPE_TAX_ID,
        )

    def tax_id_exists(self, tax_id):
        # TODO ??
        # Document.objects.filter(document_number=tax_id, type=self.tax_id_document_type).exists()
        return ImportedDocument.objects.filter(document_number=tax_id, type=self.tax_id_document_type).exists()
