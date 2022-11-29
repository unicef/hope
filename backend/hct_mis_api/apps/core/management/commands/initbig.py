import math
import random
import time

from collections import namedtuple

from django.core.management import call_command
from django.core.management import BaseCommand

from hct_mis_api.apps.grievance.fixtures import TicketIndividualDataUpdateDetailsFactory
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.program.fixtures import ProgramFactory, CashPlanFactory, Program
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory, TargetingCriteriaFactory
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import (
    PaymentRecordFactory,
)
from hct_mis_api.apps.account.models import Role, UserRole
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory

from faker import Faker


def print_stats():
    print("-" * 30)
    print("Households:", Household.objects.count())
    print("Individuals:", Individual.objects.count())
    print("Business Areas:", BusinessArea.objects.count())
    print("Registration Data Imports:", RegistrationDataImport.objects.count())
    print("Cash Plans:", CashPlan.objects.count())
    print("Target Populations:", TargetPopulation.objects.count())
    print("Grievance Tickets:", GrievanceTicket.objects.count())
    print("Programs:", Program.objects.count())
    print("-" * 30)


start_time = time.time()


def elapsed_print(*args, **kwargs):
    print(f"[{time.time() - start_time:.2f}s]", *args, **kwargs)


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
        individual.save(update_fields=["household"])
    return size


def create_households(individuals_amount, area_with_locale):
    business_area = BusinessAreaFactory(name=area_with_locale.area)
    rdis = [
        RegistrationDataImportFactory(business_area=business_area)
        for _ in range(math.ceil(individuals_amount / pow(10, 5)))
    ]

    total = 0
    elapsed_print(f"Creating ~{individuals_amount} individuals for {business_area.name} with {len(rdis)} RDI")
    faker = Faker([area_with_locale.locale])
    while total < individuals_amount:
        amount_of_individuals = create_household_with_individuals(
            business_area=business_area,
            size=faker.random_int(min=1, max=4),
            rdi=random.choice(rdis),
            faker=faker,
        )
        total += amount_of_individuals


def create_payment_records(business_area_names):
    elapsed_print("Creating payment records")

    for business_area_name in business_area_names:
        business_area = BusinessArea.objects.get(name=business_area_name)
        all_hhs_in_ba = Household.objects.filter(business_area=business_area)
        hhs_to_have_pr = all_hhs_in_ba.order_by("?")[: int(all_hhs_in_ba.count() * 0.6)]
        for household in hhs_to_have_pr:
            cash_plan = CashPlan.objects.filter(business_area=household.business_area).order_by("?").first()
            tp = TargetPopulation.objects.filter(business_area=household.business_area).order_by("?").first()
            PaymentRecordFactory(
                household=household,
                cash_plan=cash_plan,
                target_population=tp,
                business_area=household.business_area,
                status=PaymentRecord.STATUS_SUCCESS,
            )
    # TODO: visible in paym verif


def create_user_roles_in_business_areas(user, business_areas):
    role = Role.objects.get(name="Role with all permissions")
    for area in business_areas:
        UserRole.objects.get_or_create(user=user, role=role, business_area=BusinessArea.objects.get(name=area))


def create_grievance_tickets_for_ba(business_area, admin_area, faker, scale):
    size = int(2 * pow(10, 6) * scale)
    elapsed_print(f"Creating {size} grievance tickets for {business_area.name}")
    individuals = Individual.objects.filter(business_area=business_area)
    for _ in range(size):
        TicketIndividualDataUpdateDetailsFactory(
            ticket=GrievanceTicketFactory(
                business_area=business_area,
                category=GrievanceTicket.CATEGORY_DATA_CHANGE,
                issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
                admin2=admin_area,
            ),
            individual=individuals.order_by("?").first(),
            individual_data={
                "given_name": faker.first_name(),
                "family_name": faker.last_name(),
                "flex_fields": {},
            },
        )


