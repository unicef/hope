from typing import Any, Dict, List, Optional, Tuple

from django.core.exceptions import ValidationError

from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.household.forms import (BankAccountInfoForm,
                                              DocumentForm, IndividualForm)
from hct_mis_api.apps.household.models import (
    DISABLED, HEAD, NOT_DISABLED, ROLE_ALTERNATE, ROLE_PRIMARY, DocumentType,
    PendingBankAccountInfo, PendingDocument, PendingHousehold,
    PendingIndividual, PendingIndividualRoleInHousehold)
from hct_mis_api.apps.payment.models import (AccountType, FinancialInstitution,
                                             PendingAccount)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.contrib.aurora.services.base_flex_registration_service import \
    BaseRegistrationService

YES = "1"
NO = "0"


COUNTRY = "country"
PRIMARY_COLLECTOR = "primary_collector"
SECONDARY_COLLECTOR = "secondary_collector"

INDIVIDUAL_FIELD = "individual"
DOCUMENT_FIELD = "document"
BANK_FIELD = "bank"
ACCOUNT_FIELD = "account_details"
EXTRA_FIELD = "extra"


def mergedicts(a: Dict, b: Dict, path: Optional[List]) -> Dict:
    if not path:
        path = list()
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                mergedicts(a[key], b[key], path + [str(key)])
            elif a[key] != b[key]:
                raise Exception("Conflict at " + ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


class GenericRegistrationService(BaseRegistrationService):
    master_detail = True
    default_mapping = {
        "household": {
            "admin1_h_c": "household.admin1",
            "admin2_h_c": "household.admin2",
            "admin3_h_c": "household.admin3",
            "admin4_h_c": "household.admin4",
            "village_h_c": "household.village",
            "residence_status_h_c": "household.residence_status",
            "address_h_c": "household.address",
        },
        "individuals": {
            "given_name_i_c": "individual.given_name",
            "middle_name_i_c": "individual.middle_name",
            "family_name_i_c": "individual.family_name",
            "full_name_i_c": "individual.full_name",
            "birth_date_i_c": "individual.birth_date",
            "gender_i_c": "individual.sex",
            "disability_i_c": "individual.disability",
            "relationship_i_c": "individual.relationship",
            "email": "individual.email",
            "phone_no_i_c": "individual.phone_no",
            "phone_no_alternative_i_c": "individual.phone_no_alternative",
            "marital_status_i_c": "individual.marital_status",
            "who_answers_phone_i_c": "individual.who_answers_phone",
            "tax_id_type_i_c": "document.doc_tax-key",
            "tax_id_no_i_c": "document.doc_tax-document_number",
            "tax_id_photo_i_c": "document.doc_tax-photo",
            "birth_certificate_type_i_c": "document.doc_birth-key",
            "birth_certificate_no_i_c": "document.doc_birth-document_number",
            "birth_certificate_photo_i_c": "document.doc_birth-photo",
            "drivers_license_type_i_c": "document.doc_driver-key",
            "drivers_license_no_i_c": "document.doc_driver-document_number",
            "drivers_license_photo_i_c": "document.doc_driver-photo",
            "national_passport_type_i_c": "document.doc_passport-key",
            "national_passport_no_i_c": "document.doc_passport-document_number",
            "national_passport_photo_i_c": "document.doc_passport-photo",
            "national_id_type_i_c": "document.doc_national-key",
            "national_id_i_c": "document.doc_national-document_number",
            "national_id_photo_i_c": "document.doc_national-photo",
            "electoral_card_type_i_c": "document.doc_electoral-key",
            "electoral_card_no_i_c": "document.doc_electoral-document_number",
            "electoral_card_photo_i_c": "document.doc_electoral-photo",
            "bank_account_h_f": "bank.bank1-bank_account_number",
            "bank_name_h_f": "bank.bank1-bank_name",
            "bank_debit_card_h_f": "bank.bank1-debit_card_number",
            "account_holder_name_i_c": "bank.bank1-account_holder_name",
            "bank_branch_name_i_c": "bank.bank1-bank_branch_name",
            "role_pr_i_c": "extra.primary_collector",
            "role_sec_i_c": "extra.secondary_collector",
        },
    }

    @staticmethod
    def get_boolean(value: Any) -> bool:
        if value in ["yes", "YES", "Y", "y", "1", 1, True]:
            return True
        elif value in ["no", "NO", "N", "n", "0", 0, False]:
            return False
        return value

    @staticmethod
    def get_sex(value: str) -> str:
        return value.upper()

    @staticmethod
    def get_relationship(value: str) -> str:
        return value.upper() if value else ""

    @staticmethod
    def get_marital_status(value: str) -> str:
        return value.upper() if value else ""

    @staticmethod
    def get_disability(value: Any) -> str:
        return DISABLED if GenericRegistrationService.get_boolean(value) else NOT_DISABLED

    @classmethod
    def get(cls, data: Dict, key: str) -> Any:
        """
        utility method to get the value given a list of one dict or a dict
        {"key": "value"}
        {"key": ["value"]}
        [{"key": "value"}]
        [{"key": ["value"]}]
        """
        if isinstance(data, list) and len(data) == 1:
            data = data[0]
        if key in data:
            return data[key][0] if isinstance(data[key], list) and len(data[key]) == 1 else data[key]

    @classmethod
    def _create_household_dict(cls, data_dict: Dict, mapping_dict: Dict) -> Dict:
        """create household dictionary ready to be build"""
        my_dict = {}
        for key, value in mapping_dict.items():
            if isinstance(value, str):
                model, field = value.split(".")
                if model == "household":
                    retrieved_value = cls.get(data_dict, key)
                    if retrieved_value:
                        if field == "flex_fields":
                            if "flex_fields" not in my_dict:
                                my_dict["flex_fields"] = dict()
                            flex_dict = my_dict["flex_fields"]
                            flex_dict[key] = retrieved_value
                        else:
                            my_dict[field] = retrieved_value
            elif isinstance(value, dict):
                if key in data_dict:
                    my_dict.update(cls._create_household_dict(data_dict[key], mapping_dict[key]))

        # update admin areas values
        for key in ["admin1", "admin2", "admin3", "admin4"]:
            if key in my_dict and Area.objects.filter(p_code=my_dict[key]).exists():
                my_dict[key] = str(Area.objects.get(p_code=my_dict[key]).id)
        return my_dict

    @staticmethod
    def get_extra_ff(extra_flex_fields: list, data: Dict) -> Dict:
        extra_ffs = {}
        for ff in extra_flex_fields:
            values = data.copy()
            path = ff.split(".")
            found = True
            for item in path:
                if item in values:
                    values = values[item]
                else:
                    found = False
            if found:
                extra_ffs[ff.replace(".", "_")] = values
        return extra_ffs

    @classmethod
    def create_individuals_dicts(cls, data_dict: List, mapping_dict: Dict, mapping: Dict) -> List:
        """create individuals dicts, including documents and banks"""
        individuals_dicts = []
        constances = mapping.get("individual_constances", {})

        for item in data_dict:
            my_dict = dict(extra=dict())
            my_dict["documents"] = dict()
            my_dict["banks"] = dict()
            my_dict[ACCOUNT_FIELD] = dict()
            flex_fields = dict()
            for key, value in mapping_dict.items():
                model, field = value.split(".")
                retrieved_value = cls.get(item, key)
                method = getattr(cls, f"get_{field}", None)
                if method:
                    retrieved_value = method(retrieved_value)
                if retrieved_value is not None and retrieved_value != "":
                    if model == INDIVIDUAL_FIELD:
                        my_dict[field] = retrieved_value
                    if model == DOCUMENT_FIELD:
                        doc_num, doc_field = field.split("-")
                        if doc_num not in my_dict["documents"]:
                            my_dict["documents"][doc_num] = dict()
                        my_dict["documents"][doc_num].update({doc_field: retrieved_value})
                    if model == BANK_FIELD:
                        bank_num, bank_field = field.split("-")
                        if bank_num not in my_dict["banks"]:
                            my_dict["banks"][bank_num] = dict()
                        my_dict["banks"][bank_num].update({bank_field: retrieved_value})
                    if model == ACCOUNT_FIELD:
                        my_dict[ACCOUNT_FIELD][field] = retrieved_value
                    if model == EXTRA_FIELD:
                        my_dict["extra"][field] = retrieved_value
                    for kk, vv in item.items():
                        if kk not in mapping_dict:
                            flex_fields[kk] = vv
                my_dict["flex_fields"] = flex_fields
            if not bool(my_dict["flex_fields"]):
                my_dict.pop("flex_fields")
            my_dict.update(constances)
            individuals_dicts.append(my_dict)
        return individuals_dicts

    def create_household_data(
        self,
        record: Any,
        registration_data_import: RegistrationDataImport,
        mapping: Dict,
    ) -> PendingHousehold:
        record_data_dict = record.get_data()
        household_payload = self._create_household_dict(record_data_dict, mapping)
        flex_fields = household_payload.pop("flex_fields", dict())

        flex_fields.update(**self.get_extra_ff(mapping.get("flex_fields", list()), record_data_dict))
        household_data = {
            **household_payload,
            # "flex_registrations_record": record,
            "registration_data_import": str(registration_data_import.pk),
            "business_area": registration_data_import.business_area,
            "program": registration_data_import.program,
            "first_registration_date": record.timestamp,
            "last_registration_date": record.timestamp,
            "country_origin": str(Country.objects.get(iso_code2=mapping["defaults"][COUNTRY]).pk),
            "country": str(Country.objects.get(iso_code2=mapping["defaults"][COUNTRY]).pk),
            "consent": True,
            "flex_fields": flex_fields,
        }
        if constances := mapping.get("household_constances", None):
            household_data.update(constances)
        return self._create_object_and_validate(household_data, PendingHousehold)

    def create_individuals(
        self,
        record: Any,
        household: PendingHousehold,
        mapping: Dict,
    ) -> Tuple:
        base_individual_data_dict = dict(
            household=household,
            registration_data_import=household.registration_data_import,
            business_area=household.business_area,
            program=household.program,
            first_registration_date=record.timestamp,
            last_registration_date=record.timestamp,
            detail_id=record.source_id,
        )

        record_data_dict = record.get_data()
        individuals_key = mapping["defaults"].get("individuals_key", "individuals")
        individuals_data = self.create_individuals_dicts(
            record_data_dict[individuals_key], mapping[individuals_key], mapping
        )

        individuals = []
        head = None
        pr_collector = None
        sec_collector = None

        for individual_data in individuals_data:
            documents_data = individual_data.pop("documents")
            banks_data = individual_data.pop("banks")
            account_data = individual_data.pop("account_details")
            extra_data = individual_data.pop("extra", dict())

            individual_dict = dict(
                **base_individual_data_dict,
                **individual_data,
            )
            if "full_name" not in individual_dict:
                individual_dict["full_name"] = " ".join(
                    [
                        individual_dict[key]
                        for key in ["given_name", "middle_name", "family_name"]
                        if key in individual_dict
                    ]
                )
            if not self.master_detail:
                individual_dict["relationship"] = HEAD
            individual = self._create_object_and_validate(individual_dict, PendingIndividual, IndividualForm)

            if individual.relationship == HEAD:
                if head:
                    raise ValidationError("Head of Household already exist")
                head = individual

            for _, bank_data in banks_data.items():
                bank_data[INDIVIDUAL_FIELD] = individual
                self._create_object_and_validate(bank_data, PendingBankAccountInfo, BankAccountInfoForm)

            for _, document_data in documents_data.items():
                key = document_data.pop("key", None)  # skip documents' without key
                if key:
                    document_data["type"] = DocumentType.objects.get(key=key)
                    document_data[INDIVIDUAL_FIELD] = individual
                    document_data["program"] = individual.program
                    document_data[COUNTRY] = str(Country.objects.get(iso_code2=mapping["defaults"][COUNTRY]).pk)
                    if photo_base_64 := document_data.get("photo", None):
                        document_data["photo"] = self._prepare_picture_from_base64(
                            photo_base_64, document_data.get("document_number", key)
                        )
                    self._create_object_and_validate(document_data, PendingDocument, DocumentForm)

            if account_data:
                financial_institution_code = account_data["data"].get("code", None)
                PendingAccount.objects.create(
                    individual_id=individual.id,
                    account_type=AccountType.objects.get(key="bank"),
                    number=account_data["data"].get("number", None),
                    financial_institution=FinancialInstitution.objects.filter(code=financial_institution_code).first()
                    if financial_institution_code
                    else None,
                    **account_data,
                )

            if self.get_boolean(extra_data.get(PRIMARY_COLLECTOR, False)):
                if pr_collector:
                    raise ValidationError("Primary Collector already exist")
                pr_collector = individual

            if self.get_boolean(extra_data.get(SECONDARY_COLLECTOR, False)):
                if sec_collector:
                    raise ValidationError("Secondary Collector already exist")
                sec_collector = individual

            individuals.append(individual)
        if not self.master_detail:
            assert len(individuals) == 1
            head = pr_collector = individuals[0]
        return individuals, head, pr_collector, sec_collector

    def create_household_for_rdi_household(self, record: Any, registration_data_import: RegistrationDataImport) -> None:
        mapping = mergedicts(self.default_mapping, self.registration.mapping, [])

        household = self.create_household_data(record, registration_data_import, mapping)
        individuals, head, pr_collector, sec_collector = self.create_individuals(
            record,
            household,
            mapping,
        )

        if head:
            household.head_of_household = head

        if pr_collector:
            PendingIndividualRoleInHousehold.objects.create(
                individual=pr_collector, household=household, role=ROLE_PRIMARY
            )
        if sec_collector:
            PendingIndividualRoleInHousehold.objects.create(
                individual=sec_collector, household=household, role=ROLE_ALTERNATE
            )

        household.detail_id = record.source_id
        household.save()
        record.mark_as_imported()
