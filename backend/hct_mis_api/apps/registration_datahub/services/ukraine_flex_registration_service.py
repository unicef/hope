import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from django.core.exceptions import ValidationError
from django.forms import modelform_factory

from django_countries.fields import Country

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
    YES,
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

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from hct_mis_api.apps.account.models import Role


class UkraineBaseRegistrationService(BaseRegistrationService):
    BUSINESS_AREA_SLUG: str = "ukraine"
    REGISTRATION_ID: Tuple = (2, 3)

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
        "email": "email",
    }

    HOUSEHOLD_MAPPING_DICT = {
        "residence_status": "residence_status_h_c",
        "admin1": "admin1_h_c",
        "admin2": "admin2_h_c",
        "size": "size_h_c",
    }
    DOCUMENT_MAPPING_TYPE_DICT = {
        IDENTIFICATION_TYPE_NATIONAL_ID: ("national_id_no_i_c_1", "national_id_picture"),
        IDENTIFICATION_TYPE_NATIONAL_PASSPORT: ("international_passport_i_c", "international_passport_picture"),
        IDENTIFICATION_TYPE_DRIVERS_LICENSE: ("drivers_license_no_i_c", "drivers_license_picture"),
        IDENTIFICATION_TYPE_BIRTH_CERTIFICATE: ("birth_certificate_no_i_c", "birth_certificate_picture"),
        IDENTIFICATION_TYPE_RESIDENCE_PERMIT_NO: ("residence_permit_no_i_c", "residence_permit_picture"),
        IDENTIFICATION_TYPE_TAX_ID: ("tax_id_no_i_c", "tax_id_picture"),
    }

    def create_household_for_rdi_household(
        self, record: Record, registration_data_import: RegistrationDataImportDatahub
    ) -> None:
        self._check_registration_id(record.registration, "Ukraine data is processed only from registration 2, 3 or 11!")

        individuals: List[ImportedIndividual] = []
        documents: List[ImportedDocument] = []
        record_data_dict = record.get_data()
        household_dict = record_data_dict.get("household", [])[0]
        individuals_array = record_data_dict.get("individuals", [])

        if not self._has_head(individuals_array):
            self._set_default_head_of_household(individuals_array)

        self.validate_household(individuals_array)

        household_data = self._prepare_household_data(household_dict, record, registration_data_import)
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

        for index, individual_dict in enumerate(individuals_array):
            try:
                individual_data = self._prepare_individual_data(individual_dict, household, registration_data_import)
                role = individual_data.pop("role")
                phone_no = individual_data.pop("phone_no", "")

                individual: ImportedIndividual = self._create_object_and_validate(individual_data, ImportedIndividual)
                individual.disability_certificate_picture = individual_data.get("disability_certificate_picture")
                individual.phone_no = phone_no
                individual.kobo_asset_id = record.source_id
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
                raise ValidationError({f"individual nr {index + 1}": [str(e)]}) from e

        ImportedDocument.objects.bulk_create(documents)

    def _set_default_head_of_household(self, individuals_array: "QuerySet") -> None:
        for individual_data in individuals_array:
            if individual_data.get("role_i_c") == "y":
                individual_data["relationship_i_c"] = "head"
                break

    def _create_role(self, role: "Role", individual: ImportedIndividual, household: ImportedHousehold) -> None:
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

    def _prepare_household_data(
        self, household_dict: Dict, record: Record, registration_data_import: RegistrationDataImportDatahub
    ) -> Dict:
        household_data = dict(
            **build_arg_dict_from_dict(household_dict, self.HOUSEHOLD_MAPPING_DICT),
            flex_registrations_record=record,
            registration_data_import=registration_data_import,
            first_registration_date=record.timestamp,
            last_registration_date=record.timestamp,
            country_origin=Country(code="UA"),
            country=Country(code="UA"),
            consent=True,
            collect_individual_data=YES,
        )

        if residence_status := household_data.get("residence_status"):
            household_data["residence_status"] = residence_status.upper()

        return household_data

    def _prepare_individual_data(
        self,
        individual_dict: Dict,
        household: ImportedHousehold,
        registration_data_import: RegistrationDataImportDatahub,
    ) -> Dict:
        individual_data = dict(
            **build_arg_dict_from_dict(individual_dict, self.INDIVIDUAL_MAPPING_DICT),
            household=household,
            registration_data_import=registration_data_import,
            first_registration_date=household.first_registration_date,
            last_registration_date=household.last_registration_date,
        )
        disability = individual_data.get("disability", "n")
        disability_certificate_picture = individual_data.get("disability_certificate_picture")
        if disability == "y" or disability_certificate_picture:
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
        else:
            individual_data["phone_no"] = ""

        if disability_certificate_picture:
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

    def _prepare_documents(self, individual_dict: Dict, individual: ImportedIndividual) -> List[ImportedDocument]:
        documents = []

        for document_type_string, (
            document_number_field_name,
            picture_field_name,
        ) in self.DOCUMENT_MAPPING_TYPE_DICT.items():
            document_number = individual_dict.get(document_number_field_name)
            certificate_picture = individual_dict.get(picture_field_name, "")

            if not document_number and not certificate_picture:
                continue

            document_number = document_number or f"ONLY_PICTURE_{uuid.uuid4()}"

            certificate_picture = self._prepare_picture_from_base64(certificate_picture, document_number)

            document_type = ImportedDocumentType.objects.get(type=document_type_string)
            document_kwargs = {
                "country": "UA",
                "type": document_type,
                "document_number": document_number,
                "individual": individual,
            }
            ModelClassForm = modelform_factory(ImportedDocument, fields=list(document_kwargs.keys()))
            form = ModelClassForm(document_kwargs)
            if not form.is_valid():
                raise ValidationError(form.errors)
            document = ImportedDocument(photo=certificate_picture, **document_kwargs)
            documents.append(document)

        return documents

    def _prepare_bank_account_info(
        self, individual_dict: Dict, individual: ImportedIndividual
    ) -> Optional[Dict[str, Any]]:
        if individual_dict.get("bank_account_h_f", "n") != "y":
            return None
        if not individual_dict.get("bank_account_number") or not individual_dict.get("bank_account"):
            return None
        bank_name = individual_dict.get("bank_name_h_f", "")
        # AB#154910 default bank name for Ukraine is 'Private Bank'
        other_bank_name = individual_dict.get("other_bank_name", "Private Bank")
        # bank_name is required
        bank_name = bank_name or other_bank_name
        bank_account_info_data = {
            "bank_account_number": str(individual_dict.get("bank_account", "")).replace(" ", ""),
            "bank_name": bank_name,
            "debit_card_number": str(individual_dict.get("bank_account_number", "")).replace(" ", ""),
            "individual": individual,
        }
        return bank_account_info_data

    def validate_household(self, individuals_array: List[ImportedIndividual]) -> None:
        if not individuals_array:
            raise ValidationError("Household should has at least one individual")

        has_head = self._has_head(individuals_array)
        if not has_head:
            raise ValidationError("Household should has at least one Head of Household")

    def _has_head(self, individuals_array: List[ImportedIndividual]) -> bool:
        return any(
            individual_data.get(
                "relationship_i_c",
            )
            == "head"
            for individual_data in individuals_array
        )


class UkraineRegistrationService(UkraineBaseRegistrationService):
    REGISTRATION_ID: Tuple = (11,)

    HOUSEHOLD_MAPPING_DICT = {
        "admin1": "admin1_h_c",
        "admin2": "admin2_h_c",
        "admin3": "admin3_h_c",
        "admin4": "admin4_h_c",
    }
