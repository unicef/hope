from django.db import transaction
from django.utils import timezone

from .base import DjangoOperator


class RegistrationXLSXImportOperator(DjangoOperator):
    """
    Works on valid XLSX files, parsing them and creating households/individuals
    in the Registration Datahub. Once finished it will update the status of
    that registration data import instance.
    """

    business_area = None
    households = None
    individuals = None
    documents = None

    def _handle_document_fields(self, value, header, *args, **kwargs):
        if header == "other_id_type_i_c":
            doc_type = value
        else:
            doc_type = (
                header.replace("_no_", "")
                .replace("_i_c", "")
                .replace("_", " ")
                .capitalize()
            )
        individual = kwargs.get("individual")
        row_num = kwargs.get("row_number")
        document_data = self.documents.get(f"individual_{row_num}")
        if document_data:
            document_data["value"] = value
        else:
            self.documents[f"individual_{row_num}"] = {
                "individual": individual,
                "header": header,
                "type": doc_type,
                "value": value,
            }

    def _handle_document_photo_fields(self, value, header, *args, **kwargs):
        row_num = kwargs.get("row_number")
        individual = kwargs.get("individual")
        document_data = self.documents.get(f"individual_{row_num}")
        if document_data:
            document_data["photo"] = value
        else:
            self.documents[f"individual_{row_num}"] = {
                "individual": individual,
                "header": header,
                "photo": value,
            }

    def _handle_image_field(self, value, header, *args, **kwargs):
        return

    def _create_documents(self):
        from registration_datahub.models import (
            ImportedDocument,
            ImportedDocumentType,
        )

        docs_to_create = []
        for document_data in self.documents.values():
            doc_type = ImportedDocumentType.objects.get(
                country=self.business_area, label=document_data.get("type"),
            )
            # TODO: do some stuff with photo
            photo = document_data.get("photo")
            individual = document_data.get("individual")
            photo_name = (
                f"{individual.full_name.lower().replace(' ', '_')}"
                f"_{timezone.now()}.jpg"
            )
            obj = ImportedDocument(
                document_number=document_data.get("value"),
                photo=None,
                individual=individual,
                type=doc_type,
            )
            # obj.photo.save(photo_name, photo, save=False)
            docs_to_create.append(obj)

        ImportedDocument.objects.bulk_create(docs_to_create)

    def _create_objects(self, sheet, registration_data_import):
        from core.utils import (
            get_combined_attributes,
            serialize_flex_attributes,
        )
        from registration_datahub.models import (
            ImportedHousehold,
            ImportedIndividual,
        )

        complex_fields = {
            "individuals": {
                "birth_certificate_no_i_c": self._handle_document_fields,
                "birth_certificate_photo_i_c": self._handle_document_photo_fields,
                "drivers_license_no_i_c": self._handle_document_fields,
                "drivers_license_photo_i_c": self._handle_document_photo_fields,
                "electoral_card_no_i_c": self._handle_document_fields,
                "electoral_card_photo_i_c": self._handle_document_photo_fields,
                "unhcr_id_no_i_c": self._handle_document_fields,
                "unhcr_id_photo_i_c": self._handle_document_photo_fields,
                "national_id_no_ic": self._handle_document_fields,
                "national_id_photo_ic": self._handle_document_photo_fields,
                "national_passport_i_c": self._handle_document_fields,
                "national_passport_photo_i_c": self._handle_document_photo_fields,
                "scope_id_no_i_c": self._handle_document_fields,
                "scope_id_photo_i_c": self._handle_document_photo_fields,
                "other_id_type_i_c": self._handle_document_fields,
                "other_id_no_i_c": self._handle_document_fields,
                "other_id_photo_i_c": self._handle_document_photo_fields,
            },
            "households": {"consent_h_c": self._handle_image_field,},
        }

        sheet_title = sheet.title.lower()

        combined_fields = get_combined_attributes()
        flex_fields = serialize_flex_attributes()

        first_row = sheet[1]
        households_to_update = []
        for row in sheet.iter_rows(min_row=3):
            if not any([cell.value for cell in row]):
                continue

            if sheet_title == "households":
                obj_to_create = ImportedHousehold(
                    registration_data_import=registration_data_import,
                )
            else:
                obj_to_create = ImportedIndividual(
                    registration_data_import=registration_data_import,
                )

            household_id = None
            for cell, header_cell in zip(row, first_row):
                header = header_cell.value
                current_field = combined_fields.get(header)
                is_not_required_and_empty = (
                    current_field.get("required") and not cell.value
                )
                if not current_field or is_not_required_and_empty:
                    continue

                if header == "household_id":
                    household_id = cell.value
                    if sheet_title == "individuals":
                        obj_to_create.household = self.households.get(
                            household_id
                        )

                if (
                    hasattr(obj_to_create, header)
                    and header not in complex_fields.keys()
                ):
                    if header == "relationship" and cell.value == "HEAD":
                        household = self.households.get(household_id)
                        household.head_of_household = obj_to_create
                        households_to_update.append(household)
                    else:
                        setattr(obj_to_create, header, cell.value)
                elif header in complex_fields[sheet_title]:
                    fn = complex_fields[sheet_title].get(header)
                    value = fn(value=cell.value, header=header)
                    if value is not None:
                        setattr(obj_to_create, header, value)
                elif header in flex_fields[sheet_title]:
                    if flex_fields[sheet_title][header]["type"] == "IMAGE":
                        image = self._handle_image_field(cell.value, header)
                    obj_to_create.flex_fields[header] = cell.value

            if sheet_title == "households":
                self.households[household_id] = obj_to_create
            else:
                self.individuals.append(obj_to_create)

        if sheet_title == "households":
            # FIXME: ADD ALL REQUIRED FIELDS, HANDLE CONSENT IMAGE AND OTHER STUFF
            ImportedHousehold.objects.bulk_create(self.households.values())
        else:
            ImportedIndividual.objects.bulk_create(self.individuals)
            ImportedHousehold.objects.bulk_update(
                households_to_update, ["head_of_household"], 1000,
            )
            self._create_documents()

    @transaction.atomic()
    def execute(self, context, **kwargs):
        import openpyxl

        from core.models import BusinessArea
        from registration_datahub.models import RegistrationDataImportDatahub
        from registration_datahub.models import ImportData

        self.households = {}
        self.documents = {}
        self.individuals = []

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        registration_data_import = RegistrationDataImportDatahub.objects.get(
            id=config_vars.get("registration_data_import_id")
        )
        import_data = ImportData.objects.get(
            id=config_vars.get("import_data_id"),
        )

        business_area_id = config_vars.get("business_area")
        self.business_area = BusinessArea.objects.get(id=business_area_id)

        wb = openpyxl.load_workbook(import_data.xlsx_file, data_only=True)

        for sheet in wb.worksheets:
            if sheet.title in ("Individuals", "Households"):
                self._create_objects(sheet, registration_data_import)

        registration_data_import.import_done = True
        registration_data_import.save()
