from django.utils import timezone

import pytest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.payment.fixtures import (
    ApprovalFactory,
    ApprovalProcessFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import Approval, PaymentPlan

pytestmark = pytest.mark.django_db


class TestPaymentPlanModel:
    def test_get_last_approval_process_data_in_approval(self, afghanistan):
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=PaymentPlan.Status.IN_APPROVAL)
        approval_user = UserFactory()
        approval_date = timezone.datetime(2000, 10, 10, tzinfo=timezone.utc)
        ApprovalProcessFactory(
            payment_plan=payment_plan,
            sent_for_approval_date=approval_date,
            sent_for_approval_by=approval_user,
        )
        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == approval_date
        assert modified_data.modified_by == approval_user

    def test_get_last_approval_process_data_in_authorization(self, afghanistan):
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=PaymentPlan.Status.IN_AUTHORIZATION)
        approval_user = UserFactory()
        approval_process = ApprovalProcessFactory(
            payment_plan=payment_plan,
        )
        ApprovalFactory(type=Approval.APPROVAL, approval_process=approval_process)
        approval_approval2 = ApprovalFactory(
            type=Approval.APPROVAL, approval_process=approval_process, created_by=approval_user
        )
        ApprovalFactory(type=Approval.AUTHORIZATION, approval_process=approval_process)
        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == approval_approval2.created_at
        assert modified_data.modified_by == approval_user

    def test_get_last_approval_process_data_in_review(self, afghanistan):
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=PaymentPlan.Status.IN_REVIEW)
        approval_user = UserFactory()
        approval_process = ApprovalProcessFactory(
            payment_plan=payment_plan,
        )
        ApprovalFactory(type=Approval.AUTHORIZATION, approval_process=approval_process)
        approval_authorization2 = ApprovalFactory(
            type=Approval.AUTHORIZATION, approval_process=approval_process, created_by=approval_user
        )
        ApprovalFactory(type=Approval.APPROVAL, approval_process=approval_process)
        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == approval_authorization2.created_at
        assert modified_data.modified_by == approval_user

    def test_get_last_approval_process_data_no_approval_process(self, afghanistan):
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=PaymentPlan.Status.IN_REVIEW)

        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == payment_plan.updated_at
        assert modified_data.modified_by is None

    @pytest.mark.parametrize(
        "status",
        [
            PaymentPlan.Status.FINISHED,
            PaymentPlan.Status.ACCEPTED,
            PaymentPlan.Status.PREPARING,
            PaymentPlan.Status.OPEN,
            PaymentPlan.Status.LOCKED,
            PaymentPlan.Status.LOCKED_FSP,
        ],
    )
    def test_get_last_approval_process_data_other_status(self, afghanistan, status):
        payment_plan = PaymentPlanFactory(business_area=afghanistan, status=status)
        approval_user = UserFactory()
        approval_date = timezone.datetime(2000, 10, 10, tzinfo=timezone.utc)
        ApprovalProcessFactory(
            payment_plan=payment_plan,
            sent_for_approval_date=approval_date,
            sent_for_approval_by=approval_user,
        )
        modified_data = payment_plan._get_last_approval_process_data()
        assert modified_data.modified_date == payment_plan.updated_at
        assert modified_data.modified_by is None
