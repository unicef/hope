from datetime import datetime
from typing import Optional

from django.utils import timezone

import pytest
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.payment.fixtures import ApprovalProcessFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory
from tests.selenium.page_object.managerial_console.managerial_console import (
    ManagerialConsole,
)

pytestmark = pytest.mark.django_db()


@pytest.fixture
def create_active_test_program() -> Program:
    return create_program("Test Programm", partner=Partner.objects.filter(name="UNHCR").first())


@pytest.fixture
def second_test_program() -> Program:
    return create_program("Do not test it")


def create_program(
    name: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.ACTIVE,
    partner: Optional[Partner] = None,
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    program = ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )
    if partner:
        program.partners.add(partner.id)
    return program


@pytest.fixture
def create_payment_plan(create_active_test_program: Program, second_test_program: Program) -> PaymentPlan:
    program_cycle_second = ProgramCycleFactory(program=second_test_program)
    ba = BusinessArea.objects.get(slug="afghanistan")
    PaymentPlanFactory(
        program_cycle=program_cycle_second,
        status=PaymentPlan.Status.IN_APPROVAL,
        business_area=ba,
    )

    payment_plan = PaymentPlan.objects.update_or_create(
        name="Test Payment Plan",
        business_area=ba,
        targeting_criteria=TargetingCriteriaFactory(),
        currency="USD",
        dispersion_start_date=datetime.now(),
        dispersion_end_date=datetime.now() + relativedelta(days=14),
        status_date=datetime.now(),
        status=PaymentPlan.Status.IN_APPROVAL,
        created_by=User.objects.first(),
        program_cycle=create_active_test_program.cycles.first(),
        total_delivered_quantity=999,
        total_entitled_quantity=2999,
        is_follow_up=False,
    )[0]
    approval_user = UserFactory()
    approval_date = timezone.datetime(2000, 10, 10, tzinfo=timezone.utc)
    ApprovalProcessFactory(
        payment_plan=payment_plan,
        sent_for_approval_date=approval_date,
        sent_for_approval_by=approval_user,
    )
    return payment_plan


@pytest.mark.usefixtures("login")
class TestSmokeManagerialConsole:
    @pytest.mark.xfail(reason="UNSTABLE")
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
        program_cycle = program.cycles.first()
        ba = BusinessArea.objects.filter(slug="afghanistan").first()
        user = User.objects.first()
        PaymentPlanFactory(
            program_cycle=program_cycle,
            status=PaymentPlan.Status.IN_APPROVAL,
            business_area=ba,
            created_by=user,
        )
        PaymentPlanFactory(
            program_cycle=program_cycle,
            status=PaymentPlan.Status.IN_AUTHORIZATION,
            business_area=ba,
            created_by=user,
        )
        PaymentPlanFactory(
            program_cycle=program_cycle,
            status=PaymentPlan.Status.IN_REVIEW,
            business_area=ba,
            created_by=user,
        )
        PaymentPlanFactory(
            program_cycle=program_cycle,
            status=PaymentPlan.Status.ACCEPTED,
            business_area=ba,
            created_by=user,
        )
        pageManagerialConsole.getMenuUserProfile().click()
        pageManagerialConsole.getMenuItemClearCache().click()

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

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_managerial_console_happy_path(
        self, pageManagerialConsole: ManagerialConsole, create_payment_plan: PaymentPlan
    ) -> None:
        pageManagerialConsole.getNavManagerialConsole().click()
        # Approve Payment Plan
        pageManagerialConsole.getProgramSelectApproval().click()
        pageManagerialConsole.select_listbox_element("Test Programm")

        pageManagerialConsole.getColumnField()
        pageManagerialConsole.getSelectApproval().click()
        pageManagerialConsole.getApproveButton().click()
        pageManagerialConsole.getCommentApprove().find_elements(By.TAG_NAME, "textarea")[0].send_keys("Test Test 123")
        pageManagerialConsole.getButtonSave().click()
        # Authorize Payment Plan
        pageManagerialConsole.getProgramSelectAuthorization().click()
        pageManagerialConsole.select_listbox_element("Test Programm")
        pageManagerialConsole.getColumnFieldAuthorization()
        pageManagerialConsole.getSelectAllAuthorization().click()
        pageManagerialConsole.getAuthorizeButton().click()
        pageManagerialConsole.getButtonSave().click()
        # Release Payment Plan
        pageManagerialConsole.getColumnFieldRelease()
        pageManagerialConsole.getSelectAllRelease().click()
        pageManagerialConsole.getReleaseButton().click()
        pageManagerialConsole.getButtonSave().click()
        # Check Released Payment Plans
        assert create_payment_plan.unicef_id in pageManagerialConsole.getColumnFieldReleased().text
