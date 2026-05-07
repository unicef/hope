from datetime import datetime

from dateutil.relativedelta import relativedelta

from extras.test_utils.factories import DataCollectingTypeFactory, ProgramCycleFactory, ProgramFactory
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, Program, ProgramCycle


def get_program_with_dct_type_and_name(
    name: str,
    code: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.ACTIVE,
) -> Program:
    ba = BusinessArea.objects.get(slug="afghanistan")
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()

    program = ProgramFactory(
        name=name,
        code=code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
        business_area=ba,
    )
    ProgramCycleFactory(
        program=program,
        status=ProgramCycle.FINISHED,
        start_date=(datetime.now() - relativedelta(days=25)).date(),
        end_date=(datetime.now() + relativedelta(days=10)).date(),
    )

    return program
