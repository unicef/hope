import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from django.core.exceptions import ValidationError
from django.forms import modelform_factory

from django_countries.fields import Country

from hct_mis_api.apps.core.utils import (
    build_arg_dict_from_dict,
    build_arg_dict_from_dict_if_exists,
    build_flex_arg_dict_from_list_if_exists,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import (
    DISABLED,
    HEAD,
    IDENTIFICATION_TYPE_BANK_STATEMENT,
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
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    process_flex_records_task,
    process_sri_lanka_flex_records_task,
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
    from uuid import UUID

    from django.db.models.query import QuerySet

    from hct_mis_api.apps.account.models import Role


class FlexRegistrationService(BaseRegistrationService):
    BUSINESS_AREA_SLUG = "ukraine"
    REGISTRATION_ID = (2, 3)
    PROCESS_FLEX_RECORDS_TASK = process_flex_records_task

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
        if record.registration not in self.REGISTRATION_ID:
            raise ValidationError("Ukraine data is processed only from registration 2 or 3!")

        individuals: List[ImportedIndividual] = []
        documents: List[ImportedDocument] = []
        record_data_dict = record.get_data()
        household_dict = record_data_dict.get("household", [])[0]
        individuals_array = record_data_dict.get("individuals", [])

        if not self._has_head(individuals_array):
            self._set_default_head_of_household(individuals_array)

        self.validate_household(individuals_array)

        household_data = self._prepare_household_data(household_dict, record, registration_data_import)
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
            **build_arg_dict_from_dict(household_dict, FlexRegistrationService.HOUSEHOLD_MAPPING_DICT),
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
            **build_arg_dict_from_dict(individual_dict, FlexRegistrationService.INDIVIDUAL_MAPPING_DICT),
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
        ) in FlexRegistrationService.DOCUMENT_MAPPING_TYPE_DICT.items():
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
        if not individual_dict.get("bank_account_number"):
            return None
        bank_name = individual_dict.get("bank_name_h_f", "")
        other_bank_name = individual_dict.get("other_bank_name", "")
        if not bank_name:
            bank_name = other_bank_name
        bank_account_info_data = {
            "bank_account_number": individual_dict.get("bank_account_number", "").replace(" ", ""),
            "bank_name": bank_name,
            "debit_card_number": individual_dict.get("bank_account_number", "").replace(" ", ""),
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
        return any(individual_data.get("relationship_i_c") == "head" for individual_data in individuals_array)


class SriLankaRegistrationService(BaseRegistrationService):
    BUSINESS_AREA_SLUG = "sri-lanka"
    REGISTRATION_ID = (17,)
    PROCESS_FLEX_RECORDS_TASK = process_sri_lanka_flex_records_task

    HOUSEHOLD_MAPPING_DICT = {
        "admin2": "admin2_h_c",
        "admin3": "admin3_h_c",
        "admin4": "admin4_h_c",
        "address": "address_h_c",
    }

    INDIVIDUAL_MAPPING_DICT = {
        "full_name": "full_name_i_c",
        "birth_date": "birth_date_i_c",
        "sex": "gender_i_c",
        "who_answers_phone": "who_answers_phone_i_c",
        "relationship": "relationship_i_c",
        "phone_no": "phone_no_i_c",
        "email": "email",
    }

    INDIVIDUAL_FLEX_FIELDS = [
        "has_nic_number_i_c",
        "confirm_nic_number",
        "branch_or_branch_code",
        "who_answers_this_phone",
        "confirm_alternate_collector_phone_number",
        "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi",
    ]

    def _prepare_household_data(
        self, localization_dict: Dict, record: Record, registration_data_import: RegistrationDataImportDatahub
    ) -> Dict:
        household_data = {
            **build_arg_dict_from_dict(localization_dict, SriLankaRegistrationService.HOUSEHOLD_MAPPING_DICT),
            "flex_registrations_record": record,
            "registration_data_import": registration_data_import,
            "first_registration_date": record.timestamp,
            "last_registration_date": record.timestamp,
            "country_origin": Country(code="LK"),
            "country": Country(code="LK"),
            "consent": True,
            "collect_individual_data": YES,
            "size": 0,
            "flex_fields": {"moh_center_of_reference": localization_dict.get("moh_center_of_reference")},
        }
        admin2 = localization_dict.get("admin2_h_c")
        if admin2 and Area.objects.filter(p_code=admin2).exists():
            household_data["admin2_title"] = Area.objects.get(p_code=admin2).name
        admin3 = localization_dict.get("admin3_h_c")
        if admin3 and Area.objects.filter(p_code=admin3).exists():
            household_data["admin3_title"] = Area.objects.get(p_code=admin3).name
        admin4 = localization_dict.get("admin4_h_c")
        if admin4 and Area.objects.filter(p_code=admin4).exists():
            household_data["admin4_title"] = Area.objects.get(p_code=admin4).name

        if admin2 and Area.objects.filter(p_code=admin2).exists():
            household_data["admin1"] = Area.objects.get(p_code=admin2).parent.p_code
            household_data["admin1_title"] = Area.objects.get(p_code=admin2).parent.name

        if admin4 and Area.objects.filter(p_code=admin4).exists():
            household_data["admin_area"] = Area.objects.get(p_code=admin4).p_code
            household_data["admin_area_title"] = Area.objects.get(p_code=admin4).name
        elif admin3 and Area.objects.filter(p_code=admin3).exists():
            household_data["admin_area"] = Area.objects.get(p_code=admin3).p_code
            household_data["admin_area_title"] = Area.objects.get(p_code=admin3).name
        elif admin2 and Area.objects.filter(p_code=admin2).exists():
            household_data["admin_area"] = Area.objects.get(p_code=admin2).p_code
            household_data["admin_area_title"] = Area.objects.get(p_code=admin2).name

        return household_data

    def _prepare_individual_data(self, head_of_household_info: Dict, **kwargs: Any) -> Dict:
        individual_data = dict(
            **build_arg_dict_from_dict_if_exists(
                head_of_household_info, SriLankaRegistrationService.INDIVIDUAL_MAPPING_DICT
            ),
            flex_fields=build_flex_arg_dict_from_list_if_exists(
                head_of_household_info, SriLankaRegistrationService.INDIVIDUAL_FLEX_FIELDS
            ),
            **kwargs,
        )

        if relationship := individual_data.get("relationship"):
            individual_data["relationship"] = relationship.upper()
        if sex := individual_data.get("sex").strip():
            individual_data["sex"] = sex.upper()

        return individual_data

    def _prepare_national_id(
        self, individual_dict: Dict, imported_individual: ImportedIndividual
    ) -> Optional[ImportedDocument]:
        national_id = individual_dict.get("national_id_no_i_c")
        if not national_id:
            return None
        return ImportedDocument.objects.create(
            document_number=national_id,
            individual=imported_individual,
            type=ImportedDocumentType.objects.get(type=IDENTIFICATION_TYPE_NATIONAL_ID),
            country=Country(code="LK"),
        )

    def _prepare_birth_certificate(
        self, individual_dict: Dict, imported_individual: ImportedIndividual
    ) -> Optional[ImportedDocument]:
        national_id = individual_dict.get("chidlren_birth_certificate")
        if not national_id:
            return None
        return ImportedDocument.objects.create(
            document_number=national_id,
            individual=imported_individual,
            type=ImportedDocumentType.objects.get(type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE),
            country=Country(code="LK"),
        )

    def _prepare_bank_statement_document(self, individual_dict: Dict, imported_individual: ImportedIndividual) -> None:
        bank_account = individual_dict.get("confirm_bank_account_number")
        if not bank_account:
            return None
        photo_base_64 = individual_dict.get("bank_account_details_picture")
        if not photo_base_64:
            return None
        image = self._prepare_picture_from_base64(photo_base_64, bank_account)
        return ImportedDocument.objects.create(
            document_number=bank_account,
            individual=imported_individual,
            type=ImportedDocumentType.objects.get(type=IDENTIFICATION_TYPE_BANK_STATEMENT),
            photo=image,
            country=Country(code="LK"),
        )

    def create_household_for_rdi_household(
        self, record: Record, registration_data_import: RegistrationDataImportDatahub
    ) -> None:
        if record.registration not in self.REGISTRATION_ID:
            raise ValidationError("Sri-Lanka data is processed only from registration 17!")

        record_data_dict = record.get_data()

        localization_dict = record_data_dict.get("localization-info", [])[0]
        head_of_household_dict = record_data_dict.get("caretaker-info", [])[0]
        collector_dict = record_data_dict.get("collector-info", [])[0]
        individuals_list = record_data_dict.get("children-info", [])
        id_enumerator = record_data_dict.get("id_enumerator")
        preferred_language_of_contact = record_data_dict.pop("prefered_language_of_contact", None)
        should_use_hoh_as_collector = (
            collector_dict.get("does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi") == "y"
        )
        household_data = self._prepare_household_data(localization_dict, record, registration_data_import)
        household = self._create_object_and_validate(household_data, ImportedHousehold)
        if id_enumerator:
            household.flex_fields["id_enumerator"] = id_enumerator
        base_individual_data_dict = dict(
            household=household,
            registration_data_import=registration_data_import,
            first_registration_date=record.timestamp,
            last_registration_date=record.timestamp,
            preferred_language=preferred_language_of_contact,
        )

        head_of_household = ImportedIndividual.objects.create(
            **base_individual_data_dict, **self._prepare_individual_data(head_of_household_dict), relationship=HEAD
        )
        self._prepare_national_id(head_of_household_dict, head_of_household)

        bank_name = f"{collector_dict.get('bank_description')} [{collector_dict.get('bank_name')} - {collector_dict.get('branch_or_branch_code')}]"  # TODO: check if this is correct
        bank_account_number = collector_dict.get("confirm_bank_account_number")
        if should_use_hoh_as_collector:
            primary_collector = head_of_household
        else:
            primary_collector = ImportedIndividual.objects.create(
                **base_individual_data_dict, **self._prepare_individual_data(collector_dict)
            )
            self._prepare_national_id(collector_dict, primary_collector)
        self._prepare_bank_statement_document(collector_dict, primary_collector)

        ImportedIndividualRoleInHousehold.objects.create(
            household=household, individual=primary_collector, role=ROLE_PRIMARY
        )
        if bank_name and bank_account_number:
            ImportedBankAccountInfo.objects.create(
                bank_name=bank_name, bank_account_number=bank_account_number, individual=primary_collector
            )
        individuals_to_create = []
        for individual_data_dict in individuals_list:
            if not bool(individual_data_dict):
                continue
            individuals_to_create.append(
                ImportedIndividual(
                    **{
                        **self._prepare_individual_data(individual_data_dict),
                        **base_individual_data_dict,
                    }
                )
            )

        ImportedIndividual.objects.bulk_create(individuals_to_create)
        for individual_data_dict, imported_individual in zip(individuals_list, individuals_to_create):
            self._prepare_birth_certificate(individual_data_dict, imported_individual)
        household.size = len(individuals_to_create) + 1
        household.head_of_household = head_of_household
        household.kobo_asset_id = record.source_id
        household.save()

        record.mark_as_imported()


def get_registration_to_rdi_service_map() -> Dict[int, Any]:
    return {
        2: FlexRegistrationService,  # ukraine
        3: FlexRegistrationService,  # ukraine
        17: SriLankaRegistrationService,  # sri lanka
        # 18: "czech republic",
        # 19: "czech republic",
    }


def create_task_for_processing_records(service: Any, rdi_id: "UUID", records_ids: List) -> None:
    if celery_task := service.PROCESS_FLEX_RECORDS_TASK:
        celery_task.delay(rdi_id, records_ids)
