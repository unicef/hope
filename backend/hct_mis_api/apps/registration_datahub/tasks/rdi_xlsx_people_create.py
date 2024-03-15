import logging
from functools import partial
from typing import Any, Callable, Dict

from django.db import transaction

import openpyxl
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import Scope
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import SheetImageLoader, serialize_flex_attributes
from hct_mis_api.apps.household.models import HEAD, ROLE_ALTERNATE, ROLE_PRIMARY
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
    RdiXlsxCreateTask,
)
from hct_mis_api.apps.registration_datahub.tasks.utils import collectors_str_ids_to_list
from hct_mis_api.apps.utils.age_at_registration import calculate_age_at_registration

logger = logging.getLogger(__name__)


class RdiXlsxPeopleCreateTask(RdiXlsxCreateTask):
    """
    Works on valid XLSX files, parsing them and creating households/individuals
    in the Registration Datahub. Once finished it will update the status of
    that registration data import instance.
    """

    def __init__(self) -> None:
        super().__init__()
        self.households_to_update = []
        # self.collectors_with_indexes = {
        #     "individual": {
        #         "primary_collector_ids_for": [],
        #         "alternate_collector_ids_for": []
        #     },
        #
        # }
        self.COMBINED_FIELDS: Dict = {
            **FieldFactory.from_scopes([Scope.XLSX_PEOPLE]).apply_business_area().to_dict_by("xlsx_field"),
            **serialize_flex_attributes()["individuals"],
        }

    def _handle_collectors(
        self,
        value: Any,
        header: str,
        individual: ImportedIndividual,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        list_of_ids = collectors_str_ids_to_list(value)
        if list_of_ids is None:
            return

        for hh_id in list_of_ids:
            if not hh_id:
                continue
            role = ROLE_PRIMARY if header == "pp_primary_collector_id" else ROLE_ALTERNATE
            self.collectors[hh_id].append(ImportedIndividualRoleInHousehold(individual=individual, role=role))

    def _create_collectors(self) -> None:
        collectors_to_create = []
        for hh_id, collectors_list in self.collectors.items():
            for collector in collectors_list:
                collector.household_id = self.households.get(hh_id).pk
                collectors_to_create.append(collector)
        ImportedIndividualRoleInHousehold.objects.bulk_create(collectors_to_create)

    # TODO: relationship_i_c == 'NON_BENEFICIARY' >
    #  The individual is ONLY an external collector
    #  (primary_collector_id, alternate_collector_id fields specify the entities for which this person collects)

    # TODO: update "primary_collector_id", "alternate_collector_id" based on "index_id" here?
    def _create_hh_ind(self, obj: Any, row, first_row, complex_fields, complex_types, sheet_title: str) -> None:
        obj_to_create = obj()
        registration_data_import = obj.registration_data_import

        excluded = ("pp_age", "pp_index_id")
        for cell, header_cell in zip(row, first_row):
            cell_number = int(cell.row)
            try:
                header = header_cell.value
                combined_fields = self.COMBINED_FIELDS
                current_field = combined_fields.get(header, {})

                if not current_field and header not in complex_fields[sheet_title]:
                    continue

                if header in excluded:
                    continue

                is_not_image = current_field.get("type") != "IMAGE"

                cell_value = cell.value
                if isinstance(cell_value, str):
                    cell_value = cell_value.strip()

                is_not_required_and_empty = not current_field.get("required") and cell.value is None and is_not_image
                if is_not_required_and_empty:
                    continue

                if sheet_title == "individuals":
                    obj_to_create.household = self.households.get(cell_number)

                if header in complex_fields[sheet_title]:
                    fn_complex: Callable = complex_fields[sheet_title][header]
                    value = fn_complex(
                        value=cell_value,
                        cell=cell,
                        header=header,
                        row_num=cell.row,
                        individual=obj_to_create if sheet_title == "individuals" else None,
                        household=obj_to_create if sheet_title == "households" else None,
                        is_field_required=current_field.get("required", False),
                    )
                    if value is not None:
                        setattr(
                            obj_to_create,
                            combined_fields[header]["name"],
                            value,
                        )
                elif hasattr(
                    obj_to_create,
                    combined_fields[header]["name"],
                ):
                    value = self._cast_value(cell_value, header)
                    if value in (None, ""):
                        continue

                    if sheet_title == "individuals":
                        if header == "pp_relationship_i_c" and value == HEAD:
                            household = self.households.get(cell_number)
                            if household is not None:
                                household.head_of_household = obj_to_create
                                self.households_to_update.append(household)
                    setattr(
                        obj_to_create,
                        combined_fields[header]["name"],
                        value,
                    )
                elif header in self.FLEX_FIELDS[sheet_title]:
                    value = self._cast_value(cell_value, header)
                    type_name = self.FLEX_FIELDS[sheet_title][header]["type"]
                    if type_name in complex_types:
                        fn_flex: Callable = complex_types[type_name]
                        value = fn_flex(
                            value=cell_value,
                            cell=cell,
                            header=header,
                            is_flex_field=True,
                            is_field_required=current_field.get("required", False),
                        )
                    if value is not None:
                        obj_to_create.flex_fields[header] = value
            except Exception as e:
                raise Exception(
                    f"Error processing cell {header_cell} with `{cell}`: {e.__class__.__name__}({e})"
                ) from e

            obj_to_create.last_registration_date = obj_to_create.first_registration_date
            obj_to_create.detail_id = row[0].row
            print("==>> cell_number =>", cell_number, row[0].row)
            if sheet_title == "households":
                obj_to_create.set_admin_areas()
                self.households[cell_number] = obj_to_create
            else:
                obj_to_create = self._validate_birth_date(obj_to_create)
                obj_to_create.age_at_registration = calculate_age_at_registration(
                    registration_data_import, str(obj_to_create.birth_date)
                )
                self.individuals.append(obj_to_create)

    def _create_objects(self, sheet: Worksheet, registration_data_import: RegistrationDataImport) -> None:
        complex_fields: Dict[str, Dict[str, Callable]] = {
            "individuals": {
                "pp_photo_i_c": self._handle_image_field,
                "pp_primary_collector_id": self._handle_collectors,
                "pp_alternate_collector_id": self._handle_collectors,
                "pp_pregnant_i_c": self._handle_bool_field,
                "pp_fchild_hoh_i_c": self._handle_bool_field,
                "pp_child_hoh_i_c": self._handle_bool_field,
                "pp_bank_name_i_c": self._handle_bank_account_fields,
                "pp_bank_account_number_i_c": self._handle_bank_account_fields,
                "pp_debit_card_number_i_c": self._handle_bank_account_fields,
                "pp_account_holder_name_i_c": self._handle_bank_account_fields,
                "pp_bank_branch_name_i_c": self._handle_bank_account_fields,
                "pp_first_registration_date_i_c": self._handle_datetime,
                "pp_unhcr_id_no_i_c": self._handle_identity_fields,
                "pp_unhcr_id_photo_i_c": self._handle_identity_photo,
                "pp_unhcr_id_issuer_i_c": self._handle_identity_issuing_country_fields,
                "pp_scope_id_no_i_c": self._handle_identity_fields,
                "pp_scope_id_photo_i_c": self._handle_identity_photo,
                "pp_scope_id_issuer_i_c": self._handle_identity_issuing_country_fields,
            },
            "households": {
                "pp_consent_sign_h_c": self._handle_image_field,
                "pp_hh_geopoint_h_c": self._handle_geopoint_field,
                "pp_fchild_hoh_h_c": self._handle_bool_field,
                "pp_child_hoh_h_c": self._handle_bool_field,
                "pp_consent_h_c": self._handle_bool_field,
                "pp_first_registration_date_h_c": self._handle_datetime,
            },
        }
        document_complex_types: Dict[str, Callable] = {}
        for document_type in ImportedDocumentType.objects.all():
            document_complex_types[f"pp_{document_type.key}_i_c"] = self._handle_document_fields
            document_complex_types[f"pp_{document_type.key}_no_i_c"] = self._handle_document_fields
            document_complex_types[f"pp_{document_type.key}_photo_i_c"] = self._handle_document_photo_fields
            document_complex_types[f"pp_{document_type.key}_issuer_i_c"] = self._handle_document_issuing_country_fields
        complex_fields["individuals"].update(document_complex_types)
        complex_types: Dict[str, Callable] = {
            "GEOPOINT": self._handle_geopoint_field,
            "IMAGE": self._handle_image_field,
            "DECIMAL": self._handle_decimal_field,
            "BOOL": self._handle_bool_field,
        }

        program_id = RegistrationDataImport.objects.get(id=registration_data_import.hct_id).program.id

        hh_obj = partial(
            ImportedHousehold,
            registration_data_import=registration_data_import,
            program_id=program_id,
            collect_type=ImportedHousehold.CollectType.SINGLE.value,
        )
        ind_obj = partial(ImportedIndividual, registration_data_import=registration_data_import, program_id=program_id)

        first_row = sheet[1]

        def has_value(cell: Cell) -> bool:
            if cell.value is None:
                return False
            if isinstance(cell.value, str):
                return cell.value.strip() != ""
            return True

        for row in sheet.iter_rows(min_row=3):
            if not any(has_value(cell) for cell in row):
                continue
            try:
                self._create_hh_ind(hh_obj, row, first_row, complex_fields, complex_types, "households")
                ImportedHousehold.objects.bulk_create(self.households.values())

                self._create_hh_ind(ind_obj, row, first_row, complex_fields, complex_types, "individuals")

            except Exception as e:
                raise Exception(f"Error processing row {row[0].row}: {e.__class__.__name__}({e})") from e

        ImportedIndividual.objects.bulk_create(self.individuals)
        ImportedHousehold.objects.bulk_update(
            self.households_to_update,
            ["head_of_household"],
            1000,
        )
        self._create_documents()
        self._create_identities()
        self._create_collectors()
        self._create_bank_accounts_infos()

    @transaction.atomic(using="registration_datahub")
    def execute(
        self, registration_data_import_id: str, import_data_id: str, business_area_id: str, program_id: str
    ) -> None:
        registration_data_import = RegistrationDataImportDatahub.objects.select_for_update().get(
            id=registration_data_import_id,
        )
        registration_data_import.import_done = RegistrationDataImportDatahub.STARTED
        registration_data_import.save()

        import_data = ImportData.objects.get(id=import_data_id)

        self.business_area = BusinessArea.objects.get(id=business_area_id)

        wb = openpyxl.load_workbook(import_data.file, data_only=True)

        # households objects have to be created first
        worksheet = wb["People"]
        logger.info("Starting import of %s", registration_data_import.id)
        self.image_loader = SheetImageLoader(worksheet)
        self._create_objects(worksheet, registration_data_import)

        registration_data_import.import_done = RegistrationDataImportDatahub.DONE
        registration_data_import.save()
        old_rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
        if not self.business_area.postpone_deduplication:
            # TODO: not sure about deduplication for people?
            logger.info("Starting deduplication of %s", registration_data_import.id)
            rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
            rdi_mis.status = RegistrationDataImport.DEDUPLICATION
            rdi_mis.save()
            DeduplicateTask(self.business_area.slug, str(program_id)).deduplicate_imported_individuals(
                registration_data_import_datahub=registration_data_import
            )
            logger.info("Finished deduplication of %s", registration_data_import.id)
        else:
            rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.hct_id)
            rdi_mis.status = RegistrationDataImport.IN_REVIEW
            rdi_mis.save()
            log_create(
                RegistrationDataImport.ACTIVITY_LOG_MAPPING,
                "business_area",
                None,
                rdi_mis.program_id,
                old_rdi_mis,
                rdi_mis,
            )
