from datetime import timedelta

from django.utils import timezone
from django.core.management import BaseCommand

from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.household.models import MALE
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory

from faker import Faker

faker = Faker()


def create_household_with_individual(address):
    now = timezone.now()
    delta_20_years = timedelta(days=365 * 20)
    afghanistan = BusinessArea.objects.get(name="Afghanistan")

    rdi = RegistrationDataImportFactory(
        data_source=RegistrationDataImport.XLS,
        business_area=afghanistan,
        number_of_households=1,
        number_of_individuals=1,
    )

    hh = Household(
        first_registration_date=now,
        last_registration_date=now,
        business_area=afghanistan,
        address=address,
        registration_data_import=rdi,
        size=1,
        withdrawn=False,
    )

    hh.head_of_household = Individual.objects.create(
        birth_date=now - delta_20_years,
        first_registration_date=now,
        last_registration_date=now,
        business_area=afghanistan,
        sex=MALE,
        full_name=faker.name(),
    )
    hh.save()

    hh.head_of_household.household = hh
    hh.head_of_household.save()


def init_targeting(seed):
    create_household_with_individual(
        address=f"TargetingVille-{seed}",
    )
    ProgramFactory(name=f"TargetingProgram-{seed}", status=Program.ACTIVE)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "scenario",
            action="store",
            choices=["targeting"],
        )

        parser.add_argument(
            "--seed",
            default=int(timezone.now().timestamp() * 100),
            action="store",
            nargs="?",
            type=int,
        )

    def handle(self, *args, **options):
        print("Initializing scenario with options:", {k: v for k, v in options.items() if k in ["scenario", "seed"]})
        {"targeting": init_targeting}[options["scenario"]](options.get("seed"))
