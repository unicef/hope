import json
import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional, Union

from django.contrib.gis.geos import Point
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction

from dateutil.parser import parse
from django_countries.fields import Country

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.kobo.api import KoboAPI
from hct_mis_api.apps.core.kobo.common import (
    KOBO_FORM_INDIVIDUALS_COLUMN_NAME,
    get_field_name,
    get_submission_metadata,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import chunks, rename_dict_keys
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.geo.models import Country as GeoCountry
from hct_mis_api.apps.household.models import (
    HEAD,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    DocumentType,
    PendingBankAccountInfo,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualIdentity,
    PendingIndividualRoleInHousehold,
)
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.registration_data.models import (
    ImportData,
    KoboImportedSubmission,
    RegistrationDataImport,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.registration_datahub.tasks.rdi_base_create import (
    RdiBaseCreateTask,
)
from hct_mis_api.apps.registration_datahub.utils import (
    calculate_hash_for_kobo_submission,
    find_attachment_in_kobo,
)
from hct_mis_api.apps.utils.age_at_registration import calculate_age_at_registration

logger = logging.getLogger(__name__)


class RdiKoboCreateTask(RdiBaseCreateTask):
    """
    Imports project data from Kobo via a REST API, parsing them and creating
    households/individuals in the Registration Datahub. Once finished it will
    update the status of that registration data import instance.
    """

    def __init__(
        self,
        registration_data_import_id: str,
        business_area_id: str,
    ) -> None:
        document_keys = DocumentType.objects.values_list("key", flat=True)
        self.DOCS_AND_IDENTITIES_FIELDS = [
            f"{key}_{suffix}" for key in document_keys for suffix in ["no_i_c", "photo_i_c", "issuer_i_c"]
        ]
        self.BANK_RELATED_FIELDS = (
            "bank_name_i_c",
            "bank_account_number_i_c",
            "debit_card_number_i_c",
            "bank_branch_name_i_c",
            "account_holder_name_i_c",
        )
        self.registration_data_import = RegistrationDataImport.objects.get(
            id=registration_data_import_id,
        )
        self.business_area = BusinessArea.objects.get(id=business_area_id)

        self.reduced_submissions: List[Any] = []
        self.attachments: List[Dict] = []
        super().__init__()

    def _handle_image_field(self, value: Any, is_flex_field: bool) -> Optional[Union[str, File]]:
        if not self.registration_data_import.pull_pictures:
            return None
        if self.attachments is None:
            return None
        attachment = find_attachment_in_kobo(self.attachments, value)
        if attachment is None:
            return None
        current_download_url = attachment.get("download_url", "")
        download_url = current_download_url.replace("?format=json", "")
        api = KoboAPI()
        image_bytes = api.get_attached_file(download_url)
        file = File(image_bytes, name=value)
        if is_flex_field:
            return default_storage.save(value, file)
        return file

    def _handle_geopoint_field(self, value: Any, is_flex_field: bool) -> Point:
        geopoint = value.split(" ")
        x = float(geopoint[0])
        y = float(geopoint[1])
        return Point(x=x, y=y, srid=4326)

    def _handle_decimal_field(self, value: Any, is_flex_field: bool) -> Any:
        if not is_flex_field:
            return value
        return float(value)

    def _cast_and_assign(
        self, value: Union[str, list], field: str, obj: Union[PendingIndividual, PendingHousehold]
    ) -> None:
        complex_fields = {
            "IMAGE": self._handle_image_field,
            "GEOPOINT": self._handle_geopoint_field,
            "DECIMAL": self._handle_decimal_field,
        }
        excluded = ("age",)

        field_data_dict = self.COMBINED_FIELDS.get(field)

        if field_data_dict is None or field in excluded:
            return

        is_flex_field = field.endswith(("_i_f", "_h_f"))

        if field_data_dict["type"] in complex_fields:
            cast_fn = complex_fields.get(field_data_dict["type"])
            correct_value = cast_fn(value, is_flex_field)
        elif field_data_dict["name"] in ["admin1", "admin2", "admin3", "admin4"]:
            correct_value = Area.objects.get(p_code=value)
        elif field_data_dict["name"] in ["country", "country_origin"]:
            correct_value = GeoCountry.objects.get(iso_code2=Country(value).code)
        else:
            correct_value = self._cast_value(value, field)

        if is_flex_field:
            obj.flex_fields[field_data_dict["name"]] = correct_value
        else:
            setattr(obj, field_data_dict["name"], correct_value)

    def _handle_documents_and_identities(self, documents_and_identities: List) -> None:
        identity_fields = {
            "scope_id",
            "unhcr_id",
        }

        documents = []
        identities = []
        for documents_dict in documents_and_identities:
            for document_name, data in documents_dict.items():
                if not PendingIndividual.objects.filter(id=data["individual"].id).exists():
                    continue

                is_identity = document_name in identity_fields

                if country := data.get("issuing_country"):
                    data["country"] = GeoCountry.objects.get(iso_code2=Country(country).code)

                if is_identity:
                    partner = "WFP" if document_name == "scope_id" else "UNHCR"
                    identities.append(
                        PendingIndividualIdentity(
                            partner=partner,
                            individual=data["individual"],
                            document_number=data.get("number", ""),
                            country=data.get("country"),
                        )
                    )
                    continue
                document_type = DocumentType.objects.get(key=document_name)
                file = self._handle_image_field(data.get("photo", ""), False)
                documents.append(
                    PendingDocument(
                        document_number=data.get("number", ""),
                        photo=file,
                        individual=data["individual"],
                        type=document_type,
                        program=data["individual"].program,
                        country=data.get("country"),
                    )
                )
        PendingDocument.objects.bulk_create(documents)
        PendingIndividualIdentity.objects.bulk_create(identities)

    @staticmethod
    def _handle_collectors(collectors_dict: Dict, individuals_dict: Dict) -> None:
        collectors_to_bulk_create = []
        for hash_key, collectors_list in collectors_dict.items():
            for collector in collectors_list:
                collector.individual_id = individuals_dict.get(hash_key)
                collectors_to_bulk_create.append(collector)
        PendingIndividualRoleInHousehold.objects.bulk_create(collectors_to_bulk_create)

    @transaction.atomic()
    def execute(
        self,
        import_data_id: str,
        program_id: Optional[str] = None,
    ) -> None:
        self.registration_data_import.status = RegistrationDataImport.IMPORTING
        self.registration_data_import.save()

        import_data = ImportData.objects.get(id=import_data_id)

        submissions_json = import_data.file.read()
        submissions = json.loads(submissions_json)
        self.reduced_submissions = rename_dict_keys(submissions, get_field_name)
        head_of_households_mapping = {}
        households_to_create = []
        individuals_ids_hash_dict = {}
        bank_accounts_to_create = []
        collectors_to_create = defaultdict(list)
        household_hash_list = []
        household_batch_size = 50
        for reduced_submission_chunk in chunks(self.reduced_submissions, household_batch_size):
            for household in reduced_submission_chunk:
                # AB#199540
                household_hash = calculate_hash_for_kobo_submission(household)
                submission_duplicate = household_hash in household_hash_list
                if submission_duplicate:
                    continue
                household_hash_list.append(household_hash)

                submission_meta_data = get_submission_metadata(household)
                if self.business_area.get_sys_option("ignore_amended_kobo_submissions"):
                    submission_meta_data["amended"] = False

                if KoboImportedSubmission.objects.filter(**submission_meta_data).exists():
                    continue

                submission_meta_data.pop("amended", None)
                self.handle_household(
                    bank_accounts_to_create,
                    collectors_to_create,
                    head_of_households_mapping,
                    household,
                    households_to_create,
                    individuals_ids_hash_dict,
                    submission_meta_data,
                )
            self.bulk_creates(bank_accounts_to_create, head_of_households_mapping, households_to_create)
            bank_accounts_to_create = []
            head_of_households_mapping = {}
            households_to_create = []
        self._handle_collectors(collectors_to_create, individuals_ids_hash_dict)

        rdi_mis = RegistrationDataImport.objects.get(id=self.registration_data_import.id)
        rdi_mis.status = RegistrationDataImport.IN_REVIEW
        rdi_mis.save()

        rdi_mis.bulk_update_household_size()

        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING,
            "business_area",
            None,
            self.registration_data_import.program_id,
            self.registration_data_import,
            rdi_mis,
        )
        if not self.business_area.postpone_deduplication:
            DeduplicateTask(self.business_area.slug, str(program_id)).deduplicate_pending_individuals(
                registration_data_import=self.registration_data_import
            )

    def bulk_creates(
        self,
        bank_accounts_to_create: list[PendingBankAccountInfo],
        head_of_households_mapping: dict,
        households_to_create: list[PendingHousehold],
    ) -> None:
        PendingHousehold.objects.bulk_create(households_to_create)
        households_to_update = []
        for household, individual in head_of_households_mapping.items():
            household.head_of_household = individual
            households_to_update.append(household)
        PendingHousehold.objects.bulk_update(
            households_to_update,
            ["head_of_household"],
        )
        PendingBankAccountInfo.objects.bulk_create(bank_accounts_to_create)

    def handle_household(
        self,
        bank_accounts_to_create: list[PendingBankAccountInfo],
        collectors_to_create: dict,
        head_of_households_mapping: dict,
        household: dict,
        households_to_create: list[PendingHousehold],
        individuals_ids_hash_dict: dict,
        submission_meta_data: dict,
    ) -> None:
        individuals_to_create_list = []
        documents_and_identities_to_create = []
        submission_meta_data["detail_id"] = submission_meta_data.pop("kobo_asset_id", "")
        household_obj = PendingHousehold(**submission_meta_data)
        self.attachments = household.get("_attachments", [])
        registration_date = None
        current_individuals = []
        for hh_field, hh_value in household.items():
            if hh_field == KOBO_FORM_INDIVIDUALS_COLUMN_NAME:
                for individual in hh_value:
                    current_individual_docs_and_identities = defaultdict(dict)
                    current_individual_bank_account = {}
                    individual_obj = PendingIndividual()
                    only_collector_flag = False
                    role = None
                    for i_field, i_value in individual.items():
                        if i_field in self.DOCS_AND_IDENTITIES_FIELDS:
                            key = (
                                i_field.replace("_photo_i_c", "")
                                .replace("_no_i_c", "")
                                .replace("_issuer_i_c", "")
                                .replace("_i_c", "")
                            )
                            if i_field.endswith("_type_i_c"):
                                value_key = "name"
                            elif i_field.endswith("_photo_i_c"):
                                value_key = "photo"
                            elif i_field.endswith("_issuer_i_c"):
                                value_key = "issuing_country"
                            else:
                                value_key = "number"
                            current_individual_docs_and_identities[key][value_key] = i_value
                            current_individual_docs_and_identities[key]["individual"] = individual_obj
                        elif i_field == "relationship_i_c" and i_value.upper() == NON_BENEFICIARY:
                            only_collector_flag = True
                        elif i_field == "role_i_c":
                            role = i_value.upper()
                        elif i_field in self.BANK_RELATED_FIELDS:
                            name = i_field.replace("_i_c", "")
                            current_individual_bank_account["individual"] = individual_obj
                            current_individual_bank_account[name] = i_value
                        elif i_field.endswith("_h_c") or i_field.endswith("_h_f"):
                            try:
                                self._cast_and_assign(i_value, i_field, household_obj)
                            except Exception as e:
                                self._handle_exception("Household", i_field, e)
                        else:
                            try:
                                self._cast_and_assign(i_value, i_field, individual_obj)
                            except Exception as e:
                                self._handle_exception("Individual", i_field, e)
                    individual_obj.last_registration_date = individual_obj.first_registration_date
                    individual_obj.registration_data_import = self.registration_data_import
                    individual_obj.program = self.registration_data_import.program
                    individual_obj.business_area = self.business_area
                    individual_obj.age_at_registration = calculate_age_at_registration(
                        self.registration_data_import.created_at, str(individual_obj.birth_date)
                    )
                    populate_pdu_with_null_values(self.registration_data_import.program, individual_obj.flex_fields)

                    if individual_obj.relationship == HEAD:
                        head_of_households_mapping[household_obj] = individual_obj

                    individual_obj.household = household_obj if only_collector_flag is False else None

                    individuals_ids_hash_dict[individual_obj.get_hash_key] = individual_obj.id
                    individuals_to_create_list.append(individual_obj)
                    current_individuals.append(individual_obj)
                    documents_and_identities_to_create.append(current_individual_docs_and_identities)
                    if current_individual_bank_account:
                        bank_accounts_to_create.append(PendingBankAccountInfo(**current_individual_bank_account))
                    if role in (ROLE_PRIMARY, ROLE_ALTERNATE):
                        role_obj = PendingIndividualRoleInHousehold(
                            individual_id=individual_obj.pk,
                            household_id=household_obj.pk,
                            role=role,
                        )
                        collectors_to_create[individual_obj.get_hash_key].append(role_obj)
                    if individual_obj.household is None:
                        individual_obj.relationship = NON_BENEFICIARY

            elif hh_field == "end":
                registration_date = parse(hh_value)
            elif hh_field == "start":
                household_obj.start = parse(hh_value)
            elif hh_field == "_submission_time":
                household_obj.kobo_submission_time = parse(hh_value)
            else:
                try:
                    self._cast_and_assign(hh_value, hh_field, household_obj)
                except Exception as e:
                    self._handle_exception("Household", hh_field, e)
        household_obj.first_registration_date = registration_date
        household_obj.last_registration_date = registration_date
        household_obj.registration_data_import = self.registration_data_import
        household_obj.program = self.registration_data_import.program
        household_obj.business_area = self.business_area
        household_obj.set_admin_areas()
        households_to_create.append(household_obj)
        for ind in current_individuals:
            ind.first_registration_date = registration_date
            ind.last_registration_date = registration_date
            ind.detail_id = household_obj.detail_id
        PendingIndividual.objects.bulk_create(individuals_to_create_list)
        self._handle_documents_and_identities(documents_and_identities_to_create)

    def _handle_exception(self, assigned_to: str, field_name: str, e: BaseException) -> None:
        logger.warning(e)
        raise Exception(f"Error processing {assigned_to}: field `{field_name}` {e.__class__.__name__}({e})") from e
