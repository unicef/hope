from unittest.mock import Mock, patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.household.forms import CreateTargetPopulationTextForm
from hope.apps.targeting.celery_tasks import create_tp_from_list
from hope.models import PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def form_data(program_cycle):
    return {
        "action": "create",
        "name": "Test TP",
        "target_field": "unicef_id",
        "separator": ",",
        "criteria": "123,333",
        "program_cycle": program_cycle.pk,
    }


@pytest.fixture
def valid_form(program_cycle):
    form = Mock(spec=CreateTargetPopulationTextForm)
    form.is_valid.return_value = True
    form.cleaned_data = {
        "name": "Test TP",
        "target_field": "unicef_id",
        "separator": ",",
        "criteria": ["123,333"],
        "program_cycle": program_cycle,
    }
    return form


@patch("hope.apps.household.forms.CreateTargetPopulationTextForm")
@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.create_payments")
def test_create_tp_from_list_creates_payment_plan_and_triggers_payments(
    mock_create_payments,
    mock_form_class,
    form_data,
    valid_form,
    user,
    program,
):
    mock_form_class.return_value = valid_form

    create_tp_from_list(
        form_data,
        str(user.pk),
        str(program.pk),
    )

    payment_plan = PaymentPlan.objects.get(name="Test TP")

    mock_create_payments.assert_called_once_with(payment_plan)
    assert payment_plan.business_area == program.business_area
    assert payment_plan.program_cycle == valid_form.cleaned_data["program_cycle"]
    assert payment_plan.created_by == user
    assert payment_plan.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK
