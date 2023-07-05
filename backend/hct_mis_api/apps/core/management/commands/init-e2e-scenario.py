from argparse import ArgumentParser
from datetime import timedelta
from typing import Any, Tuple

from django.core.management import BaseCommand
from django.utils import timezone

from faker import Faker

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import (
    MALE,
    ROLE_PRIMARY,
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.steficon.fixtures import RuleCommitFactory, RuleFactory
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import full_rebuild

faker = Faker()


def create_household_with_individual(address: str) -> Tuple[Household, Individual]:
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

    return hh, hh.head_of_household


def create_household_with_individual_for_payment_plan(address: str) -> None:
    hh, ind = create_household_with_individual(address)
    IndividualRoleInHousehold.objects.create(
        role=ROLE_PRIMARY,
        household=hh,
        individual=ind,
    )


def init_targeting(seed: str) -> None:
    create_household_with_individual(address=f"TargetingVille-{seed}")
    ProgramFactory(name=f"TargetingProgram-{seed}", status=Program.ACTIVE)


def init_payment_plan(seed: str) -> None:
    afghanistan = BusinessArea.objects.get(name="Afghanistan")
    addresses = [f"PaymentPlanVille-{seed}-1", f"PaymentPlanVille-{seed}-2", f"PaymentPlanVille-{seed}-3"]
    root = User.objects.get(username="root")

    create_household_with_individual_for_payment_plan(address=addresses[0])
    create_household_with_individual_for_payment_plan(address=addresses[1])
    create_household_with_individual_for_payment_plan(address=addresses[2])
    program = ProgramFactory(
        name=f"PaymentPlanProgram-{seed}", status=Program.ACTIVE, start_date="2022-12-12", end_date="2042-12-12"
    )

    targeting_criteria = TargetingCriteria.objects.create()
    TargetingCriteriaRuleFilter.objects.create(
        targeting_criteria_rule=TargetingCriteriaRule.objects.create(
            targeting_criteria=targeting_criteria,
        ),
        comparison_method="EQUALS",
        field_name="address",
        arguments=[addresses[0]],
    )
    TargetingCriteriaRuleFilter.objects.create(
        targeting_criteria_rule=TargetingCriteriaRule.objects.create(
            targeting_criteria=targeting_criteria,
        ),
        comparison_method="EQUALS",
        field_name="address",
        arguments=[addresses[1]],
    )
    TargetingCriteriaRuleFilter.objects.create(
        targeting_criteria_rule=TargetingCriteriaRule.objects.create(
            targeting_criteria=targeting_criteria,
        ),
        comparison_method="EQUALS",
        field_name="address",
        arguments=[addresses[2]],
    )

    target_population = TargetPopulation.objects.create(
        name=f"PaymentPlanTargetPopulation-{seed}",
        targeting_criteria=targeting_criteria,
        status=TargetPopulation.STATUS_OPEN,
        business_area=afghanistan,
        program=program,
        created_by=root,
    )
    full_rebuild(target_population)
    target_population.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
    target_population.save()

    rule = RuleFactory(name=f"Rule-{seed}", type=Rule.TYPE_PAYMENT_PLAN)
    RuleCommitFactory(definition="result.value=Decimal('500')", rule=rule)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "scenario",
            action="store",
            choices=["targeting", "payment_plan"],
        )

        parser.add_argument(
            "--seed",
            default=int(timezone.now().timestamp() * 100),
            action="store",
            nargs="?",
            type=int,
        )

    def handle(self, *args: Any, **options: Any) -> None:
        print("Initializing scenario with options:", {k: v for k, v in options.items() if k in ["scenario", "seed"]})
        {"targeting": init_targeting, "payment_plan": init_payment_plan}[options["scenario"]](options["seed"])
