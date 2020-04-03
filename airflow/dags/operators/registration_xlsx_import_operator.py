import io
from datetime import datetime

from PIL import Image
from django.db import transaction

from .base import DjangoOperator


class RegistrationXLSXImportOperator(DjangoOperator):
    """
    Works on valid XLSX files, parsing them and creating households/individuals
    in the Registration Datahub. Once finished it will update the status of
    that registration data import instance.
    """

    def execute(self, context, **kwargs):
        import openpyxl

        from registration_datahub.models import RegistrationDataImportDatahub
        from registration_datahub.models import (
            ImportData,
            ImportedIndividual,
            ImportedHousehold,
        )

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        registration_data_import = RegistrationDataImportDatahub.objects.get(
            id=config_vars.get("registration_data_import_id")
        )
        import_data = ImportData.objects.get(
            id=config_vars.get("import_data_id"),
        )

        wb = openpyxl.load_workbook(import_data.xlsx_file, data_only=True)

        # temporarily create consent img
        img = io.BytesIO(Image.new("RGB", (60, 30), color="red").tobytes())
        # TODO: Currently adding only core fields for testing purposes,
        #  need to add flex fields

        households = []
        ids_mapping = {}
        with transaction.atomic():
            for row in wb["Households"].iter_rows(min_row=3):
                if not any([cell.value for cell in row]):
                    continue

                hh_obj = ImportedHousehold(
                    household_ca_id="NOT PROVIDED",
                    consent=img,
                    residence_status=row[3].value,
                    nationality=row[4].value,
                    family_size=row[5].value,
                    address="Add on Individuals creation",
                    # What to do with location?
                    location=None,
                    representative=None,
                    registration_data_import_id=registration_data_import,
                    head_of_household=None,
                    registration_date=datetime.now().date(),
                )

                households.append(hh_obj)
                ids_mapping[row[0].value] = hh_obj

            ImportedHousehold.objects.bulk_create(households)

            individuals = []
            hh_to_update = []
            for row in wb["Individuals"].iter_rows(min_row=3):
                if not any([cell.value for cell in row]):
                    continue

                household = ids_mapping[row[0].value]

                individual_obj = ImportedIndividual(
                    individual_ca_id="NOT PROVIDED",
                    full_name=f"{row[9].value} {row[11].value} {row[10].value}",
                    first_name=row[9].value,
                    middle_name=row[11].value,
                    last_name=row[10].value,
                    sex=row[13].value,
                    dob=row[14].value,
                    estimated_dob=row[16].value,
                    nationality=household.nationality,
                    martial_status=row[2].value,
                    phone_number=row[7].value,
                    phone_number_alternative=row[8].value,
                    # TODO: ASK ABOUT THOSE TWO FIELDS ???
                    identification_type=row[20].value,
                    identification_number=0,
                    household=household,
                    registration_data_import_id=registration_data_import,
                    work_status=row[17].value,
                    disability=row[18].value,
                )
                if row[1].value == "YES":
                    household.representative = individual_obj
                    household.head_of_household = individual_obj
                    hh_to_update.append(household)

            ImportedIndividual.objects.bulk_create(individuals)

            ImportedHousehold.objects.bulk_update(
                hh_to_update, ["representative", "head_of_household"], 1000,
            )
