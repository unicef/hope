import copy
import logging
from typing import Any

from hope.apps.core.utils import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
)
from hope.apps.household.const import (
    HEAD,
    ROLE_PRIMARY,
)
from hope.contrib.aurora.services.generic_registration_service import (
    GenericRegistrationService,
    mergedicts,
)
from hope.models import (
    Account,
    Country,
    Document,
    DocumentType,
    FinancialInstitutionMapping,
    FinancialServiceProvider,
    PendingAccount,
    PendingDocument,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
    RegistrationDataImport,
)

logger = logging.getLogger(__name__)


class NigeriaPeopleRegistrationService(GenericRegistrationService):
    DUPLICATE_ACCOUNT_NUMBER_REASON = "Duplicate account number in Nigeria Aurora registration"
    DUPLICATE_NATIONAL_ID_REASON = "Duplicate national id in Nigeria Aurora registration"
    DEFAULT_MAPPING = {
        "defaults": {
            "individuals_key": "individual-details",
            "households_key": "household-info",
            "intro_data_key": "intro-and-consent",
            "account_key": "account_details",
            "country": "NG",
        },
        "intro-and-consent": {
            "enumerator_code": "household.flex_fields",
            "who_to_register": "household.flex_fields",
        },
        "household-info": {
            "admin1_h_c": "household.admin1",
            "admin2_h_c": "household.admin2",
            "admin3_h_c": "household.admin3",
            "admin4_h_c": "household.admin4",
        },
        "individual-details": {
            "given_name_i_c": "individual.given_name",
            "family_name_i_c": "individual.family_name",
            "middle_name_i_c": "individual.middle_name",
            "birth_date_i_c": "individual.birth_date",
            "gender_i_c": "individual.sex",
            "email_i_c": "individual.email",
            "phone_no_i_c": "individual.phone_no",
            "estimated_birth_date_i_c": "individual.estimated_birth_date",
            "account_details": "account_details.data",
            "photo_i_c": "individual.photo",
            "national_id_photo_i_c": "document.doc_national-photo",
            "national_id_no_i_c": "document.doc_national-document_number",
        },
    }

    @classmethod
    def get_mapping(cls, registration_mapping: dict | None) -> dict:
        return mergedicts(copy.deepcopy(cls.DEFAULT_MAPPING), registration_mapping or {}, [])

    @classmethod
    def _get_account_number_from_account_data(cls, account_data: dict) -> str:
        data = account_data.get("data", {})
        if isinstance(data, dict):
            return str(data.get("number") or "")
        return ""

    @classmethod
    def _get_account_number(cls, individual_data: dict, mapping: dict) -> str:
        individuals_key = mapping["defaults"].get("individuals_key", "individual-details")
        for field_name, mapped_field in mapping[individuals_key].items():
            model, field = mapped_field.split(".")
            if model != "account_details":
                continue

            retrieved_value = cls.get(individual_data, field_name)
            if field == "data" and isinstance(retrieved_value, dict):
                return str(retrieved_value.get("number") or "")
            if field == "number":
                return str(retrieved_value or "")
        return ""

    @staticmethod
    def _get_national_id_field_name(mapping: dict) -> str:
        individuals_key = mapping["defaults"].get("individuals_key", "individual-details")
        individuals_mapping = mapping.get(individuals_key, {})
        for field_name, mapped_field in individuals_mapping.items():
            if mapped_field == "document.doc_national-document_number":
                return field_name
        return "national_id_no_i_c"

    def _record_has_duplicate_national_id(
        self,
        individual_data: dict,
        registration_data_import: RegistrationDataImport,
        mapping: dict,
    ) -> bool:
        national_id_field_name = self._get_national_id_field_name(mapping)
        national_id = (individual_data.get(national_id_field_name) or "").strip()
        if not national_id:
            return False

        national_document_type_key = IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        return Document.all_merge_status_objects.filter(
            program=registration_data_import.program,
            type__key=national_document_type_key,
            document_number=national_id,
        ).exists()

    def _record_has_duplicate_account_number(
        self,
        individual_data: dict,
        registration_data_import: RegistrationDataImport,
        mapping: dict,
    ) -> bool:
        account_number = self._get_account_number(individual_data, mapping)
        if not account_number:
            return False

        return Account.all_objects.filter(
            individual__program_id=registration_data_import.program_id,
            number=account_number,
        ).exists()

    @classmethod
    def _get_account_number_from_record_data(cls, record_data: dict, mapping: dict) -> str:
        individuals_key = mapping["defaults"].get("individuals_key", "individual-details")
        individuals_data = record_data.get(individuals_key) or []
        if not individuals_data:
            return ""
        return cls._get_account_number(individuals_data[0], mapping)

    @staticmethod
    def _ignore_record(record: Any, reason: str) -> None:
        record.ignored = True
        record.error_message = reason
        record.save(update_fields=["ignored", "error_message"])

    def create_household_for_rdi_household(self, record: Any, registration_data_import: RegistrationDataImport) -> None:
        mapping = self.get_mapping(self.registration.mapping)
        record_data_dict = record.get_data()
        individuals_key = mapping["defaults"].get("individuals_key", "individual-details")
        individual_data = record_data_dict.get(individuals_key, [])[0]

        if self._record_has_duplicate_national_id(individual_data, registration_data_import, mapping):
            self._ignore_record(record, self.DUPLICATE_NATIONAL_ID_REASON)
            logger.warning(
                f"Ignoring Aurora record with duplicate national id,"
                f" record_id {record.id}, record_source_id {record.source_id}",
            )
            return

        if self._record_has_duplicate_account_number(individual_data, registration_data_import, mapping):
            self._ignore_record(record, self.DUPLICATE_ACCOUNT_NUMBER_REASON)
            logger.warning(
                f"Ignoring Aurora record with duplicate account number,"
                f" record_id {record.id}, record_source_id {record.source_id}",
            )
            return

        household = self.create_household_data(record, registration_data_import, mapping)
        individuals, head, pr_collector, _ = self.create_individuals(
            record,
            household,
            mapping,
        )

        individual = individuals[0]
        individual.relationship = HEAD
        individual.save()
        collector = pr_collector or head or individual
        head_of_household = head or individual
        household.head_of_household = head_of_household
        PendingIndividualRoleInHousehold.objects.create(individual=collector, household=household, role=ROLE_PRIMARY)

        self._prepare_national_id(individual_data, individual, mapping)

        household.registration_id = record.source_id
        household.detail_id = record.source_id
        household.save()
        record.mark_as_imported()

    def _prepare_national_id(
        self, individual_dict: dict, imported_individual: PendingIndividual, mapping: dict
    ) -> PendingDocument | None:
        national_id_field_name = self._get_national_id_field_name(mapping)
        national_id = individual_dict.get(national_id_field_name)
        if not national_id:
            return None
        photo = None
        if photo_base_64 := individual_dict.get("national_id_photo_i_c"):
            photo = self._prepare_picture_from_base64(photo_base_64, national_id)
        return PendingDocument.objects.create(
            program=imported_individual.program,
            document_number=national_id,
            individual=imported_individual,
            type=DocumentType.objects.get(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]),
            country=Country.objects.get(iso_code2="NG"),
            photo=photo,
        )

    def create_account(self, account_data: dict, individual: PendingIndividual) -> PendingAccount:
        account = super().create_account(account_data, individual)
        # TODO: remove this when fully switched to FI_pk import
        if financial_institution_code := account.data.get("uba_code"):
            uba_fsp = FinancialServiceProvider.objects.get(name="United Bank for Africa - Nigeria")

            try:
                uba_mapping = FinancialInstitutionMapping.objects.get(
                    code=financial_institution_code,
                    financial_service_provider=uba_fsp,
                )
                account.financial_institution = uba_mapping.financial_institution
                account.data["code"] = account.data.pop("uba_code")
                account.save(update_fields=["financial_institution", "data"])

            except FinancialInstitutionMapping.DoesNotExist:  # pragma: no cover
                logger.error(
                    f"FinancialInstitutionMapping for {uba_fsp} uba code {financial_institution_code} not found"
                )

        return account
