import json
import logging
from collections import defaultdict
from typing import Any

from dateutil.parser import parse
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction
from django_countries.fields import Country

from hope.apps.activity_log.models import log_create
from hope.apps.core.kobo.api import KoboAPI
from hope.apps.core.kobo.common import (
    KOBO_FORM_INDIVIDUALS_COLUMN_NAME,
    get_field_name,
    get_submission_metadata,
)
from hope.apps.core.models import BusinessArea
from hope.apps.core.utils import chunks, rename_dict_keys
from hope.apps.geo.models import Area
from hope.apps.geo.models import Country as GeoCountry
from hope.apps.household.models import (
    HEAD,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualIdentity,
    PendingIndividualRoleInHousehold,
)
from hope.apps.payment.models import Account
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.apps.registration_data.models import (
    ImportData,
    KoboImportedSubmission,
    RegistrationDataImport,
)
from hope.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hope.apps.registration_datahub.tasks.rdi_base_create import RdiBaseCreateTask
from hope.apps.registration_datahub.utils import (
    calculate_hash_for_kobo_submission,
    find_attachment_in_kobo,
)
from hope.apps.utils.age_at_registration import calculate_age_at_registration

logger = logging.getLogger(__name__)


class RdiKoboCreateTask(RdiBaseCreateTask):
    """Import project data from Kobo via a REST API, parsing them and creating households/individuals.

    Once finished it will update the status of that registration data import instance.
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
        self.registration_data_import = RegistrationDataImport.objects.get(
            id=registration_data_import_id,
        )
        self.business_area = BusinessArea.objects.get(id=business_area_id)

        self.reduced_submissions: list[Any] = []
        self.attachments: list[dict] = []
        super().__init__()

    def _handle_image_field(self, value: Any, is_flex_field: bool) -> str | File | None:
        logger.info(f"Processing image field: {value}")
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
        logger.info(f"Image field processed: {value}")
        return file

    def _handle_geopoint_field(self, value: Any, is_flex_field: bool) -> tuple[float, float]:
        geopoint = value.split(" ")
        x = float(geopoint[0])
        y = float(geopoint[1])
        return x, y

    def _handle_decimal_field(self, value: Any, is_flex_field: bool) -> Any:
        if not is_flex_field:
            return value
        return float(value)

    def _cast_and_assign(self, value: str | list, field: str, obj: PendingIndividual | PendingHousehold) -> None:
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
            # TODO remove later, fix for DRC program Paiement des ASC et IT
            # https://unicef.visualstudio.com/ICTD-HCT-MIS/_workitems/edit/260434/
            if str(self.registration_data_import.program_id) == "f5a67047-714f-459a-8ead-911d21f7925c":
                value = self._get_drc_mapped_admin_pcode_value(field_data_dict["name"], value)  # type: ignore
            correct_value = Area.objects.get(p_code=value)
        elif field_data_dict["name"] in ["country", "country_origin"]:
            correct_value = GeoCountry.objects.get(iso_code2=Country(value).code)
        else:
            correct_value = self._cast_value(value, field)

        if is_flex_field:
            obj.flex_fields[field_data_dict["name"]] = correct_value
        else:
            setattr(obj, field_data_dict["name"], correct_value)

    def _handle_documents_and_identities(self, documents_and_identities: list) -> None:
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
    def _handle_collectors(collectors_dict: dict, individuals_dict: dict) -> None:
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
        program_id: str | None = None,
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
        collectors_to_create = defaultdict(list)
        household_hash_list = []
        household_batch_size = 50
        logger.info(f"Processing {len(self.reduced_submissions)} households")
        chunk_index = 0
        household_count = 0
        for reduced_submission_chunk in chunks(self.reduced_submissions, household_batch_size):
            chunk_index += 1
            logger.info(f"Processing chunk {chunk_index}/{len(self.reduced_submissions) // household_batch_size}")
            for household in reduced_submission_chunk:
                household_count += 1
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
                    collectors_to_create,
                    head_of_households_mapping,
                    household,
                    households_to_create,
                    individuals_ids_hash_dict,
                    submission_meta_data,
                    household_count,
                )
            self.bulk_creates(head_of_households_mapping, households_to_create)
            head_of_households_mapping = {}
            households_to_create = []
        self._handle_collectors(collectors_to_create, individuals_ids_hash_dict)
        self._create_accounts()

        rdi_mis = RegistrationDataImport.objects.get(id=self.registration_data_import.id)
        rdi_mis.status = RegistrationDataImport.IN_REVIEW
        rdi_mis.number_of_individuals = PendingIndividual.objects.filter(registration_data_import=rdi_mis).count()
        rdi_mis.number_of_households = PendingHousehold.objects.filter(registration_data_import=rdi_mis).count()
        rdi_mis.save(update_fields=["status", "number_of_individuals", "number_of_households"])

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

    def handle_household(
        self,
        collectors_to_create: dict,
        head_of_households_mapping: dict,
        household: dict,
        households_to_create: list[PendingHousehold],
        individuals_ids_hash_dict: dict,
        submission_meta_data: dict,
        household_count: int,
    ) -> None:
        individuals_to_create_list = []
        documents_and_identities_to_create = []
        submission_meta_data["detail_id"] = submission_meta_data.pop("kobo_asset_id", "")
        household_obj = PendingHousehold(**submission_meta_data)
        self.attachments = household.get("_attachments", [])
        registration_date = None
        current_individuals = []
        ind_count = 0
        for hh_field, hh_value in household.items():
            if hh_field == KOBO_FORM_INDIVIDUALS_COLUMN_NAME:
                for individual in hh_value:
                    ind_count += 1
                    current_individual_docs_and_identities = defaultdict(dict)
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
                        elif i_field.endswith(("_h_c", "_h_f")):
                            try:
                                self._cast_and_assign(i_value, i_field, household_obj)
                            except Exception as e:
                                self._handle_exception("Household", i_field, e)
                        elif i_field.startswith(Account.ACCOUNT_FIELD_PREFIX):
                            self._handle_delivery_mechanism_fields(
                                i_value,
                                i_field,
                                int(f"{household_count}{ind_count}"),
                                individual_obj,
                            )
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
                        self.registration_data_import.created_at,
                        str(individual_obj.birth_date),
                    )
                    populate_pdu_with_null_values(
                        self.registration_data_import.program,
                        individual_obj.flex_fields,
                    )

                    if individual_obj.relationship == HEAD:
                        head_of_households_mapping[household_obj] = individual_obj

                    individual_obj.household = household_obj if only_collector_flag is False else None

                    individuals_ids_hash_dict[individual_obj.get_hash_key] = individual_obj.id
                    individuals_to_create_list.append(individual_obj)
                    current_individuals.append(individual_obj)
                    documents_and_identities_to_create.append(current_individual_docs_and_identities)
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
        household_obj.set_admin_areas(save=False)
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

    def _get_drc_mapped_admin_pcode_value(self, admin_field: str, value: str) -> str:
        mapping = {
            "admin1": {},
            "admin2": {},
            "admin3": {
                "CD8309ZS01": "CD8311ZS02",
                "CD8202ZS01": "CD8201ZS01",
                "CD6311ZS01": "CD6311ZS06",
                "CD6313ZS01": "CD6311ZS09",
                "CD8306ZS02": "CD8303ZS03",
                "CD8307ZS01": "CD8303ZS11",
                "CD6309ZS02": "CD6311ZS07",
                "CD8205ZS02": "CD8201ZS03",
                "CD8302ZS02": "CD8303ZS01",
                "CD6307ZS03": "CD6301ZS01",
                "CD8308ZS02": "CD8311ZS03",
                "CD8306ZS01": "CD8303ZS02",
                "CD8303ZS01": "CD8303ZS06",
                "CD8307ZS02": "CD8303ZS04",
                "CD8309ZS03": "CD8311ZS01",
            },
            "admin4": {
                "CD8309ZS01AS01": "CD8311ZS02AS04",
                "CD8309ZS01AS02": "CD8311ZS02AS10",
                "CD8309ZS01AS03": "CD8311ZS02AS01",
                "CD8309ZS01AS04": "CD8311ZS02AS05",
                "CD8309ZS01AS05": "CD8311ZS02AS08",
                "CD8309ZS01AS06": "CD8311ZS02AS14",
                "CD8309ZS01AS07": "CD8311ZS02AS17",
                "CD8309ZS01AS08": "CD8311ZS02AS13",
                "CD8309ZS01AS09": "CD8311ZS02AS07",
                "CD8309ZS01AS10": "CD8311ZS02AS09",
                "CD8309ZS01AS11": "CD8311ZS02AS15",
                "CD8309ZS01AS12": "CD8311ZS02AS11",
                "CD8309ZS01AS13": "CD8311ZS02AS06",
                "CD8309ZS01AS14": "CD8311ZS02AS02",
                "CD8309ZS01AS15": "CD8311ZS02AS03",
                "CD8309ZS01AS16": "CD8311ZS02AS12",
                "CD8309ZS01AS17": "CD8311ZS02AS16",
                "CD8202ZS01AS01": "CD8201ZS01AS03",
                "CD8202ZS01AS02": "CD8201ZS01AS17",
                "CD8202ZS01AS03": "CD8201ZS01AS11",
                "CD8202ZS01AS04": "CD8201ZS01AS16",
                "CD8202ZS01AS05": "CD8201ZS01AS10",
                "CD8202ZS01AS06": "CD8201ZS01AS14",
                "CD8202ZS01AS07": "CD8201ZS01AS01",
                "CD8202ZS01AS08": "CD8201ZS01AS07",
                "CD8202ZS01AS09": "CD8201ZS01AS09",
                "CD8202ZS01AS10": "CD8201ZS01AS06",
                "CD8202ZS01AS11": "CD8201ZS01AS05",
                "CD8202ZS01AS12": "CD8201ZS01AS15",
                "CD8202ZS01AS13": "CD8201ZS01AS13",
                "CD8202ZS01AS14": "CD8201ZS01AS04",
                "CD8202ZS01AS15": "CD8201ZS01AS08",
                "CD8202ZS01AS16": "CD8201ZS01AS12",
                "CD8202ZS01AS17": "CD8201ZS01AS02",
                "CD8202ZS01AS18": "CD8201ZS01AS18",
                "CD6311ZS01AS01": "CD6311ZS06AS15",
                "CD6311ZS01AS02": "CD6311ZS06AS19",
                "CD6311ZS01AS03": "CD6311ZS06AS06",
                "CD6311ZS01AS04": "CD6311ZS06AS21",
                "CD6311ZS01AS05": "CD6311ZS06AS08",
                "CD6311ZS01AS06": "CD6311ZS06AS05",
                "CD6311ZS01AS07": "CD6311ZS06AS10",
                "CD6311ZS01AS08": "CD6311ZS06AS14",
                "CD6311ZS01AS09": "CD6311ZS06AS13",
                "CD6311ZS01AS10": "CD6311ZS06AS03",
                "CD6311ZS01AS11": "CD6311ZS06AS12",
                "CD6311ZS01AS12": "CD6311ZS06AS18",
                "CD6311ZS01AS13": "CD6311ZS06AS11",
                "CD6311ZS01AS14": "CD6311ZS06AS07",
                "CD6311ZS01AS15": "CD6311ZS06AS02",
                "CD6311ZS01AS16": "CD6311ZS06AS17",
                "CD6311ZS01AS17": "CD6311ZS06AS09",
                "CD6311ZS01AS18": "CD6311ZS06AS04",
                "CD6311ZS01AS19": "CD6311ZS06AS20",
                "CD6311ZS01AS20": "CD6311ZS06AS16",
                "CD6311ZS01AS21": "CD6311ZS06AS01",
                "CD6313ZS01AS01": "CD6311ZS09AS06",
                "CD6313ZS01AS02": "CD6311ZS09AS02",
                "CD6313ZS01AS03": "CD6311ZS09AS12",
                "CD6313ZS01AS04": "CD6311ZS09AS10",
                "CD6313ZS01AS05": "CD6311ZS09AS03",
                "CD6313ZS01AS06": "CD6311ZS09AS08",
                "CD6313ZS01AS07": "CD6311ZS09AS05",
                "CD6313ZS01AS08": "CD6311ZS09AS07",
                "CD6313ZS01AS09": "CD6311ZS09AS01",
                "CD6313ZS01AS10": "CD6311ZS09AS11",
                "CD6313ZS01AS11": "CD6311ZS09AS09",
                "CD6313ZS01AS12": "CD6311ZS09AS04",
                "CD8306ZS02AS01": "CD8303ZS03AS01",
                "CD8306ZS02AS02": "CD8303ZS03AS08",
                "CD8306ZS02AS03": "CD8303ZS03AS04",
                "CD8306ZS02AS04": "CD8303ZS03AS11",
                "CD8306ZS02AS05": "CD8303ZS03AS02",
                "CD8306ZS02AS06": "CD8303ZS03AS03",
                "CD8306ZS02AS07": "CD8303ZS03AS06",
                "CD8306ZS02AS08": "CD8303ZS03AS10",
                "CD8306ZS02AS09": "CD8303ZS03AS12",
                "CD8306ZS02AS10": "CD8303ZS03AS05",
                "CD8306ZS02AS11": "CD8303ZS03AS07",
                "CD8306ZS02AS12": "CD8303ZS03AS09",
                "CD8307ZS01AS01": "CD8303ZS11AS15",
                "CD8307ZS01AS02": "CD8303ZS11AS06",
                "CD8307ZS01AS03": "CD8303ZS11AS01",
                "CD8307ZS01AS04": "CD8303ZS11AS16",
                "CD8307ZS01AS05": "CD8303ZS11AS13",
                "CD8307ZS01AS06": "CD8303ZS11AS04",
                "CD8307ZS01AS07": "CD8303ZS11AS11",
                "CD8307ZS01AS08": "CD8303ZS11AS17",
                "CD8307ZS01AS09": "CD8303ZS11AS19",
                "CD8307ZS01AS10": "CD8303ZS11AS02",
                "CD8307ZS01AS11": "CD8303ZS11AS14",
                "CD8307ZS01AS12": "CD8303ZS11AS18",
                "CD8307ZS01AS13": "CD8303ZS11AS12",
                "CD8307ZS01AS14": "CD8303ZS11AS07",
                "CD8307ZS01AS15": "CD8303ZS11AS05",
                "CD8307ZS01AS16": "CD8303ZS11AS09",
                "CD8307ZS01AS17": "CD8303ZS11AS03",
                "CD8307ZS01AS18": "CD8303ZS11AS10",
                "CD8307ZS01AS19": "CD8303ZS11AS08",
                "CD6309ZS02AS01": "CD6311ZS07AS18",
                "CD6309ZS02AS02": "CD6311ZS07AS01",
                "CD6309ZS02AS03": "CD6311ZS07AS11",
                "CD6309ZS02AS04": "CD6311ZS07AS04",
                "CD6309ZS02AS05": "CD6311ZS07AS03",
                "CD6309ZS02AS06": "CD6311ZS07AS06",
                "CD6309ZS02AS07": "CD6311ZS07AS13",
                "CD6309ZS02AS08": "CD6311ZS07AS08",
                "CD6309ZS02AS09": "CD6311ZS07AS09",
                "CD6309ZS02AS10": "CD6311ZS07AS15",
                "CD6309ZS02AS11": "CD6311ZS07AS05",
                "CD6309ZS02AS12": "CD6311ZS07AS16",
                "CD6309ZS02AS13": "CD6311ZS07AS10",
                "CD6309ZS02AS14": "CD6311ZS07AS14",
                "CD6309ZS02AS15": "CD6311ZS07AS07",
                "CD6309ZS02AS16": "CD6311ZS07AS02",
                "CD6309ZS02AS17": "CD6311ZS07AS12",
                "CD6309ZS02AS18": "CD6311ZS07AS17",
                "CD8205ZS02AS01": "CD8201ZS03AS11",
                "CD8205ZS02AS02": "CD8201ZS03AS12",
                "CD8205ZS02AS03": "CD8201ZS03AS06",
                "CD8205ZS02AS04": "CD8201ZS03AS07",
                "CD8205ZS02AS05": "CD8201ZS03AS05",
                "CD8205ZS02AS06": "CD8201ZS03AS13",
                "CD8205ZS02AS07": "CD8201ZS03AS10",
                "CD8205ZS02AS08": "CD8201ZS03AS08",
                "CD8205ZS02AS09": "CD8201ZS03AS01",
                "CD8205ZS02AS10": "CD8201ZS03AS04",
                "CD8205ZS02AS11": "CD8201ZS03AS02",
                "CD8205ZS02AS12": "CD8201ZS03AS14",
                "CD8205ZS02AS13": "CD8201ZS03AS09",
                "CD8205ZS02AS14": "CD8201ZS03AS03",
                "CD8302ZS02AS01": "CD8303ZS01AS04",
                "CD8302ZS02AS02": "CD8303ZS01AS13",
                "CD8302ZS02AS03": "CD8303ZS01AS14",
                "CD8302ZS02AS04": "CD8303ZS01AS08",
                "CD8302ZS02AS05": "CD8303ZS01AS10",
                "CD8302ZS02AS06": "CD8303ZS01AS06",
                "CD8302ZS02AS07": "CD8303ZS01AS17",
                "CD8302ZS02AS08": "CD8303ZS01AS15",
                "CD8302ZS02AS09": "CD8303ZS01AS05",
                "CD8302ZS02AS10": "CD8303ZS01AS02",
                "CD8302ZS02AS11": "CD8303ZS01AS09",
                "CD8302ZS02AS12": "CD8303ZS01AS01",
                "CD8302ZS02AS13": "CD8303ZS01AS03",
                "CD8302ZS02AS14": "CD8303ZS01AS16",
                "CD8302ZS02AS15": "CD8303ZS01AS11",
                "CD8302ZS02AS16": "CD8303ZS01AS07",
                "CD8302ZS02AS17": "CD8303ZS01AS12",
                "CD6307ZS03AS01": "CD6301ZS01AS12",
                "CD6307ZS03AS02": "CD6301ZS01AS10",
                "CD6307ZS03AS03": "CD6301ZS01AS08",
                "CD6307ZS03AS04": "CD6301ZS01AS07",
                "CD6307ZS03AS05": "CD6301ZS01AS06",
                "CD6307ZS03AS06": "CD6301ZS01AS09",
                "CD6307ZS03AS07": "CD6301ZS01AS11",
                "CD6307ZS03AS08": "CD6301ZS01AS13",
                "CD6307ZS03AS09": "CD6301ZS01AS04",
                "CD6307ZS03AS10": "CD6301ZS01AS16",
                "CD6307ZS03AS11": "CD6301ZS01AS03",
                "CD6307ZS03AS12": "CD6301ZS01AS01",
                "CD6307ZS03AS13": "CD6301ZS01AS15",
                "CD6307ZS03AS14": "CD6301ZS01AS05",
                "CD6307ZS03AS15": "CD6301ZS01AS14",
                "CD8306ZS01AS01": "CD8303ZS02AS09",
                "CD8306ZS01AS02": "CD8303ZS02AS01",
                "CD8306ZS01AS03": "CD8303ZS02AS05",
                "CD8306ZS01AS04": "CD8303ZS02AS08",
                "CD8306ZS01AS05": "CD8303ZS02AS06",
                "CD8306ZS01AS06": "CD8303ZS02AS13",
                "CD8306ZS01AS07": "CD8303ZS02AS03",
                "CD8306ZS01AS08": "CD8303ZS02AS04",
                "CD8306ZS01AS09": "CD8303ZS02AS02",
                "CD8306ZS01AS10": "CD8303ZS02AS12",
                "CD8306ZS01AS11": "CD8303ZS02AS10",
                "CD8306ZS01AS12": "CD8303ZS02AS07",
                "CD8306ZS01AS13": "CD8303ZS02AS11",
                "CD8308ZS02AS01": "CD8311ZS03AS08",
                "CD8308ZS02AS02": "CD8311ZS03AS05",
                "CD8308ZS02AS03": "CD8311ZS03AS13",
                "CD8308ZS02AS04": "CD8311ZS03AS10",
                "CD8308ZS02AS05": "CD8311ZS03AS02",
                "CD8308ZS02AS06": "CD8311ZS03AS16",
                "CD8308ZS02AS07": "CD8311ZS03AS14",
                "CD8308ZS02AS08": "CD8311ZS03AS09",
                "CD8308ZS02AS09": "CD8311ZS03AS12",
                "CD8308ZS02AS10": "CD8311ZS03AS03",
                "CD8308ZS02AS11": "CD8311ZS03AS17",
                "CD8308ZS02AS12": "CD8311ZS03AS15",
                "CD8308ZS02AS13": "CD8311ZS03AS06",
                "CD8308ZS02AS14": "CD8311ZS03AS11",
                "CD8308ZS02AS15": "CD8311ZS03AS01",
                "CD8308ZS02AS16": "CD8311ZS03AS07",
                "CD8308ZS02AS17": "CD8311ZS03AS04",
                "CD8303ZS01AS01": "CD8303ZS06AS09",
                "CD8303ZS01AS02": "CD8303ZS06AS15",
                "CD8303ZS01AS03": "CD8303ZS06AS22",
                "CD8303ZS01AS04": "CD8303ZS06AS16",
                "CD8303ZS01AS05": "CD8303ZS06AS08",
                "CD8303ZS01AS06": "CD8303ZS06AS12",
                "CD8303ZS01AS07": "CD8303ZS06AS21",
                "CD8303ZS01AS08": "CD8303ZS06AS17",
                "CD8303ZS01AS09": "CD8303ZS06AS18",
                "CD8303ZS01AS10": "CD8303ZS06AS14",
                "CD8303ZS01AS11": "CD8303ZS06AS11",
                "CD8303ZS01AS12": "CD8303ZS06AS01",
                "CD8303ZS01AS13": "CD8303ZS06AS07",
                "CD8303ZS01AS14": "CD8303ZS06AS06",
                "CD8303ZS01AS15": "CD8303ZS06AS02",
                "CD8303ZS01AS16": "CD8303ZS06AS03",
                "CD8303ZS01AS17": "CD8303ZS06AS10",
                "CD8303ZS01AS18": "CD8303ZS06AS13",
                "CD8303ZS01AS19": "CD8303ZS06AS04",
                "CD8303ZS01AS20": "CD8303ZS06AS19",
                "CD8303ZS01AS21": "CD8303ZS06AS05",
                "CD8303ZS01AS22": "CD8303ZS06AS20",
                "CD8307ZS02AS01": "CD8303ZS04AS02",
                "CD8307ZS02AS02": "CD8303ZS04AS10",
                "CD8307ZS02AS03": "CD8303ZS04AS08",
                "CD8307ZS02AS04": "CD8303ZS04AS01",
                "CD8307ZS02AS05": "CD8303ZS04AS04",
                "CD8307ZS02AS06": "CD8303ZS04AS06",
                "CD8307ZS02AS07": "CD8303ZS04AS03",
                "CD8307ZS02AS08": "CD8303ZS04AS07",
                "CD8307ZS02AS09": "CD8303ZS04AS05",
                "CD8307ZS02AS10": "CD8303ZS04AS09",
                "CD8307ZS02AS11": "CD8303ZS04AS11",
                "CD8309ZS03AS01": "CD8311ZS01AS01",
                "CD8309ZS03AS02": "CD8311ZS01AS11",
                "CD8309ZS03AS03": "CD8311ZS01AS03",
                "CD8309ZS03AS04": "CD8311ZS01AS12",
                "CD8309ZS03AS05": "CD8311ZS01AS08",
                "CD8309ZS03AS06": "CD8311ZS01AS06",
                "CD8309ZS03AS07": "CD8311ZS01AS14",
                "CD8309ZS03AS08": "CD8311ZS01AS04",
                "CD8309ZS03AS09": "CD8311ZS01AS07",
                "CD8309ZS03AS10": "CD8311ZS01AS13",
                "CD8309ZS03AS11": "CD8311ZS01AS10",
                "CD8309ZS03AS12": "CD8311ZS01AS05",
                "CD8309ZS03AS13": "CD8311ZS01AS09",
                "CD8309ZS03AS14": "CD8311ZS01AS02",
            },
        }
        return mapping[admin_field].get(value, value)  # type: ignore
