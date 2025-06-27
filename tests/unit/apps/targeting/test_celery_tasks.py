from unittest.mock import Mock, patch

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.forms import CreateTargetPopulationTextForm
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.targeting.celery_tasks import create_tp_from_list
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory


class CreateTPFromListTaskTest(TestCase):
    def setUp(self) -> None:
        create_afghanistan()
        self.user = UserFactory()
        self.program = ProgramFactory()
        self.program_cycle = ProgramCycleFactory(program=self.program)
        self.targeting_criteria = TargetingCriteriaFactory()
        self.form_data = {
            "action": "create",
            "name": "Test TP",
            "target_field": "unicef_id",
            "targeting_criteria": self.targeting_criteria.pk,
            "separator": ",",
            "criteria": "123,333",
            "program_cycle": self.program_cycle.pk,
        }

    @patch("hct_mis_api.apps.household.forms.CreateTargetPopulationTextForm")
    @patch("hct_mis_api.apps.payment.services.payment_plan_services.PaymentPlanService.create_payments")
    def test_create_tp_from_list_success(self, mock_create_payments: Mock, mock_form_class: Mock) -> None:
        mock_form = Mock(spec=CreateTargetPopulationTextForm)
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {
            "name": "Test TP",
            "target_field": "unicef_id",
            "targeting_criteria": self.targeting_criteria,
            "separator": ",",
            "criteria": ["123,333"],
            "program_cycle": self.program_cycle,
        }
        mock_form_class.return_value = mock_form

        create_tp_from_list(self.form_data, str(self.user.pk), str(self.program.pk))

        payment_plan = PaymentPlan.objects.get(name="Test TP")

        mock_create_payments.assert_called_once_with(payment_plan)
        self.assertEqual(payment_plan.targeting_criteria, self.targeting_criteria)
        self.assertEqual(payment_plan.business_area, self.program.business_area)
        self.assertEqual(payment_plan.program_cycle, self.program_cycle)
        self.assertEqual(payment_plan.created_by, self.user)
        self.assertEqual(payment_plan.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_OK)
