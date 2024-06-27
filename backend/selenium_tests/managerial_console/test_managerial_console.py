from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from page_object.managerial_console.managerial_console import ManagerialConsole

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_active_test_program() -> Program:
    return create_program("Test Programm")


def create_program(
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


@pytest.mark.usefixtures("login")
class TestSmokeManagerialConsole:
    def test_managerial_console_smoke_test(
        self, pageManagerialConsole: ManagerialConsole, create_active_test_program: Program
    ) -> None:
        pageManagerialConsole.getNavManagerialConsole().click()
        pageManagerialConsole.getSelectAllApproval()
        with pytest.raises(Exception):
            pageManagerialConsole.getApproveButton().click()

        pageManagerialConsole.getSelectAllAuthorization()
        with pytest.raises(Exception):
            pageManagerialConsole.getAuthorizeButton().click()

        pageManagerialConsole.getSelectAllRelease()
        with pytest.raises(Exception):
            pageManagerialConsole.getReleaseButton().click()

        program = Program.objects.filter(name="Test Programm").first()
        PaymentPlanFactory(
            program=program,
            status=PaymentPlan.Status.IN_APPROVAL,
            business_area=BusinessArea.objects.filter(slug="afghanistan").first(),
        )
        PaymentPlanFactory(
            program=program,
            status=PaymentPlan.Status.IN_AUTHORIZATION,
            business_area=BusinessArea.objects.filter(slug="afghanistan").first(),
        )
        PaymentPlanFactory(
            program=program,
            status=PaymentPlan.Status.IN_REVIEW,
            business_area=BusinessArea.objects.filter(slug="afghanistan").first(),
        )
        PaymentPlanFactory(
            program=program,
            status=PaymentPlan.Status.ACCEPTED,
            business_area=BusinessArea.objects.filter(slug="afghanistan").first(),
        )
        pageManagerialConsole.driver.refresh()

        pageManagerialConsole.getSelectAllApproval()
        pageManagerialConsole.getProgramSelectApproval()
        with pytest.raises(Exception):
            pageManagerialConsole.getApproveButton().click()

        pageManagerialConsole.getSelectAllAuthorization()
        pageManagerialConsole.getProgramSelectAuthorization()
        with pytest.raises(Exception):
            pageManagerialConsole.getAuthorizeButton().click()

        pageManagerialConsole.getSelectAllRelease()
        pageManagerialConsole.getProgramSelectRelease()
        with pytest.raises(Exception):
            pageManagerialConsole.getReleaseButton().click()

        pageManagerialConsole.getSelectApproval().click()
        pageManagerialConsole.getApproveButton().click()
        pageManagerialConsole.getPlansIds()
        pageManagerialConsole.getButtonSave()
        pageManagerialConsole.getCommentApprove()
        pageManagerialConsole.getButtonCancel().click()
        pageManagerialConsole.getProgramSelectAuthorization()
        pageManagerialConsole.getSelectAllAuthorization().click()
        pageManagerialConsole.getAuthorizeButton().click()
        pageManagerialConsole.getButtonCancel().click()
        pageManagerialConsole.getProgramSelectRelease()
        pageManagerialConsole.getSelectAllRelease().click()
        pageManagerialConsole.getReleaseButton().click()
        pageManagerialConsole.getButtonCancel().click()

    def test_managerial_console_happy_path(
        self, pageManagerialConsole: ManagerialConsole, create_active_test_program: Program
    ) -> None:
        pageManagerialConsole.getNavManagerialConsole().click()