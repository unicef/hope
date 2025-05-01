import logging
from functools import partial
from typing import Any, Callable

from django.db import transaction

import openpyxl
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import Scope
from hct_mis_api.apps.core.models import BusinessArea, FlexibleAttribute
from hct_mis_api.apps.core.utils import SheetImageLoader, serialize_flex_attributes
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.geo.models import Country as GeoCountry
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    DocumentType,
    PendingHousehold,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Account
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import ImportData, RegistrationDataImport
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
    RdiXlsxCreateTask,
)
from hct_mis_api.apps.registration_datahub.tasks.utils import collectors_str_ids_to_list
from hct_mis_api.apps.utils.age_at_registration import calculate_age_at_registration

logger = logging.getLogger(__name__)


class RdiXlsxPeopleCreateTask(RdiXlsxCreateTask):
    """Works on valid XLSX files, parsing them and creating households/individuals
    in the Registration Datahub. Once finished it will update the status of
    that registration data import instance.
    """

    def __init__(self) -> None:
        super().__init__()
        self.index_id: int | None = None
        self.households_to_update = []
        self.COMBINED_FIELDS: dict = {
            **FieldFactory.from_scopes([Scope.XLSX_PEOPLE]).apply_business_area().to_dict_by("xlsx_field"),
            **serialize_flex_attributes()["individuals"],
        }

    def _handle_collectors(
        self,
        value: Any,
        header: str,
        individual: PendingIndividual,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        list_of_index_ids = collectors_str_ids_to_list(value)
        if list_of_index_ids is None:
            return
        for index_id in list_of_index_ids:
            if not index_id:
                continue
            role = ROLE_PRIMARY if header == "pp_primary_collector_id" else ROLE_ALTERNATE
            self.collectors[int(index_id)].append(PendingIndividualRoleInHousehold(individual=individual, role=role))

    def _create_collectors(self) -> None:
        collectors_to_create = []
        for index_id, collectors_list in self.collectors.items():
            for collector in collectors_list:
                collector.household_id = self.households.get(int(index_id)).pk
                collectors_to_create.append(collector)
        PendingIndividualRoleInHousehold.objects.bulk_create(collectors_to_create)

    def _create_hh_ind(
        self, obj_to_create: Any, row: Any, first_row: Any, complex_fields: dict, complex_types: dict, sheet_title: str
    ) -> None:
        registration_data_import = obj_to_create.registration_data_import
        excluded = ("pp_age", "pp_index_id")

        for cell, header_cell in zip(row, first_row, strict=False):
            try:
                if header_cell.value in self._pdu_column_names:
                    continue
                if header_cell.value.startswith(f"pp_{Account.ACCOUNT_FIELD_PREFIX}"):
                    self._handle_delivery_mechanism_fields(cell.value, header_cell.value, cell.row, obj_to_create)
                    continue

                header = header_cell.value
                combined_fields = self.COMBINED_FIELDS
                current_field = combined_fields.get(header, {})

                if not current_field and header not in complex_fields[sheet_title]:
                    continue
                is_not_image = current_field.get("type") != "IMAGE"
                cell_value = cell.value
                if isinstance(cell_value, str):
                    cell_value = cell_value.strip()
                is_not_required_and_empty = not current_field.get("required") and cell.value is None and is_not_image
                if is_not_required_and_empty:
                    continue
                if header == "pp_index_id":
                    self.index_id = int(cell_value)
                if header in excluded:
                    continue

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
                            current_field["name"],
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
                elif hasattr(
                    obj_to_create,
                    current_field["name"],
                ):
                    value = self._cast_value(cell_value, header)
                    if value in (None, ""):
                        continue

                    if header in ("pp_admin1_i_c", "pp_admin2_i_c", "pp_admin3_i_c", "pp_admin4_i_c"):
                        setattr(
                            obj_to_create,
                            current_field["name"],
                            Area.objects.get(p_code=cell.value),
                        )
                    elif header in ("pp_country_i_c", "pp_country_origin_i_c"):
                        setattr(
                            obj_to_create,
                            current_field["name"],
                            GeoCountry.objects.get(iso_code3=cell.value),
                        )
                    else:
                        setattr(
                            obj_to_create,
                            current_field["name"],
                            value,
                        )

            except Exception as e:
                raise Exception(
                    f"Error processing cell {header_cell} with `{cell}`: {e.__class__.__name__}({e})"
                ) from e

        obj_to_create.last_registration_date = obj_to_create.first_registration_date
        obj_to_create.detail_id = row[0].row
        obj_to_create.business_area = registration_data_import.business_area
        if sheet_title == "households":
            obj_to_create.set_admin_areas()
            obj_to_create.save()
            self.households[self.index_id] = obj_to_create
        else:
            obj_to_create = self._validate_birth_date(obj_to_create)
            obj_to_create.age_at_registration = calculate_age_at_registration(
                registration_data_import.created_at, str(obj_to_create.birth_date)
            )
            populate_pdu_with_null_values(registration_data_import.program, obj_to_create.flex_fields)

            household = self.households[self.index_id]
            if household is not None:
                obj_to_create.household = self.households[self.index_id]
                household.head_of_household = obj_to_create
                self.households_to_update.append(household)

            self.individuals.append(obj_to_create)

    def _create_objects(self, sheet: Worksheet, registration_data_import: RegistrationDataImport) -> None:
        complex_fields: dict[str, dict[str, Callable]] = {
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
                "pp_consent_sign_i_c": self._handle_image_field,
                "pp_hh_geopoint_i_c": self._handle_geopoint_field,
                "pp_fchild_hoh_i_c": self._handle_bool_field,
                "pp_child_hoh_i_c": self._handle_bool_field,
                "pp_consent_i_c": self._handle_bool_field,
                "pp_first_registration_date_i_c": self._handle_datetime,
            },
        }
        document_complex_types: dict[str, Callable] = {}
        for document_type in DocumentType.objects.all():
            document_complex_types[f"pp_{document_type.key}_i_c"] = self._handle_document_fields
            document_complex_types[f"pp_{document_type.key}_no_i_c"] = self._handle_document_fields
            document_complex_types[f"pp_{document_type.key}_photo_i_c"] = self._handle_document_photo_fields
            document_complex_types[f"pp_{document_type.key}_issuer_i_c"] = self._handle_document_issuing_country_fields
        complex_fields["individuals"].update(document_complex_types)
        complex_types: dict[str, Callable] = {
            "GEOPOINT": self._handle_geopoint_field,
            "IMAGE": self._handle_image_field,
            "DECIMAL": self._handle_decimal_field,
            "BOOL": self._handle_bool_field,
        }

        rdi = RegistrationDataImport.objects.get(id=registration_data_import.id)

        hh_obj = partial(
            PendingHousehold,
            registration_data_import=rdi,
            program_id=rdi.program.id,
            collect_type=PendingHousehold.CollectType.SINGLE.value,
        )
        ind_obj = partial(PendingIndividual, registration_data_import=rdi, program_id=rdi.program.id)

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
            for sheet_title in ("households", "individuals"):
                if sheet_title == "households":
                    obj_to_create = hh_obj()
                else:
                    obj_to_create = ind_obj()
                    populate_pdu_with_null_values(registration_data_import.program, obj_to_create.flex_fields)
                    self.handle_pdu_fields(row, first_row, obj_to_create)
                self._create_hh_ind(obj_to_create, row, first_row, complex_fields, complex_types, sheet_title)

        PendingIndividual.objects.bulk_create(self.individuals)
        PendingHousehold.objects.bulk_update(
            self.households_to_update,
            ["head_of_household"],
            1000,
        )
        self._create_documents()
        self._create_identities()
        self._create_collectors()
        self._create_bank_accounts_infos()
        self._create_accounts()

    @transaction.atomic()
    def execute(
        self, registration_data_import_id: str, import_data_id: str, business_area_id: str, program_id: str
    ) -> None:
        registration_data_import = RegistrationDataImport.objects.select_for_update().get(
            id=registration_data_import_id,
        )
        self.registration_data_import = registration_data_import
        self.program = Program.objects.get(id=program_id)
        self.pdu_flexible_attributes = FlexibleAttribute.objects.filter(
            type=FlexibleAttribute.PDU, program=self.program
        ).select_related("pdu_data")
        registration_data_import.status = RegistrationDataImport.IMPORTING
        registration_data_import.save()

        import_data = ImportData.objects.get(id=import_data_id)

        self.business_area = BusinessArea.objects.get(id=business_area_id)

        wb = openpyxl.load_workbook(import_data.file, data_only=True)

        # households objects have to be created first
        worksheet = wb["People"]
        logger.info("Starting import of %s", registration_data_import.id)
        self.image_loader = SheetImageLoader(worksheet)
        self._create_objects(worksheet, registration_data_import)

        old_rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.id)
        if not self.business_area.postpone_deduplication:
            # TODO: not sure about deduplication for people??
            logger.info("Starting deduplication of %s", registration_data_import.id)
            rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.id)
            rdi_mis.status = RegistrationDataImport.DEDUPLICATION
            rdi_mis.save()
            DeduplicateTask(self.business_area.slug, str(program_id)).deduplicate_pending_individuals(
                registration_data_import=rdi_mis
            )
            logger.info("Finished deduplication of %s", registration_data_import.id)
        else:
            rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import.id)
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
