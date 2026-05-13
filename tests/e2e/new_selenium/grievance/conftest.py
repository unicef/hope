from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, Program


@pytest.fixture
def social_worker_program(business_area: BusinessArea) -> Program:
    beneficiary_group, _ = BeneficiaryGroup.objects.get_or_create(name="People")
    program = ProgramFactory(
        name="Social Program",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingType.objects.filter(type=DataCollectingType.Type.SOCIAL).first(),
        beneficiary_group=beneficiary_group,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )
    ProgramCycleFactory(program=program)
    return program
