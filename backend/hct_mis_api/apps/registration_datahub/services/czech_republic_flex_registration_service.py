import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from django.core.exceptions import ValidationError
from django.forms import modelform_factory

from django_countries.fields import Country

from hct_mis_api.apps.core.utils import (
    build_arg_dict_from_dict_if_exists,
    build_flex_arg_dict_from_list_if_exists,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_PARTIAL,
    GOVERNMENT_PARTNER,
    HEAD,
    HUMANITARIAN_PARTNER,
    NOT_DISABLED,
    PRIVATE_PARTNER,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    Record,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.services.base_flex_registration_service import (
    BaseRegistrationService,
)

logger = logging.getLogger(__name__)


class CzechRepublicFlexRegistration(BaseRegistrationService):
    BUSINESS_AREA_SLUG: str = "czech-republic"
    REGISTRATION_ID: Tuple = (25,)

    INDIVIDUAL_MAPPING_DICT: Dict[str, str] = {
        "sex": "gender_i_c",
        "birth_date": "birth_date_i_c",
        "phone_no": "phone_no_i_c",
        "given_name": "given_name_i_c",
        "family_name": "family_name_i_c",
        "relationship": "relationship_i_c",
        "preferred_language": "preferred_language_i_c",
    }

    INDIVIDUAL_FLEX_FIELDS: List[str] = [
        "employment_type",
        "work_status_i_c",
        "other_nationality",
        "other_nationality",
        "immediate_relative",
        "czech_formal_employment",
        "other_communication_language",
        "primary_carer_is_legal_guardian",
        "follow_up_flag",
        "follow_up_needed",
        "follow_up_comments",
        "disability_card_no_i_c",
        "disability_degree_i_c",
        "preregistration_case_id",
        "disability_card_issuance_i_c",
        "proof_legal_guardianship_no_i_c",
        "medical_certificate_issuance_i_c",
        "medical_certificate_validity_i_c",
        "has_disability_card_and_medical_cert",
        "legal_guardia_not_primary_carer",
    ]

    DOCUMENT_MAPPING: Dict[str, str] = {
        "birth_certificate_no_i_c": "birth_certificate",
        "disability_card_no_i_c": "disability_card",
        "national_id_no_i_c": "national_id",
        "national_passport_i_c": "national_passport",
        "medical_certificate_no_i_c": "medical_certificate",
        "other_id_no_i_c": "temporary_protection_visa",
        "proof_legal_guardianship_no_i_c": "proof_of_legal_guardianship",
    }

    def _prepare_household_data(
        self,
        record: Record,
        household_address: Dict,
        consent_data: Dict,
        needs_assessment: Dict,
        registration_data_import: RegistrationDataImportDatahub,
    ) -> Dict:
        address = household_address.get("address_h_c", "")
        village = household_address.get("village_h_c", "")
        zip_code = household_address.get("zip_code_h_c", "")

        household_data = {
            "flex_registrations_record": record,
            "registration_data_import": registration_data_import,
            "first_registration_date": record.timestamp,
            "last_registration_date": record.timestamp,
            "country_origin": Country(code="CZ"),
            "country": Country(code="CZ"),
            "consent_sharing": [],
            "collect_individual_data": COLLECT_TYPE_PARTIAL,
        }
        if needs_assessment:
            household_data["flex_fields"] = needs_assessment

        consent_h_c = consent_data.get("consent_h_c", False)
        consent_sharing = consent_data.get("consent_sharing_h_c", False)
        consent_sharing_1 = consent_data.get("consent_sharing_h_c_1", False)
        consent_sharing_2 = consent_data.get("consent_sharing_h_c_2", False)

        household_data["consent_sharing"] = []

        if consent_h_c == "y" or consent_h_c is True:
            household_data["consent"] = True
        if consent_sharing == "y" or consent_sharing is True:
            household_data["consent_sharing"].append(GOVERNMENT_PARTNER)
        if consent_sharing_1 == "y" or consent_sharing_1 is True:
            household_data["consent_sharing"].append(PRIVATE_PARTNER)
        if consent_sharing_2 == "y" or consent_sharing_2 is True:
            household_data["consent_sharing"].append(HUMANITARIAN_PARTNER)

        if address:
            household_data["address"] = address
        if village:
            household_data["village"] = village
        if zip_code:
            household_data["zip_code"] = zip_code

        admin1 = household_address.get("admin1_h_c", "")
        if admin1 and Area.objects.filter(p_code=admin1).exists():
            household_data["admin1_title"] = Area.objects.get(p_code=admin1).name
            household_data["admin1"] = Area.objects.get(p_code=admin1).p_code

        admin2 = household_address.get("admin2_h_c", "")
        if admin2 and Area.objects.filter(p_code=admin2).exists():
            household_data["admin2_title"] = Area.objects.get(p_code=admin2).name
            household_data["admin2"] = Area.objects.get(p_code=admin2).p_code

        if admin2 and Area.objects.filter(p_code=admin2).exists():
            household_data["admin_area"] = Area.objects.get(p_code=admin2).p_code
            household_data["admin_area_title"] = Area.objects.get(p_code=admin2).name
        elif admin1 and Area.objects.filter(p_code=admin1).exists():
            household_data["admin_area"] = Area.objects.get(p_code=admin1).p_code
            household_data["admin_area_title"] = Area.objects.get(p_code=admin1).name

        return household_data

    def _prepare_individual_data(
        self,
        individual_dict: Dict,
        household: ImportedHousehold,
        registration_data_import: RegistrationDataImportDatahub,
    ) -> Dict:
        individual_data = dict(
            **build_arg_dict_from_dict_if_exists(individual_dict, self.INDIVIDUAL_MAPPING_DICT),
            flex_fields=build_flex_arg_dict_from_list_if_exists(individual_dict, self.INDIVIDUAL_FLEX_FIELDS),
            household=household,
            registration_data_import=registration_data_import,
            first_registration_date=household.first_registration_date,
            last_registration_date=household.last_registration_date,
        )

        individual_data["disability"] = individual_dict.get("disability_i_c", NOT_DISABLED)

        if relationship := individual_data.get("relationship"):
            individual_data["relationship"] = relationship.upper()
        if sex := individual_data.get("sex"):
            individual_data["sex"] = sex.upper()

        given_name = individual_data.get("given_name")
        middle_name = individual_data.get("middle_name")
        family_name = individual_data.get("family_name")

        individual_data["full_name"] = " ".join(filter(None, [given_name, middle_name, family_name]))

        work_status = individual_dict.get("work_status_i_c")
        if work_status:
            if work_status == "y":
                individual_data["work_status"] = "1"
            else:
                individual_data["work_status"] = "0"
        else:
            individual_data["work_status"] = "NOT_PROVIDED"

        return individual_data

    def _prepare_bank_account_info(
        self, individual_dict: Dict, imported_individual: ImportedIndividual
    ) -> Optional[Dict]:
        bank_account_number = individual_dict.get("bank_account_number_h_f")
        if not bank_account_number:
            return None

        return {
            "bank_account_number": str(individual_dict.get("bank_account_number", "")).replace(" ", ""),
            "individual": imported_individual,
        }

    def _prepare_documents(
        self, individual_dict: Dict, imported_individual: ImportedIndividual
    ) -> list[ImportedDocument]:
        documents = []

        for individual_document_number, document_key in self.DOCUMENT_MAPPING.items():
            document_number = individual_dict.get(individual_document_number)
            if not document_number:
                continue

            document_type = ImportedDocumentType.objects.get(key=document_key)
            document_kwargs = {
                "country": "CZ",
                "type": document_type,
                "document_number": document_number,
                "individual": imported_individual,
            }

            photo, issuance_date, expiry_date = None, None, None

            if document_number == "proof_legal_guardianship_no_i_c":
                photo = individual_dict.get("proof_legal_guardianship_photo_i_c")

            elif document_number == "disability_card_no_i_c":
                photo = individual_dict.get("disability_card_photo_i_c")
                issuance_date = individual_dict.get("disability_card_issuance_i_c")
            elif document_number == "medical_certificate_no_i_c":
                photo = individual_dict.get("medical_certificate_photo_i_c")
                issuance_date = individual_dict.get("medical_certificate_issuance_i_c")
                expiry_date = individual_dict.get("medical_certificate_validity_i_c")

            if photo:
                document_kwargs["photo"] = self._prepare_picture_from_base64(photo, document_number)
            if issuance_date:
                document_kwargs["issuance_date"] = issuance_date
            if expiry_date:
                document_kwargs["expiry_date"] = expiry_date

            ModelClassForm = modelform_factory(ImportedDocument, fields=list(document_kwargs.keys()))
            form = ModelClassForm(document_kwargs)
            if not form.is_valid():
                raise ValidationError(form.errors)
            document = ImportedDocument(**document_kwargs)
            documents.append(document)

        return documents

    @staticmethod
    def _set_default_head_of_household(individuals_array: List[Any]) -> None:
        for individual_data in individuals_array:
            if individual_data.get("role_i_c") == "y":
                individual_data["relationship_i_c"] = "head"
                break

    @staticmethod
    def _has_head(individuals_array: List[ImportedIndividual]) -> bool:
        return any(
            individual_data.get(
                "relationship_i_c",
            )
            == "head"
            for individual_data in individuals_array
        )

    def validate_household(self, individuals_array: List[ImportedIndividual]) -> None:
        if not individuals_array:
            raise ValidationError("Household should has at least one individual")

        has_head = self._has_head(individuals_array)
        if not has_head:
            raise ValidationError("Household should has at least one Head of Household")

    def create_household_for_rdi_household(
        self, record: Record, registration_data_import: RegistrationDataImportDatahub
    ) -> None:
        self._check_registration_id(record.registration, "Czech Republic data is processed only from registration 25")

        record_data_dict = record.get_data()
        if isinstance(record_data_dict, str):
            record_data_dict = json.loads(record_data_dict)

        household_address = record_data_dict.get("household-address", [])[0]
        consent_data = record_data_dict.get("consent", [])[0]
        needs_assessment_list = record_data_dict.get("needs-assessment")
        needs_assessment = needs_assessment_list[0] if needs_assessment_list else None

        primary_carer_info = record_data_dict.get("primary-carer-info", [])
        children_information = record_data_dict.get("children-information", [])
        legal_guardian_information = record_data_dict.get("legal-guardian-information", [])
        legal_guardian_information = [
            info for info in legal_guardian_information if info.get("legal_guardia_not_primary_carer") != "n"
        ]
        individuals_array = [*primary_carer_info, *children_information, *legal_guardian_information]

        if not self._has_head(individuals_array):
            self._set_default_head_of_household(individuals_array)

        self.validate_household(individuals_array)

        household_data = self._prepare_household_data(
            record, household_address, consent_data, needs_assessment, registration_data_import
        )

        if not household_data.get("size"):
            household_data["size"] = len(individuals_array)
        household = self._create_object_and_validate(household_data, ImportedHousehold)
        household.set_admin_areas()

        household.kobo_asset_id = record.source_id
        household.save(
            update_fields=(
                "admin_area",
                "admin_area_title",
                "admin1_title",
                "admin2_title",
                "kobo_asset_id",
            )
        )

        individuals: List[ImportedIndividual] = []
        documents: List[ImportedDocument] = []

        for index, individual_dict in enumerate(individuals_array):
            try:
                individual_data = self._prepare_individual_data(individual_dict, household, registration_data_import)
                role = individual_dict.pop("role_i_c", "")
                phone_no = individual_data.pop("phone_no", "")

                individual: ImportedIndividual = self._create_object_and_validate(individual_data, ImportedIndividual)
                individual.phone_no = phone_no
                individual.kobo_asset_id = record.source_id
                individual.save()

                bank_account_data = self._prepare_bank_account_info(individual_dict, individual)
                if bank_account_data:
                    self._create_object_and_validate(bank_account_data, ImportedBankAccountInfo)

                if role:
                    if role.upper() == ROLE_PRIMARY:
                        ImportedIndividualRoleInHousehold.objects.create(
                            individual=individual, household=household, role=ROLE_PRIMARY
                        )
                    else:
                        ImportedIndividualRoleInHousehold.objects.create(
                            individual=individual, household=household, role=ROLE_ALTERNATE
                        )
                individuals.append(individual)

                if individual.relationship == HEAD:
                    household.head_of_household = individual
                    household.save(update_fields=("head_of_household",))
                documents.extend(self._prepare_documents(individual_dict, individual))
            except ValidationError as e:
                raise ValidationError({f"individual nr {index + 1}": [str(e)]}) from e

        ImportedDocument.objects.bulk_create(documents)
