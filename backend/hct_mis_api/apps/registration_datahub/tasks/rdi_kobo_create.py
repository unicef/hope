import json
import numbers
from collections import defaultdict
from typing import Union

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
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import rename_dict_keys
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_DICT,
    IDENTIFICATION_TYPE_OTHER,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    ImportedAgency,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualIdentity,
    ImportedIndividualRoleInHousehold,
    KoboImportedSubmission,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.registration_datahub.tasks.rdi_base_create import (
    RdiBaseCreateTask,
    logger,
)
from hct_mis_api.apps.registration_datahub.tasks.utils import get_submission_metadata


class RdiKoboCreateTask(RdiBaseCreateTask):
    """
    Imports project data from Kobo via a REST API, parsing them and creating
    households/individuals in the Registration Datahub. Once finished it will
    update the status of that registration data import instance.
    """

    DOCS_AND_IDENTITIES_FIELDS = {
        "birth_certificate_no_i_c",
        "birth_certificate_photo_i_c",
        "birth_certificate_issuer_i_c",
        "drivers_license_no_i_c",
        "drivers_license_photo_i_c",
        "drivers_license_issuer_i_c",
        "electoral_card_no_i_c",
        "electoral_card_photo_i_c",
        "electoral_card_issuer_i_c",
        "unhcr_id_no_i_c",
        "unhcr_id_photo_i_c",
        "unhcr_id_issuer_i_c",
        "national_id_no_i_c",
        "national_id_photo_i_c",
        "national_id_issuer_i_c",
        "national_passport_i_c",
        "national_passport_photo_i_c",
        "national_passport_issuer_i_c",
        "scope_id_no_i_c",
        "scope_id_photo_i_c",
        "scope_id_issuer_i_c",
        "other_id_type_i_c",
        "other_id_no_i_c",
        "other_id_photo_i_c",
        "other_id_issuer_i_c",
    }

    reduced_submissions = None
    business_area = None
    attachments = None

    def _handle_image_field(self, value, is_flex_field):
        if not self.registration_data_import_mis.pull_pictures:
            return None
        download_url = ""
        for attachment in self.attachments:
            filename = attachment.get("filename", "")
            current_download_url = attachment.get("download_url", "")
            if filename.endswith(value):
                download_url = current_download_url.replace("?format=json", "")

        if not download_url:
            return download_url

        api = KoboAPI(self.business_area.slug)
        image_bytes = api.get_attached_file(download_url)
        file = File(image_bytes, name=value)
        if is_flex_field:
            return default_storage.save(value, file)
        return file

    def _handle_geopoint_field(self, value, is_flex_field):
        geopoint = value.split(" ")
        x = float(geopoint[0])
        y = float(geopoint[1])
        return Point(x=x, y=y, srid=4326)

    def _handle_decimal_field(self, value, is_flex_field):
        if not is_flex_field:
            return value
        if isinstance(value, numbers.Number):
            return float(value)
        return value

    def _cast_and_assign(self, value: Union[str, list], field: str, obj: Union[ImportedIndividual, ImportedHousehold]):
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
        else:
            correct_value = self._cast_value(value, field)

        if is_flex_field:
            obj.flex_fields[field_data_dict["name"]] = correct_value
        else:
            setattr(obj, field_data_dict["name"], correct_value)

    def _handle_documents_and_identities(self, documents_and_identities):
        identity_fields = {
            "scope_id",
            "unhcr_id",
        }

        documents = []
        identities = []
        for documents_dict in documents_and_identities:
            for document_name, data in documents_dict.items():
                if not ImportedIndividual.objects.filter(id=data["individual"].id).exists():
                    continue

                is_identity = document_name in identity_fields

                if is_identity:
                    agency, _ = ImportedAgency.objects.get_or_create(
                        type="WFP" if document_name == "scope_id" else "UNHCR", country=Country(data["issuing_country"])
                    )
                    identities.append(
                        ImportedIndividualIdentity(
                            agency=agency,
                            individual=data["individual"],
                            document_number=data["number"],
                        )
                    )
                else:
                    type_name = document_name.upper()
                    if type_name == "OTHER_ID":
                        type_name = IDENTIFICATION_TYPE_OTHER
                    label = IDENTIFICATION_TYPE_DICT.get(type_name, data.get("name"))
                    country = Country(data["issuing_country"])
                    document_type, _ = ImportedDocumentType.objects.get_or_create(
                        label=label,
                        type=type_name,
                    )
                    file = self._handle_image_field(data.get("photo", ""), False)
                    documents.append(
                        ImportedDocument(
                            document_number=data["number"],
                            country=country,
                            photo=file,
                            individual=data["individual"],
                            type=document_type,
                        )
                    )
        ImportedDocument.objects.bulk_create(documents)
        ImportedIndividualIdentity.objects.bulk_create(identities)

    @staticmethod
    def _handle_collectors(collectors_dict, individuals_dict):
        collectors_to_bulk_create = []
        for hash_key, collectors_list in collectors_dict.items():
            for collector in collectors_list:
                collector.individual = individuals_dict.get(hash_key)
                collectors_to_bulk_create.append(collector)
        ImportedIndividualRoleInHousehold.objects.bulk_create(collectors_to_bulk_create)

    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    def execute(self, registration_data_import_id, import_data_id, business_area_id):
        registration_data_import = RegistrationDataImportDatahub.objects.select_for_update().get(
            id=registration_data_import_id,
        )
        old_rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
        self.registration_data_import_mis = old_rdi_mis
        self.registration_data_import_datahub = registration_data_import
        registration_data_import.import_done = RegistrationDataImportDatahub.STARTED
        registration_data_import.save()

        import_data = ImportData.objects.get(id=import_data_id)

        self.business_area = BusinessArea.objects.get(id=business_area_id)

        submissions_json = import_data.file.read()
        submissions = json.loads(submissions_json)
        self.reduced_submissions = rename_dict_keys(submissions, get_field_name)

        head_of_households_mapping = {}
        households_to_create = []
        individuals_to_create = {}
        collectors_to_create = defaultdict(list)
        for household in self.reduced_submissions:
            individuals_to_create_list = []
            documents_and_identities_to_create = []
            submission_meta_data = get_submission_metadata(household)
            if self.business_area.get_sys_option("ignore_amended_kobo_submissions"):
                submission_meta_data["amended"] = False

            if KoboImportedSubmission.objects.filter(**submission_meta_data).exists():
                continue

            submission_meta_data.pop("amended", None)
            household_obj = ImportedHousehold(**submission_meta_data)
            self.attachments = household.get("_attachments", [])
            registration_date = None
            current_individuals = []
            for hh_field, hh_value in household.items():
                if hh_field == KOBO_FORM_INDIVIDUALS_COLUMN_NAME:
                    for individual in hh_value:
                        current_individual_docs_and_identities = defaultdict(dict)
                        individual_obj = ImportedIndividual()
                        only_collector_flag = False
                        role = None
                        for i_field, i_value in individual.items():
                            if i_field in self.DOCS_AND_IDENTITIES_FIELDS:
                                key = (
                                    i_field.replace("_photo_i_c", "")
                                    .replace("_no_i_c", "")
                                    .replace("_issuer_i_c", "")
                                    .replace("_type_i_c", "")
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
                        individual_obj.registration_data_import = registration_data_import
                        if individual_obj.relationship == HEAD:
                            head_of_households_mapping[household_obj] = individual_obj

                        individual_obj.household = household_obj if only_collector_flag is False else None

                        individuals_to_create[individual_obj.get_hash_key] = individual_obj
                        individuals_to_create_list.append(individual_obj)
                        current_individuals.append(individual_obj)
                        documents_and_identities_to_create.append(current_individual_docs_and_identities)
                        if role in (ROLE_PRIMARY, ROLE_ALTERNATE):
                            role_obj = ImportedIndividualRoleInHousehold(
                                individual=individual_obj,
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
            household_obj.registration_data_import = registration_data_import
            household_obj = self._assign_admin_areas_titles(household_obj)
            households_to_create.append(household_obj)

            for ind in current_individuals:
                ind.first_registration_date = registration_date
                ind.last_registration_date = registration_date
                ind.kobo_asset_id = household_obj.kobo_asset_id

            ImportedIndividual.objects.bulk_create(individuals_to_create_list)
            self._handle_documents_and_identities(documents_and_identities_to_create)

        ImportedHousehold.objects.bulk_create(households_to_create)
        self._handle_collectors(collectors_to_create, individuals_to_create)

        households_to_update = []
        for household, individual in head_of_households_mapping.items():
            household.head_of_household = individual
            households_to_update.append(household)
        ImportedHousehold.objects.bulk_update(
            households_to_update,
            ["head_of_household"],
            1000,
        )
        registration_data_import.import_done = RegistrationDataImportDatahub.DONE
        registration_data_import.save()

        rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
        rdi_mis.status = RegistrationDataImport.IN_REVIEW
        rdi_mis.save()
        log_create(RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, old_rdi_mis, rdi_mis)
        if not self.business_area.postpone_deduplication:
            DeduplicateTask.deduplicate_imported_individuals(registration_data_import_datahub=registration_data_import)

    def _handle_exception(self, assigned_to, field_name, e):
        logger.exception(e)
        raise Exception(f"Error processing {assigned_to}: field `{field_name}` {e.__class__.__name__}({e})") from e
