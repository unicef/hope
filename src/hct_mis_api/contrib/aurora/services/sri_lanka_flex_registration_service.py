from typing import Any

from hct_mis_api.apps.core.utils import (
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
    build_arg_dict_from_dict_if_exists,
    build_flex_arg_dict_from_list_if_exists,
)
from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_BANK_STATEMENT,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    ROLE_PRIMARY,
    DocumentType,
    PendingBankAccountInfo,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.age_at_registration import calculate_age_at_registration
from hct_mis_api.contrib.aurora.services.base_flex_registration_service import (
    BaseRegistrationService,
)


class SriLankaRegistrationService(BaseRegistrationService):
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
        self, localization_dict: dict, record: Any, registration_data_import: RegistrationDataImport
    ) -> dict:
        household_data = {
            "registration_data_import": registration_data_import,
            "program": registration_data_import.program,
            "first_registration_date": record.timestamp,
            "last_registration_date": record.timestamp,
            "country_origin": Country.objects.get(iso_code2="LK"),
            "country": Country.objects.get(iso_code2="LK"),
            "consent": True,
            "size": 0,
            "flex_fields": {"moh_center_of_reference": localization_dict.get("moh_center_of_reference")},
            "business_area": registration_data_import.business_area,
            "address": localization_dict.get("address_h_c"),
        }
        admin2 = localization_dict.get("admin2_h_c")
        admin3 = localization_dict.get("admin3_h_c")
        admin4 = localization_dict.get("admin4_h_c")

        household_data["admin2"] = str(Area.objects.get(p_code=admin2).id) if admin2 else None
        household_data["admin3"] = str(Area.objects.get(p_code=admin3).id) if admin3 else None
        household_data["admin4"] = str(Area.objects.get(p_code=admin4).id) if admin4 else None

        if admin2 and Area.objects.filter(p_code=admin2).exists():
            household_data["admin1"] = str(Area.objects.get(p_code=admin2).parent.id)

        if admin4 and Area.objects.filter(p_code=admin4).exists():
            household_data["admin_area"] = str(Area.objects.get(p_code=admin4).id)
        elif admin3 and Area.objects.filter(p_code=admin3).exists():
            household_data["admin_area"] = str(Area.objects.get(p_code=admin3).id)
        elif admin2 and Area.objects.filter(p_code=admin2).exists():
            household_data["admin_area"] = str(Area.objects.get(p_code=admin2).id)

        return household_data

    def _prepare_individual_data(
        self,
        head_of_household_info: dict,
        registration_data_import: RegistrationDataImport | None = None,
        **kwargs: Any,
    ) -> dict:
        flex_fields_dict = build_flex_arg_dict_from_list_if_exists(
            head_of_household_info, SriLankaRegistrationService.INDIVIDUAL_FLEX_FIELDS
        )
        populate_pdu_with_null_values(registration_data_import.program, flex_fields_dict)  # type: ignore

        individual_data = dict(
            **build_arg_dict_from_dict_if_exists(
                head_of_household_info, SriLankaRegistrationService.INDIVIDUAL_MAPPING_DICT
            ),
            flex_fields=flex_fields_dict,
            program=registration_data_import.program,
            **kwargs,
        )

        if relationship := individual_data.get("relationship"):
            individual_data["relationship"] = relationship.upper()
        if sex := individual_data.get("sex").strip():
            individual_data["sex"] = sex.upper()

        individual_data["age_at_registration"] = calculate_age_at_registration(
            registration_data_import.created_at, individual_data.get("birth_date", "")
        )
        return individual_data

    def _prepare_national_id(
        self, individual_dict: dict, imported_individual: PendingIndividual
    ) -> PendingDocument | None:
        national_id = individual_dict.get("national_id_no_i_c")
        if not national_id:
            return None
        return PendingDocument.objects.create(
            program=imported_individual.program,
            document_number=national_id,
            individual=imported_individual,
            type=DocumentType.objects.get(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]),
            country=Country.objects.get(iso_code2="LK"),
        )

    def _prepare_birth_certificate(
        self, individual_dict: dict, imported_individual: PendingIndividual
    ) -> PendingDocument | None:
        national_id = individual_dict.get("chidlren_birth_certificate")
        if not national_id:
            return None
        return PendingDocument.objects.create(
            program=imported_individual.program,
            document_number=national_id,
            individual=imported_individual,
            type=DocumentType.objects.get(
                key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
            ),
            country=Country.objects.get(iso_code2="LK"),
        )

    def _prepare_bank_statement_document(self, individual_dict: dict, imported_individual: PendingIndividual) -> None:
        bank_account = individual_dict.get("confirm_bank_account_number")
        if not bank_account:
            return None
        photo_base_64 = individual_dict.get("bank_account_details_picture")
        if not photo_base_64:
            return None
        image = self._prepare_picture_from_base64(photo_base_64, bank_account)
        return PendingDocument.objects.create(
            program=imported_individual.program,
            document_number=bank_account,
            individual=imported_individual,
            type=DocumentType.objects.get(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BANK_STATEMENT]),
            photo=image,
            country=Country.objects.get(iso_code2="LK"),
        )

    def create_household_for_rdi_household(self, record: Any, registration_data_import: RegistrationDataImport) -> None:
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
        household = self._create_object_and_validate(household_data, PendingHousehold)
        if id_enumerator:
            household.flex_fields["id_enumerator"] = id_enumerator

        base_individual_data_dict = {
            "household": household,
            "registration_data_import": registration_data_import,
            "first_registration_date": record.timestamp,
            "last_registration_date": record.timestamp,
            "preferred_language": preferred_language_of_contact,
            "business_area": registration_data_import.business_area,
        }

        head_of_household = PendingIndividual.objects.create(
            **base_individual_data_dict,
            **self._prepare_individual_data(head_of_household_dict, registration_data_import),
            relationship=HEAD,
        )
        self._prepare_national_id(head_of_household_dict, head_of_household)

        # TODO: check if this is correct
        bank_name = f"{collector_dict.get('bank_description')} [{collector_dict.get('bank_name')} - {collector_dict.get('branch_or_branch_code')}]"
        bank_account_number = collector_dict.get("confirm_bank_account_number")
        if should_use_hoh_as_collector:
            primary_collector = head_of_household
        else:
            primary_collector = PendingIndividual.objects.create(
                **base_individual_data_dict, **self._prepare_individual_data(collector_dict, registration_data_import)
            )
            self._prepare_national_id(collector_dict, primary_collector)
        self._prepare_bank_statement_document(collector_dict, primary_collector)

        PendingIndividualRoleInHousehold.objects.create(
            household=household, individual=primary_collector, role=ROLE_PRIMARY
        )
        if bank_name and bank_account_number:
            PendingBankAccountInfo.objects.create(
                bank_name=bank_name,
                bank_account_number=bank_account_number,
                account_holder_name=collector_dict.get("account_holder_name_i_c", ""),
                bank_branch_name=collector_dict.get("bank_branch_name_i_c", ""),
                individual=primary_collector,
            )
        individuals_to_create = []
        for individual_data_dict in individuals_list:
            if not bool(individual_data_dict):
                continue

            individuals_to_create.append(
                PendingIndividual(
                    **{
                        **self._prepare_individual_data(individual_data_dict, registration_data_import),
                        **base_individual_data_dict,
                    },
                )
            )

        PendingIndividual.objects.bulk_create(individuals_to_create)
        for individual_data_dict, imported_individual in zip(individuals_list, individuals_to_create, strict=False):
            self._prepare_birth_certificate(individual_data_dict, imported_individual)
        household.size = len(individuals_to_create) + 1
        household.head_of_household = head_of_household
        household.detail_id = record.source_id
        household.save()

        record.mark_as_imported()
