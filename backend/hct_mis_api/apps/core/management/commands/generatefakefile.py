import datetime
import random

from django.conf import settings
from django.core.management import BaseCommand

from dateutil.relativedelta import relativedelta
from faker import Faker
from openpyxl.drawing.image import Image

from hct_mis_api.apps.core.field_attributes.fields_types import (
    TYPE_BOOL,
    TYPE_DATE,
    TYPE_GEOPOINT,
    TYPE_INTEGER,
    TYPE_SELECT_ONE,
    TYPE_STRING,
)
from hct_mis_api.apps.core.utils import get_combined_attributes
from hct_mis_api.apps.household.models import HEAD
from hct_mis_api.apps.registration_datahub.template_generator import (
    TemplateFileGenerator,
)


class Command(BaseCommand):
    """
    It's ugly but only used to generate the fake test file
    """

    help = "Generate fake file for RDI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--households",
            dest="households_count",
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of program objects.",
        )

    def handle(self, *args, **options):
        wb = TemplateFileGenerator.get_template_file()
        households_ws = wb["Households"]
        individuals_ws = wb["Individuals"]
        combined_fields = get_combined_attributes()
        faker = Faker()
        today = datetime.date.today()

        all_hh = []
        all_ind = []

        for number in range(1, options["households_count"] + 1):
            print(f"household: {number}")
            single_household_data = []
            for cell in households_ws[1]:
                header = cell.value or ""
                if header in ("admin1_h_c", "admin2_h_c"):
                    single_household_data.append("")
                    continue
                elif header.endswith("_h_f"):
                    single_household_data.append("")
                    continue
                elif header == "household_id":
                    single_household_data.append(number)
                    continue
                elif header == "address_h_c":
                    value = faker.address()
                    single_household_data.append(value)
                    continue
                elif header == "consent_h_c":
                    img = Image(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.png")
                    households_ws.add_image(img, f"{cell.column_letter}{number + 2}")
                    single_household_data.append("")
                    continue
                elif header == "first_registration_date_h_c":
                    value = faker.date_between(start_date="-30d", end_date="today")
                    single_household_data.append(value)
                    continue
                elif header == "size_h_c":
                    single_household_data.append(4)
                    continue

                field_dict = combined_fields.get(header)

                if field_dict is None:
                    single_household_data.append("")
                    continue

                field_type = field_dict["type"]

                if field_type == TYPE_SELECT_ONE:
                    choices = [x["value"] for x in field_dict["choices"]]
                    value = random.choice(choices)
                elif field_type == TYPE_BOOL:
                    choices = [True, False]
                    value = random.choice(choices)
                elif field_type == TYPE_DATE:
                    value = faker.date_of_birth(maximum_age=90)
                elif field_type == TYPE_INTEGER:
                    value = 0
                elif field_type == TYPE_GEOPOINT:
                    raw_value = faker.latlng()
                    value = f"{raw_value[0]}, {raw_value[1]}"
                elif field_type == TYPE_STRING:
                    value = faker.word()
                else:
                    value = ""

                single_household_data.append(value)

            for i in range(1, 5):
                single_individual_data = []

                name = faker.name()
                name_list = name.split(" ")
                if len(name_list) == 2:
                    first_name = name_list[0]
                    last_name = name_list[1]
                if len(name_list) == 3:
                    first_name = name_list[1]
                    last_name = name_list[2]

                birth_date = faker.date_of_birth()
                age = relativedelta(today, birth_date).years
                for cell in individuals_ws[1]:
                    header = cell.value or ""
                    if header in (
                        "other_id_no_i_c",
                        "other_id_type_i_c",
                        "birth_certificate_no_i_c",
                        "birth_certificate_photo_i_c",
                        "drivers_license_no_i_c",
                        "drivers_license_photo_i_c",
                        "electoral_card_no_i_c",
                        "electoral_card_photo_i_c",
                        "unhcr_id_no_i_c",
                        "unhcr_id_photo_i_c",
                        "national_passport_i_c",
                        "national_passport_photo_i_c",
                        "national_id_no_i_c",
                        "national_id_photo_i_c",
                        "scope_id_no_i_c",
                        "scope_id_photo_i_c",
                    ):
                        single_individual_data.append("")
                        continue
                    elif header.endswith("_i_f"):
                        single_household_data.append("")
                        continue
                    elif header == "household_id":
                        single_individual_data.append(number)
                        continue
                    elif header == "first_registration_date_h_c":
                        value = faker.date_between(start_date="-30d", end_date="today")
                        single_individual_data.append(value)
                        continue
                    elif header == "primary_collector_id":
                        if i == 1:
                            value = number
                        else:
                            value = ""
                        single_individual_data.append(value)
                        continue
                    elif header == "alternate_collector_id":
                        if i == 2:
                            value = number
                        else:
                            value = ""
                        single_individual_data.append(value)
                        continue
                    elif header == "full_name_i_c":
                        value = name
                        single_individual_data.append(value)
                        continue
                    elif header == "given_name_i_c":
                        value = first_name
                        single_individual_data.append(value)
                        continue
                    elif header == "middle_name_i_c":
                        value = ""
                        single_individual_data.append(value)
                        continue
                    elif header == "family_name_i_c":
                        value = last_name
                        single_individual_data.append(value)
                        continue
                    elif header == "age":
                        single_individual_data.append(age)
                        continue
                    elif header == "birth_date_i_c":
                        single_individual_data.append(birth_date)
                        continue
                    elif header.startswith("phone_no_"):
                        single_individual_data.append(faker.phone_number())
                        continue
                    elif header == "relationship_i_c":
                        if i == 1:
                            value = HEAD
                        else:
                            i_field_dict = combined_fields.get(header)
                            choices = [x["value"] for x in i_field_dict["choices"] if x["value"] != HEAD]
                            value = random.choice(choices)
                        single_individual_data.append(value)
                        continue

                    i_field_dict = combined_fields.get(header)

                    if i_field_dict is None:
                        single_household_data.append("")
                        continue

                    i_field_type = i_field_dict["type"]

                    if i_field_type == TYPE_SELECT_ONE:
                        choices = [x["value"] for x in i_field_dict["choices"]]
                        value = random.choice(choices)
                    elif i_field_type == TYPE_BOOL:
                        choices = [True, False]
                        value = random.choice(choices)
                    elif i_field_type == TYPE_DATE:
                        value = faker.date_of_birth(maximum_age=90)
                    elif i_field_type == TYPE_INTEGER:
                        value = 0
                    elif i_field_type == TYPE_GEOPOINT:
                        raw_value = faker.latlng()
                        value = f"{raw_value[0]}, {raw_value[1]}"
                    elif i_field_type == TYPE_STRING:
                        value = faker.word()
                    else:
                        value = ""

                    single_individual_data.append(value)

                all_ind.append(single_individual_data)
            all_hh.append(single_household_data)

        for hh in all_hh:
            households_ws.append(hh)
        print("households added")
        for ind in all_ind:
            individuals_ws.append(ind)
        print("individuals added")

        wb.save("fake_file.xlsx")
