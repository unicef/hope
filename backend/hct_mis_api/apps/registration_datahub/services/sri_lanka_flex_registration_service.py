from typing import Any, Dict, Optional

from django_countries.fields import Country

from hct_mis_api.apps.core.utils import (
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
    build_arg_dict_from_dict,
    build_arg_dict_from_dict_if_exists,
    build_flex_arg_dict_from_list_if_exists,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_BANK_STATEMENT,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
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


class SriLankaRegistrationService(BaseRegistrationService):
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
            type=ImportedDocumentType.objects.get(
                key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
            ),
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
            type=ImportedDocumentType.objects.get(
                key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
            ),
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
            type=ImportedDocumentType.objects.get(
                key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BANK_STATEMENT]
            ),
            photo=image,
            country=Country(code="LK"),
        )

    def create_household_for_rdi_household(
        self, record: Record, registration_data_import: RegistrationDataImportDatahub
    ) -> None:
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
