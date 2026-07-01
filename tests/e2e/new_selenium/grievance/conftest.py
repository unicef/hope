from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, Household, Program


@pytest.fixture
def social_worker_program(business_area: BusinessArea) -> Program:
    beneficiary_group, _ = BeneficiaryGroup.objects.get_or_create(name="People")
    return ProgramFactory(
        name="Social Program",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingType.objects.filter(type=DataCollectingType.Type.SOCIAL).first(),
        beneficiary_group=beneficiary_group,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )


@pytest.fixture
def household_update_program(business_area: BusinessArea) -> Program:
    beneficiary_group, _ = BeneficiaryGroup.objects.get_or_create(
        name="Household Group",
        defaults={
            "group_label": "Household",
            "group_label_plural": "Households",
            "member_label": "Individual",
            "member_label_plural": "Individuals",
            "master_detail": True,
        },
    )
    return ProgramFactory(
        name="HH Update Program",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
    )


@pytest.fixture
def household_for_update(business_area: BusinessArea, household_update_program: Program) -> Household:
    return HouseholdFactory(business_area=business_area, program=household_update_program)
