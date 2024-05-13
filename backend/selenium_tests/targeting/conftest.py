from datetime import datetime

from django.conf import settings
from django.core.management import call_command
from django.db import transaction

import pytest
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import HEARING, HOST, REFUGEE, SEEING, Household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def sw_program() -> Program:
    return get_program_with_dct_type_and_name(
        "SW Program", dct_type=DataCollectingType.Type.SOCIAL, status=Program.ACTIVE
    )


@pytest.fixture
def non_sw_program() -> Program:
    return get_program_with_dct_type_and_name(
        "Non SW Program", dct_type=DataCollectingType.Type.STANDARD, status=Program.ACTIVE
    )


@pytest.fixture
def household_with_disability() -> Household:
    program = Program.objects.first()
    with transaction.atomic():
        household, individuals = create_household_and_individuals(
            household_data={"business_area": program.business_area, "program": program, "residence_status": HOST},
            individuals_data=[
                {"business_area": program.business_area, "observed_disability": [SEEING, HEARING]},
            ],
        )
        return household


@pytest.fixture
def household_without_disabilities() -> Household:
    program = Program.objects.first()
    with transaction.atomic():
        household, individuals = create_household_and_individuals(
            household_data={"business_area": program.business_area, "program": program, "residence_status": HOST},
            individuals_data=[
                {"business_area": program.business_area, "observed_disability": []},
            ],
        )
        return household


@pytest.fixture
def household_refugee() -> Household:
    program = Program.objects.first()
    with transaction.atomic():
        household, individuals = create_household_and_individuals(
            household_data={"business_area": program.business_area, "program": program, "residence_status": REFUGEE},
            individuals_data=[
                {"business_area": program.business_area, "observed_disability": []},
            ],
        )
        return household


def get_program_with_dct_type_and_name(
    name: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.fixture
def add_targeting() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/documenttype.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/targeting/fixtures/data-cypress.json")
