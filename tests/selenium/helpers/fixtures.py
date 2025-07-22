from datetime import datetime

from dateutil.relativedelta import relativedelta
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory

from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program, ProgramCycle


def get_program_with_dct_type_and_name(
    name: str, programme_code: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan")
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        cycle__status=ProgramCycle.FINISHED,
        cycle__start_date=(datetime.now() - relativedelta(days=25)).date(),
        cycle__end_date=(datetime.now() + relativedelta(days=10)).date(),
        beneficiary_group=beneficiary_group,
    )
    return program
