from django.db import transaction

from backend.hct_mis_api.apps.core.utils import get_combined_attributes
from .base import DjangoOperator


class RegistrationXLSXImportOperator(DjangoOperator):
    """
    Works on valid XLSX files, parsing them and creating households/individuals
    in the Registration Datahub. Once finished it will update the status of
    that registration data import instance.
    """

    households = None
    individuals = None

    def _handle_location(self, value):
        from geopy.geocoders import ArcGIS

        location = ArcGIS().reverse(value)

    def _create_objects(self, sheet, registration_data_import):
        from registration_datahub.models import (
            ImportedHousehold,
            ImportedIndividual,
        )

        complex_fields = {
            "individuals": {"location": self.handle_location,},
            "households": {},
        }

        sheet_title = sheet.title.lower()

        combined_fields = get_combined_attributes()

        first_row = sheet[1]
        households_to_update = []
        for row in sheet.iter_rows(min_row=3):
            if not any([cell.value for cell in row]):
                continue

            if sheet_title == "households":
                obj_to_create = ImportedHousehold(
                    household_ca_id="NOT PROVIDED",
                    registration_data_import_id=registration_data_import,
                )
            else:
                obj_to_create = ImportedIndividual(
                    registration_data_import_id=registration_data_import,
                )

            household_id = None
            for cell, header in zip(row, first_row):
                current_field = combined_fields.get(header.value)
                if not current_field:
                    continue

                if header == "household_id":
                    household_id = cell.value
                    if sheet_title == "individuals":
                        obj_to_create.household = self.households.get(household_id)

                if (
                    hasattr(obj_to_create, header)
                    and header not in complex_fields.keys()
                ):
                    if header == "representative":
                        household = self.households.get(household_id)
                        household.representative = obj_to_create
                        households_to_update.append(household)
                    elif header == "head_of_household":
                        household = self.households.get(household_id)
                        household.head_of_household = obj_to_create
                        households_to_update.append(household)
                    else:
                        setattr(obj_to_create, header, cell.value)
                elif header in complex_fields[sheet_title]:
                    fn = complex_fields[sheet_title].get(header)
                    value = fn(cell.value)
                    setattr(obj_to_create, header, value)

            if sheet_title == "households":
                self.households[household_id] = obj_to_create
            else:
                # TODO: maybe make it as signal or override save() method
                first_name = obj_to_create.first_name
                middle_name = obj_to_create.middle_name
                last_name = obj_to_create.last_name
                obj_to_create.full_name = (
                    first_name + f" {middle_name}"
                    if middle_name
                    else "" + f" {last_name}"
                )
                self.individuals.append(obj_to_create)

        if sheet_title == "households":
            ImportedHousehold.objects.bulk_create(self.households)
        else:
            ImportedIndividual.objects.bulk_create(self.individuals)
            ImportedHousehold.objects.bulk_update(
                households_to_update, ["representative", "head_of_household"], 1000,
            )

    @transaction.atomic()
    def execute(self, context, **kwargs):
        import openpyxl

        from registration_datahub.models import RegistrationDataImportDatahub
        from registration_datahub.models import ImportData

        # households have to be dict with id as key
        # to match household to individuals
        self.households = {}
        self.individuals = []

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        registration_data_import = RegistrationDataImportDatahub.objects.select_for_update().get(
            id=config_vars.get("registration_data_import_id")
        )
        import_data = ImportData.objects.get(id=config_vars.get("import_data_id"),)

        wb = openpyxl.load_workbook(import_data.xlsx_file, data_only=True)

        # TODO: Currently adding only core fields for testing purposes,
        #  need to add flex fields
        for sheet in wb.worksheets:
            self._create_objects(sheet, registration_data_import)

        registration_data_import.status = "DONE"
        registration_data_import.save()
