import os
from argparse import ArgumentParser
from datetime import timedelta
from typing import Any, Tuple

from django.core.management import BaseCommand, execute_from_command_line
from django.utils import timezone

from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from extras.test_utils.factories.steficon import RuleCommitFactory, RuleFactory
from faker import Faker

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.models import (
    MALE,
    ROLE_PRIMARY,
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.targeting.models import (
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
)
from hct_mis_api.apps.utils.models import MergeStatusModel

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
        household_collection=HouseholdCollection.objects.create(),
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    hh.head_of_household = Individual.objects.create(
        birth_date=now - delta_20_years,
        first_registration_date=now,
        last_registration_date=now,
        business_area=afghanistan,
        sex=MALE,
        registration_data_import=rdi,
        full_name=faker.name(),
        individual_collection=IndividualCollection.objects.create(),
        rdi_merge_status=MergeStatusModel.MERGED,
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
        rdi_merge_status=MergeStatusModel.MERGED,
    )


def init_targeting(seed: str) -> None:
    create_household_with_individual(address=f"TargetingVille-{seed}")
    ProgramFactory(
        name=f"TargetingProgram-{seed}",
        status=Program.ACTIVE,
        data_collecting_type=DataCollectingType.objects.get(id=2),
    )


def init_clear(seed: str) -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hct_mis_api.config.settings")
    execute_from_command_line(["init-e2e-scenario.py", "initcypress", "--skip-drop"])


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
    payment_plan = PaymentPlan.objects.create(
        name=f"PaymentPlanTargetPopulation-{seed}",
        status=PaymentPlan.Status.TP_OPEN,
        business_area=afghanistan,
        program_cycle=program.cycles.first(),
        created_by=root,
    )

    TargetingCriteriaRuleFilter.objects.create(
        targeting_criteria_rule=TargetingCriteriaRule.objects.create(
            payment_plan=payment_plan,
        ),
        comparison_method="EQUALS",
        field_name="address",
        arguments=[addresses[0]],
    )
    TargetingCriteriaRuleFilter.objects.create(
        targeting_criteria_rule=TargetingCriteriaRule.objects.create(
            payment_plan=payment_plan,
        ),
        comparison_method="EQUALS",
        field_name="address",
        arguments=[addresses[1]],
    )
    TargetingCriteriaRuleFilter.objects.create(
        targeting_criteria_rule=TargetingCriteriaRule.objects.create(
            payment_plan=payment_plan,
        ),
        comparison_method="EQUALS",
        field_name="address",
        arguments=[addresses[2]],
    )

    rule = RuleFactory(name=f"Rule-{seed}", type=Rule.TYPE_PAYMENT_PLAN)
    RuleCommitFactory(definition="result.value=Decimal('500')", rule=rule)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "scenario",
            action="store",
            choices=["targeting", "payment_plan", "init_clear"],
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
        {"targeting": init_targeting, "payment_plan": init_payment_plan, "init_clear": init_clear}[options["scenario"]](
            options["seed"]
        )
