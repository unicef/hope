from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, Program


@pytest.fixture
def social_worker_program(business_area: BusinessArea) -> Program:
    beneficiary_group, _ = BeneficiaryGroup.objects.get_or_create(name="People")
    return ProgramFactory(
        name="Social Program",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL),
        beneficiary_group=beneficiary_group,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )
