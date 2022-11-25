import random

from collections import namedtuple

from django.core.management import call_command
from django.core.management import BaseCommand

from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.core.models import BusinessArea


from faker import Faker


def create_household_with_individuals(business_area, size, rdi, faker):
    individuals = [
        IndividualFactory.create(
            household=None,
            given_name=faker.first_name(),
            middle_name=faker.first_name(),
            family_name=faker.last_name(),
            full_name=faker.name(),
            registration_data_import=rdi,
            business_area=business_area,
        )
        for _ in range(size)
    ]
    household = HouseholdFactory.create(
        business_area=business_area,
        registration_data_import=rdi,
        head_of_household=individuals[0],
    )

    for individual in individuals:
        individual.household = household
        individual.save()
    return household


def print_stats():
    print("-" * 30)
    print("Households: ", Household.objects.count())
    print("Individuals: ", Individual.objects.count())
    print("Business Areas: ", BusinessArea.objects.count())
    print("Registration Data Imports: ", RegistrationDataImport.objects.count())
    print("-" * 30)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--scale",
            action="store",
            default=1.0,
        )

    def handle(self, *args, **options):
        call_command("loaddata", "hct_mis_api/apps/geo/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/core/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/account/fixtures/data.json")
        call_command(
            "loaddata", "hct_mis_api/apps/registration_datahub/fixtures/data.json", database="registration_datahub"
        )

        scale = float(options["scale"])
        print(f"Creating fake data with scale {scale}")

        amount_of_rdis = 10
        print(f"Creating {amount_of_rdis} registration data imports")
        registration_data_imports = RegistrationDataImportFactory.create_batch(amount_of_rdis)

        AreaWithLocale = namedtuple("AreaWithLocale", ["area", "locale"])

        small_business_areas_with_locales = [
            AreaWithLocale("Japan", "ja_JP"),
            AreaWithLocale("Egypt", "ar_EG"),
            AreaWithLocale("Vietnam", "vi_VN"),
            AreaWithLocale("Albania", "sq_AL"),
            AreaWithLocale("Cyprus", "el_CY"),
            AreaWithLocale("Czech Republic", "cs_CZ"),
            AreaWithLocale("Denmark", "da_DK"),
            AreaWithLocale("Estonia", "et_EE"),
            AreaWithLocale("Finland", "fi_FI"),
            AreaWithLocale("France", "fr_FR"),
        ]

        print_stats()

        expected_small_ba_size = int(pow(10, 5) * scale)
        for area_with_locale in small_business_areas_with_locales:
            total = 0
            business_area = BusinessAreaFactory(name=area_with_locale.area)
            print(f"Creating {expected_small_ba_size} individuals for {business_area.name}")
            faker = Faker([area_with_locale.locale])
            while total < expected_small_ba_size:
                amount_of_individuals = faker.random_int(min=1, max=4)
                create_household_with_individuals(
                    business_area=business_area,
                    size=amount_of_individuals,
                    rdi=random.choice(registration_data_imports),
                    faker=faker,
                )
                total += amount_of_individuals

        # main_business_area = AreaWithLocale("Ukraine", "uk_UA")

        print("Done generating data")
        print_stats()