def create_grievance_tickets(scale, business_areas):
    for business_area_data in business_areas:
        faker = Faker([business_area_data.locale])
        country = geo_models.Country.objects.get_or_create(name=business_area_data.area)[0]
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        admin_area = AreaFactory(name=f"city-{country.name}", area_type=area_type, p_code=faker.postcode())
        business_area = BusinessArea.objects.get(name=business_area_data.area)
        create_grievance_tickets_for_ba(business_area, admin_area, faker, scale / len(business_areas))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--scale",
            action="store",
            default=1.0,
        )

    def handle(self, *args, **options):
        elapsed_print("Clearing db")

        call_command("flush", "--noinput")
        call_command("flush", "--noinput", database="cash_assist_datahub_mis")
        call_command("flush", "--noinput", database="cash_assist_datahub_ca")
        call_command("flush", "--noinput", database="cash_assist_datahub_erp")
        call_command("flush", "--noinput", database="registration_datahub")

        call_command("loaddata", "hct_mis_api/apps/geo/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/core/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/account/fixtures/data.json")
        call_command(
            "loaddata", "hct_mis_api/apps/registration_datahub/fixtures/data.json", database="registration_datahub"
        )
        call_command("loadcountries")

        user = User.objects.get(username="root")

        scale = float(options["scale"])
        elapsed_print(f"Creating fake data with scale {scale}")
        print_stats()

        AreaWithLocale = namedtuple("AreaWithLocale", ["area", "locale"])

        small_business_areas_with_locales = [
            AreaWithLocale("Azerbaijan", "az_AZ"),
            AreaWithLocale("Egypt", "ar_EG"),
            AreaWithLocale("Belarus", "ru_RU"),
            AreaWithLocale("China", "zh_CN"),
            AreaWithLocale("Philippines", "en_PH"),
            AreaWithLocale("Indonesia", "id_ID"),
            AreaWithLocale("Thailand", "th_TH"),
            AreaWithLocale("Ethiopia", "en_IE"),
            AreaWithLocale("Morocco", "ar_AA"),
            AreaWithLocale("Venezuela", "es_CA"),
        ]

        expected_small_ba_size = int(pow(10, 5) * scale)
        for area_with_locale in small_business_areas_with_locales:
            create_households(
                individuals_amount=expected_small_ba_size,
                area_with_locale=area_with_locale,
            )
        ukraine = AreaWithLocale("Ukraine", "uk_UA")
        create_households(
            individuals_amount=int(4 * pow(10, 6) * scale),
            area_with_locale=ukraine,
        )

        all_bas = small_business_areas_with_locales + [ukraine]
        create_user_roles_in_business_areas(user, (a.area for a in all_bas))

        elapsed_print("Creating programs")
        for business_area in BusinessArea.objects.filter(name__in=[area.area for area in all_bas]):
            for _ in range(3):
                ProgramFactory(business_area=business_area, status=Program.ACTIVE)

        elapsed_print("Creating cash plans")
        for business_area in BusinessArea.objects.filter(name__in=[area.area for area in all_bas]):
            for _ in range(3):
                CashPlanFactory(
                    business_area=business_area,
                    status=CashPlan.DISTRIBUTION_COMPLETED,
                    program=Program.objects.filter(business_area=business_area).order_by("?").first(),
                )

        elapsed_print("Creating target populations")
        for business_area in BusinessArea.objects.filter(name__in=[area.area for area in all_bas]):
            for _ in range(3):
                TargetPopulationFactory(
                    business_area=business_area,
                    status=TargetPopulation.STATUS_LOCKED,
                    created_by=user,
                    targeting_criteria=(TargetingCriteriaFactory()),
                    program=Program.objects.filter(business_area=business_area).order_by("?").first(),
                )

        create_payment_records([area.area for area in all_bas])

        create_grievance_tickets(scale, all_bas)

        elapsed_print("Done generating data")
        print_stats()


# TODO: country dashboard shows money
