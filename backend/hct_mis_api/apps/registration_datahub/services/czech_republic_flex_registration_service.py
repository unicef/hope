from typing import List

from django.core.exceptions import ValidationError
from django.forms import modelform_factory

from django_countries.fields import Country

from hct_mis_api.apps.core.utils import (
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
    build_arg_dict_from_dict_if_exists,
    build_flex_arg_dict_from_list_if_exists,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
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
)
from hct_mis_api.apps.registration_datahub.services.base_flex_registration_service import (
    BaseRegistrationService,
)


class CzechRepublicFlexRegistration(BaseRegistrationService):
    INDIVIDUAL_MAPPING_DICT = {
        "sex": "gender_i_c",
        "birth_date": "birth_date_i_c",
        "phone_no": "phone_no_i_c",
        "given_name": "given_name_i_c",
        "family_name": "family_name_i_c",
        "relationship": "relationship_i_c",
        "preferred_language": "preferred_language_i_c",
    }

    INDIVIDUAL_FLEX_FIELDS = [
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

    DOCUMENT_MAPPING = (
        (IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID], "national_id_no_i_c"),
        (IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT], "national_passport_i_c"),
        (IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE], "disability_card_no_i_c"),
        (IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE], "medical_certificate_no_i_c"),
    )

    def _prepare_household_data(
        self, record, household_address, consent_data, needs_assessment, registration_data_import
    ):
        address = household_address.get("address_h_c", "") + household_address.get("village_h_c", "")
        zip_code = household_address.get("zip_code_h_c", "")

        admin1 = household_address.get("admin1_h_c", "")
        admin2 = household_address.get("admin2_h_c", "")

        household_data = dict(
            flex_registrations_record=record,
            registration_data_import=registration_data_import,
            first_registration_date=record.timestamp,
            last_registration_date=record.timestamp,
            country_origin=Country(code="CZ"),
            country=Country(code="CZ"),
            consent=consent_data.get("consent_h_c", False),
            flex_fields=needs_assessment,
            address=address,
            zip_code=zip_code,
            admin1=admin1,
            admin2=admin2,
        )

        return household_data

    def _prepare_individual_data(self, individual_dict, household, registration_data_import):
        individual_data = dict(
            **build_arg_dict_from_dict_if_exists(individual_dict, self.INDIVIDUAL_MAPPING_DICT),
            flex_fields=build_flex_arg_dict_from_list_if_exists(individual_dict, self.INDIVIDUAL_FLEX_FIELDS),
            household=household,
            registration_data_import=registration_data_import,
            first_registration_date=household.first_registration_date,
            last_registration_date=household.last_registration_date,
        )

        disability = individual_data.get("disability_i_c")
        if disability == "disabled":
            individual_data["disabled"] = True

        if relationship := individual_data.get("relationship"):
            individual_data["relationship"] = relationship.upper()
        if sex := individual_data.get("sex"):
            individual_data["sex"] = sex.upper()

        given_name = individual_data.get("given_name")
        middle_name = individual_data.get("middle_name")
        family_name = individual_data.get("family_name")

        individual_data["full_name"] = " ".join(filter(None, [given_name, middle_name, family_name]))

        return individual_data

    def _prepare_bank_account_info(self, individual_dict, imported_individual):
        bank_account_number = individual_dict.get("bank_account_number")
        if not bank_account_number:
            return None

        return ImportedBankAccountInfo.objects.create(
            bank_account_number=bank_account_number, individual=imported_individual
        )

    def _prepare_documents(self, individual_dict, imported_individual):
        documents = []

        for document_key, individual_document_number in self.DOCUMENT_MAPPING:
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
            ModelClassForm = modelform_factory(ImportedDocument, fields=list(document_kwargs.keys()))
            form = ModelClassForm(document_kwargs)
            if not form.is_valid():
                raise ValidationError(form.errors)
            document = ImportedDocument(**document_kwargs)
            documents.append(document)

        return documents

    def create_household_for_rdi_household(self, record: Record, registration_data_import):
        # remember to check number
        record_data_dict = record.get_data()

        household_address = record_data_dict.get("household-address")
        consent_data = record_data_dict.get("consent")
        needs_assessment = record_data_dict.get("needs-assessment")

        primary_carer_info = record_data_dict.get("primary-carer-info")
        children_information = record_data_dict.get("children-information")
        legal_guardian_information = record_data_dict.get("legal-guardian-information")

        individuals_array = [*primary_carer_info, *children_information, *legal_guardian_information]

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
                "admin3_title",
                "admin4_title",
                "kobo_asset_id",
            )
        )

        individuals: List[ImportedIndividual] = []
        documents: List[ImportedDocument] = []

        for index, individual_dict in enumerate(individuals_array):
            try:
                individual_data = self._prepare_individual_data(individual_dict, household, registration_data_import)
                role = individual_data.pop("role_i_c")
                phone_no = individual_data.pop("phone_no", "")

                individual: ImportedIndividual = self._create_object_and_validate(individual_data, ImportedIndividual)
                individual.phone_no = phone_no
                individual.kobo_asset_id = record.source_id
                individual.save()

                bank_account_data = self._prepare_bank_account_info(individual_dict, individual)
                if bank_account_data:
                    self._create_object_and_validate(bank_account_data, ImportedBankAccountInfo)
                if role:
                    if role == "primary":
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
