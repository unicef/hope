from datetime import datetime
from typing import Optional

import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from e2e.page_object.managerial_console.managerial_console import ManagerialConsole
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.payment import (
    ApprovalProcessFactory,
    PaymentPlanFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from hope.apps.account.models import Partner, User
from hope.apps.core.models import BusinessArea, DataCollectingType
from hope.apps.payment.models import PaymentPlan
from hope.apps.program.models import BeneficiaryGroup, Program

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
        self,
        page_managerial_console: ManagerialConsole,
        create_active_test_program: Program,
    ) -> None:
        page_managerial_console.get_nav_managerial_console().click()
        page_managerial_console.get_select_all_approval()
        with pytest.raises(NoSuchElementException):
            page_managerial_console.get_approve_button().click()

        page_managerial_console.get_select_all_authorization()
        with pytest.raises(NoSuchElementException):
            page_managerial_console.get_authorize_button().click()

        page_managerial_console.get_select_all_release()
        with pytest.raises(NoSuchElementException):
            page_managerial_console.get_release_button().click()

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
        page_managerial_console.get_menu_user_profile().click()
        page_managerial_console.get_menu_item_clear_cache().click()

        page_managerial_console.get_select_all_approval()
        page_managerial_console.get_program_select_approval()

        with pytest.raises(NoSuchElementException):
            page_managerial_console.get_approve_button().click()

        page_managerial_console.get_select_all_authorization()
        page_managerial_console.get_program_select_authorization()
        with pytest.raises(NoSuchElementException):
            page_managerial_console.get_authorize_button().click()

        page_managerial_console.get_select_all_release()
        page_managerial_console.get_program_select_release()
        with pytest.raises(NoSuchElementException):
            page_managerial_console.get_release_button().click()

        page_managerial_console.get_select_approval().click()
        page_managerial_console.get_approve_button().click()
        page_managerial_console.get_plans_ids()
        page_managerial_console.get_button_save()
        page_managerial_console.get_comment_approve()
        page_managerial_console.get_button_cancel().click()
        page_managerial_console.get_program_select_authorization()
        page_managerial_console.get_select_all_authorization().click()
        page_managerial_console.get_authorize_button().click()
        page_managerial_console.get_button_cancel().click()
        page_managerial_console.get_program_select_release()
        page_managerial_console.get_select_all_release().click()
        page_managerial_console.get_release_button().click()
        page_managerial_console.get_button_cancel().click()

    @pytest.mark.xfail(reason="UNSTABLE")
    def test_managerial_console_happy_path(
        self,
        page_managerial_console: ManagerialConsole,
        create_payment_plan: PaymentPlan,
    ) -> None:
        page_managerial_console.get_nav_managerial_console().click()
        # Approve Payment Plan
        page_managerial_console.get_program_select_approval().click()
        page_managerial_console.select_listbox_element("Test Programm")

        page_managerial_console.get_column_field()
        page_managerial_console.get_select_approval().click()
        page_managerial_console.get_approve_button().click()
        page_managerial_console.get_comment_approve().find_elements(By.TAG_NAME, "textarea")[0].send_keys(
            "Test Test 123"
        )
        page_managerial_console.get_button_save().click()
        # Authorize Payment Plan
        page_managerial_console.get_program_select_authorization().click()
        page_managerial_console.select_listbox_element("Test Programm")
        page_managerial_console.get_column_field_authorization()
        page_managerial_console.get_select_all_authorization().click()
        page_managerial_console.get_authorize_button().click()
        page_managerial_console.get_button_save().click()
        # Release Payment Plan
        page_managerial_console.get_column_field_release()
        page_managerial_console.get_select_all_release().click()
        page_managerial_console.get_release_button().click()
        page_managerial_console.get_button_save().click()
        # Check Released Payment Plans
        assert create_payment_plan.unicef_id in page_managerial_console.get_column_field_released().text
