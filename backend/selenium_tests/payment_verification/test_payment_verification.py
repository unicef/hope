from datetime import datetime
import pytest

from page_object.payment_verification.payment_verification import PaymentVerification
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def active_program() -> Program:
    return get_program_with_dct_type_and_name("Active Program", "ACTI", status=Program.ACTIVE)


def get_program_with_dct_type_and_name(
        name: str, programme_code: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


@pytest.mark.usefixtures("login")
class TestSmokePaymentVerification:
    def test_smoke_payment_verification(self, active_program: Program, pagePaymentVerification: PaymentVerification) -> None:
        pagePaymentVerification.selectGlobalProgramFilter("Active Program").click()
        pagePaymentVerification.getNavPaymentVerification().click()
        pagePaymentVerification.screenshot("payment_verification")
        from selenium_tests.tools.tag_name_finder import printing
        printing("Mapping", pagePaymentVerification.driver)
        printing("Methods", pagePaymentVerification.driver)
        printing("Assert", pagePaymentVerification.driver)
