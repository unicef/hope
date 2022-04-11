import base64
import json
import uuid
from typing import List

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.forms import modelform_factory

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import build_arg_dict_from_dict
from hct_mis_api.apps.household.models import (
    DISABLED,
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_DRIVERS_LICENSE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO,
    IDENTIFICATION_TYPE_TAX_ID,
    NOT_DISABLED,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    rdi_deduplication_task,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    Record,
    RegistrationDataImportDatahub,
)


class UkrainianRegistrationService:
    INDIVIDUAL_MAPPING_DICT = {
        "given_name": "given_name_i_c",
        "family_name": "family_name_i_c",
        "middle_name": "patronymic",
        "birth_date": "birth_date",
        "sex": "gender_i_c",
        "relationship": "relationship_i_c",
        "disability": "disability_i_c",
        "disability_certificate_picture": "disability_certificate_picture",
        "phone_no": "phone_no_i_c",
        "role": "role_i_c",
    }

    HOUSEHOLD_MAPPING_DICT = {
        "residence_status": "residence_status_h_c",
        "admin1": "admin1_h_c",
        "admin2": "admin2_h_c",
        "size": "size_h_c",
        # "where_are_you_now": "",
    }
    DOCUMENT_MAPPING_TYPE_DICT = {
        IDENTIFICATION_TYPE_NATIONAL_ID: ("national_id_no_i_c_1", "national_id_picture"),
        IDENTIFICATION_TYPE_NATIONAL_PASSPORT: ("international_passport_i_c", "international_passport_picture"),
        IDENTIFICATION_TYPE_DRIVERS_LICENSE: ("drivers_license_no_i_c", "drivers_license_picture"),
        IDENTIFICATION_TYPE_BIRTH_CERTIFICATE: ("birth_certificate_no_i_c", "birth_certificate_picture"),
        IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO: ("residence_permit_no_i_c", "residence_permit_picture"),
        IDENTIFICATION_TYPE_TAX_ID: ("tax_id_no_i_c", "tax_id_picture"),
    }

    def __init__(self, records: QuerySet[Record]):
        self.records = records

    @atomic("default")
    @atomic("registration_datahub")
    def create_rdi(self, imported_by, rdi_name="rdi_name"):
        business_area = BusinessArea.objects.get(slug="ukraine")
        number_of_individuals = 0
        number_of_households = self.records.count()

        rdi = RegistrationDataImport.objects.create(
            name=rdi_name,
            data_source=RegistrationDataImport.FLEX_REGISTRATION,
            imported_by=imported_by,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            business_area=business_area,
            status=RegistrationDataImport.IMPORTING,
        )

        import_data = ImportData.objects.create(
            status=ImportData.STATUS_PENDING,
            business_area_slug=business_area.slug,
            data_type=ImportData.FLEX_REGISTRATION,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            created_by_id=imported_by.id,
        )
        rdi_datahub = RegistrationDataImportDatahub.objects.create(
            name=rdi_name,
            hct_id=rdi.id,
            import_data=import_data,
            import_done=RegistrationDataImportDatahub.NOT_STARTED,
            business_area_slug=business_area.slug,
        )

        for record in self.records:
            try:
                number_of_individuals += self.create_household_for_rdi_household(record, rdi_datahub)
            except ValidationError as e:
                raise ValidationError({f"Record id: {record.id}": [str(e)]})

        rdi.number_of_individuals = number_of_individuals
        import_data.number_of_individuals = number_of_individuals
        rdi.status = RegistrationDataImport.DEDUPLICATION
        rdi.save()
        rdi_deduplication_task.delay(rdi_datahub.id)
        import_data.save(update_fields=("number_of_individuals",))
        return rdi

    def create_household_for_rdi_household(
        self, record: Record, registration_data_import: RegistrationDataImportDatahub
    ):
        individuals: List[ImportedIndividual] = []
        documents: List[ImportedDocument] = []
        record_data_dict = json.loads(record.storage.tobytes().decode("utf-8"))
        household_dict = record_data_dict.get("household", [])[0]
        individuals_array = record_data_dict.get("individuals", [])

        self.validate_household(individuals_array)

        household_data = self._prepare_household_data(household_dict, record, registration_data_import)
        household = self._create_object_and_validate(household_data, ImportedHousehold)

        for index, individual_dict in enumerate(individuals_array):
            try:
                individual_data = self._prepare_individual_data(individual_dict, household, registration_data_import)
                role = individual_data.pop("role")
                individual = self._create_object_and_validate(individual_data, ImportedIndividual)
                individual.disability_certificate_picture = individual_data.get("disability_certificate_picture")
                individual.save()
                bank_account_data = self._prepare_bank_account_info(individual_dict, individual)
                if bank_account_data:
                    self._create_object_and_validate(bank_account_data, ImportedBankAccountInfo)
                self._create_role(role, individual, household)
                individuals.append(individual)

                if individual.relationship == HEAD:
                    household.head_of_household = individual
                    household.save(update_fields=("head_of_household",))
                documents.extend(self._prepare_documents(individual_dict, individual))
            except ValidationError as e:
                raise ValidationError({f"individual nr {index+1}": [str(e)]})

        record.registration_data_import = registration_data_import
        record.save(update_fields=("registration_data_import",))
        ImportedDocument.objects.bulk_create(documents)
        return len(individuals)

    def _create_role(self, role, individual, household):
        if role == "y":
            defaults = dict(individual=individual, household=household)
            if ImportedIndividualRoleInHousehold.objects.filter(household=household, role=ROLE_PRIMARY).count() == 0:
                ImportedIndividualRoleInHousehold.objects.create(**defaults, role=ROLE_PRIMARY)
            elif (
                ImportedIndividualRoleInHousehold.objects.filter(household=household, role=ROLE_ALTERNATE).count() == 0
            ):
                ImportedIndividualRoleInHousehold.objects.create(**defaults, role=ROLE_ALTERNATE)
            else:
                raise ValidationError("There should be only two collectors!")

    def _create_object_and_validate(self, data, model_class):
        ModelClassForm = modelform_factory(model_class, fields=data.keys())
        form = ModelClassForm(data)
        if not form.is_valid():
            raise ValidationError(form.errors)
        return form.save()

    def _prepare_household_data(self, household_dict, record, registration_data_import) -> dict:
        household_data = dict(
            **build_arg_dict_from_dict(household_dict, UkrainianRegistrationService.HOUSEHOLD_MAPPING_DICT),
            flex_registrations_record=record,
            registration_data_import=registration_data_import,
            first_registration_date=record.timestamp,
            last_registration_date=record.timestamp,
        )

        if residence_status := household_data.get("residence_status"):
            household_data["residence_status"] = residence_status.upper()

        return household_data

    def _prepare_individual_data(
        self,
        individual_dict: dict,
        household: ImportedHousehold,
        registration_data_import: RegistrationDataImportDatahub,
    ) -> dict:
        individual_data = dict(
            **build_arg_dict_from_dict(individual_dict, UkrainianRegistrationService.INDIVIDUAL_MAPPING_DICT),
            household=household,
            registration_data_import=registration_data_import,
            first_registration_date=household.first_registration_date,
            last_registration_date=household.last_registration_date,
        )
        disability = individual_data.get("disability", "n")
        if disability == "y":
            individual_data["disability"] = DISABLED
        else:
            individual_data["disability"] = NOT_DISABLED

        if relationship := individual_data.get("relationship"):
            individual_data["relationship"] = relationship.upper()
        if sex := individual_data.get("sex"):
            individual_data["sex"] = sex.upper()

        if phone_no := individual_data.get("phone_no"):
            if phone_no.startswith("0") and not phone_no.startswith("00"):
                phone_no = phone_no[1:]
            if not phone_no.startswith("+380"):
                individual_data["phone_no"] = f"+380{phone_no}"

        if disability_certificate_picture := individual_data.get("disability_certificate_picture"):
            certificate_picture = f"CERTIFICATE_PICTURE_{uuid.uuid4()}"
            disability_certificate_picture = self._prepare_picture_from_base64(
                disability_certificate_picture, certificate_picture
            )
            individual_data["disability_certificate_picture"] = disability_certificate_picture

        given_name = individual_data.get("given_name")
        middle_name = individual_data.get("middle_name")
        family_name = individual_data.get("family_name")

        individual_data["full_name"] = " ".join(filter(None, [given_name, middle_name, family_name]))

        return individual_data

    def _prepare_documents(self, individual_dict: dict, individual: ImportedIndividual) -> List[ImportedDocument]:
        documents = []

        for document_type_string, (
            document_number_field_name,
            picture_field_name,
        ) in UkrainianRegistrationService.DOCUMENT_MAPPING_TYPE_DICT.items():
            document_number = individual_dict.get(document_number_field_name)
            certificate_picture = individual_dict.get(picture_field_name, "")

            if not document_number and not certificate_picture:
                continue

            document_number = document_number or f"NOT_VALID_NUMBER_{uuid.uuid4()}"

            certificate_picture = self._prepare_picture_from_base64(certificate_picture, document_number)

            document_type = ImportedDocumentType.objects.get(type=document_type_string, country="UA")
            document = ImportedDocument(
                type=document_type,
                document_number=document_number,
                photo=certificate_picture,
                individual=individual,
            )
            documents.append(document)

        return documents

    def _prepare_picture_from_base64(self, certificate_picture, document_number):
        if certificate_picture:
            format_image = "jpg"
            certificate_picture = ContentFile(
                base64.b64decode(certificate_picture), name=f"{document_number}.{format_image}"
            )
        return certificate_picture

    def _prepare_bank_account_info(self, individual_dict: dict, individual: ImportedIndividual):
        if individual_dict.get("bank_account_h_f", "n") != "y":
            return
        bank_name = individual_dict.get("bank_name_h_f", "")
        other_bank_name = individual_dict.get("other_bank_name", "")
        if not bank_name:
            bank_name = other_bank_name
        bank_account_info_data = {
            "bank_account_number": individual_dict.get("bank_account_number", ""),
            "bank_name": bank_name,
            "debit_card_number": individual_dict.get("bank_account_number", ""),
            "individual": individual,
        }
        return bank_account_info_data

    def validate_household(self, individuals_array):
        if not individuals_array:
            raise ValidationError("Household should has at least one individual")

        has_head = False
        for individual_data in individuals_array:
            if individual_data.get("relationship_i_c") == "head":
                has_head = True
                break
        if not has_head:
            raise ValidationError("Household should has at least one Head of Household")
